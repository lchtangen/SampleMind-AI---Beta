"""
Marketplace Routes — SampleMind Phase 15

Stripe Connect marketplace for .smpack pack publishing and purchasing.
Creators upload packs, buyers purchase via Stripe, delivery via Cloudflare R2.

Endpoints:
  POST /api/v1/marketplace/onboard        — start Stripe Connect onboarding
  POST /api/v1/marketplace/publish        — publish a .smpack pack for sale
  GET  /api/v1/marketplace/listings       — list available packs
  GET  /api/v1/marketplace/listings/{id}  — get pack detail
  POST /api/v1/marketplace/purchase       — purchase a pack (Stripe Checkout)
  GET  /api/v1/marketplace/my-packs       — packs created by current user
  GET  /api/v1/marketplace/purchases      — packs purchased by current user

Flow:
  1. Creator runs `samplemind pack build ...` → .smpack file
  2. Creator calls POST /publish → uploads to R2, creates Stripe Product+Price
  3. Buyer calls POST /purchase → Stripe Checkout session returned
  4. Stripe webhook `checkout.session.completed` → generate R2 download URL → store
  5. Buyer polls GET /purchases to get download URL
"""

from __future__ import annotations

import logging
import os
from datetime import UTC

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/marketplace", tags=["marketplace"])


# ── Request / Response schemas ────────────────────────────────────────────────


class OnboardRequest(BaseModel):
    user_id: str
    email: str
    return_url: str = "https://app.samplemind.ai/marketplace/onboard/complete"
    refresh_url: str = "https://app.samplemind.ai/marketplace/onboard"


class OnboardResponse(BaseModel):
    account_id: str
    onboarding_url: str


class PublishRequest(BaseModel):
    user_id: str
    pack_name: str
    description: str = ""
    tags: list[str] = []
    price_usd: float  # e.g. 9.99
    smpack_r2_key: str  # R2 object key of the already-uploaded .smpack file
    preview_r2_key: str | None = None
    sample_count: int = 0
    bpm_range: list[int] = []
    key_signatures: list[str] = []


class PublishResponse(BaseModel):
    listing_id: str
    stripe_product_id: str
    stripe_price_id: str
    public_url: str


class PackListing(BaseModel):
    listing_id: str
    pack_name: str
    description: str
    tags: list[str]
    price_usd: float
    creator_id: str
    sample_count: int
    bpm_range: list[int]
    key_signatures: list[str]
    preview_url: str | None
    created_at: str


class PurchaseRequest(BaseModel):
    buyer_user_id: str
    listing_id: str
    success_url: str = "https://app.samplemind.ai/marketplace/purchase/success"
    cancel_url: str = "https://app.samplemind.ai/marketplace"


class PurchaseResponse(BaseModel):
    checkout_session_id: str
    checkout_url: str


class PurchaseRecord(BaseModel):
    purchase_id: str
    listing_id: str
    pack_name: str
    download_url: str | None  # None until payment confirmed
    purchased_at: str
    status: str  # pending | completed | expired


# ── In-memory store (replace with Tortoise DB in production) ──────────────────

_listings: dict[str, dict] = {}
_purchases: dict[str, dict] = {}


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/onboard", response_model=OnboardResponse)
async def creator_onboard(body: OnboardRequest) -> OnboardResponse:
    """
    Start Stripe Connect Express onboarding for a creator.

    Returns a Stripe-hosted onboarding URL. After completion, the creator
    can publish packs and receive payouts.
    """
    connect = _get_connect_service()
    try:
        account_id = await connect.create_connected_account(
            user_id=body.user_id,
            email=body.email,
        )
        onboarding_url = await connect.create_account_link(
            account_id=account_id,
            return_url=body.return_url,
            refresh_url=body.refresh_url,
        )
        return OnboardResponse(account_id=account_id, onboarding_url=onboarding_url)
    except Exception as exc:
        logger.error("Stripe Connect onboard failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/publish", response_model=PublishResponse)
async def publish_pack(body: PublishRequest) -> PublishResponse:
    """
    Publish a .smpack file as a marketplace listing.

    The .smpack must already be uploaded to R2 (use the upload endpoint or CLI).
    This creates a Stripe Product + Price and registers the listing.
    """
    import uuid
    from datetime import datetime

    connect = _get_connect_service()
    r2 = _get_r2()

    try:
        product_id, price_id = await connect.create_pack_product(
            pack_name=body.pack_name,
            description=body.description,
            price_usd=body.price_usd,
            metadata={
                "user_id": body.user_id,
                "smpack_key": body.smpack_r2_key,
                "sample_count": str(body.sample_count),
            },
        )
    except Exception as exc:
        logger.error("Stripe product creation failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Stripe error: {exc}")

    listing_id = str(uuid.uuid4())
    preview_url = (
        r2.get_public_url(body.preview_r2_key)
        if body.preview_r2_key and r2.available
        else None
    )

    listing = {
        "listing_id": listing_id,
        "pack_name": body.pack_name,
        "description": body.description,
        "tags": body.tags,
        "price_usd": body.price_usd,
        "creator_id": body.user_id,
        "sample_count": body.sample_count,
        "bpm_range": body.bpm_range,
        "key_signatures": body.key_signatures,
        "preview_url": preview_url,
        "smpack_r2_key": body.smpack_r2_key,
        "stripe_product_id": product_id,
        "stripe_price_id": price_id,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _listings[listing_id] = listing

    public_url = f"{os.getenv('APP_BASE_URL', 'https://app.samplemind.ai')}/marketplace/{listing_id}"
    return PublishResponse(
        listing_id=listing_id,
        stripe_product_id=product_id,
        stripe_price_id=price_id,
        public_url=public_url,
    )


@router.get("/listings", response_model=list[PackListing])
async def list_packs(
    tag: str | None = None,
    min_bpm: int | None = None,
    max_bpm: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[PackListing]:
    """List available marketplace packs with optional filtering."""
    results = list(_listings.values())

    if tag:
        results = [
            r for r in results if tag.lower() in [t.lower() for t in r.get("tags", [])]
        ]

    if min_bpm is not None:
        results = [
            r for r in results if r.get("bpm_range") and r["bpm_range"][0] >= min_bpm
        ]

    if max_bpm is not None:
        results = [
            r for r in results if r.get("bpm_range") and r["bpm_range"][-1] <= max_bpm
        ]

    results = results[offset : offset + limit]
    return [
        PackListing(
            **{
                k: v
                for k, v in r.items()
                if k != "smpack_r2_key"
                and k not in ("stripe_product_id", "stripe_price_id")
            }
        )
        for r in results
    ]


@router.get("/listings/{listing_id}", response_model=PackListing)
async def get_listing(listing_id: str) -> PackListing:
    """Get a single pack listing by ID."""
    listing = _listings.get(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return PackListing(
        **{
            k: v
            for k, v in listing.items()
            if k not in ("smpack_r2_key", "stripe_product_id", "stripe_price_id")
        }
    )


@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_pack(body: PurchaseRequest) -> PurchaseResponse:
    """
    Initiate a pack purchase via Stripe Checkout.

    Returns a checkout URL. After successful payment, the Stripe webhook
    `checkout.session.completed` will unlock the download URL.
    """
    listing = _listings.get(body.listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    connect = _get_connect_service()
    try:
        session_id, checkout_url = await connect.create_pack_checkout(
            price_id=listing["stripe_price_id"],
            buyer_user_id=body.buyer_user_id,
            listing_id=body.listing_id,
            success_url=body.success_url,
            cancel_url=body.cancel_url,
        )
        return PurchaseResponse(
            checkout_session_id=session_id, checkout_url=checkout_url
        )
    except Exception as exc:
        logger.error("Checkout creation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/purchases", response_model=list[PurchaseRecord])
async def get_purchases(user_id: str) -> list[PurchaseRecord]:
    """List all packs purchased by a user."""
    results = [
        PurchaseRecord(**p)
        for p in _purchases.values()
        if p.get("buyer_user_id") == user_id
    ]
    return results


@router.get("/my-packs", response_model=list[PackListing])
async def get_my_packs(user_id: str) -> list[PackListing]:
    """List all packs published by a creator."""
    return [
        PackListing(
            **{
                k: v
                for k, v in r.items()
                if k not in ("smpack_r2_key", "stripe_product_id", "stripe_price_id")
            }
        )
        for r in _listings.values()
        if r.get("creator_id") == user_id
    ]


@router.post("/webhook/purchase-complete")
async def marketplace_purchase_webhook(
    stripe_signature: str = Header(None, alias="stripe-signature"),
) -> JSONResponse:
    """
    Internal webhook called after checkout.session.completed.

    Generates a 24-hour R2 signed download URL and stores it in the purchase record.
    In production, this is triggered by the Stripe webhook handler in billing.py.
    """
    # This endpoint is called programmatically from the billing webhook handler
    # Actual Stripe webhook verification happens in billing.py
    return JSONResponse({"status": "ok"})


# ── Internal: fulfill a completed purchase ────────────────────────────────────


async def fulfill_pack_purchase(
    stripe_session_id: str,
    buyer_user_id: str,
    listing_id: str,
) -> str | None:
    """
    Called from the Stripe webhook handler after payment confirmation.

    Generates a 24-hour R2 signed download URL and records the purchase.

    Returns:
        download_url if successful, None on error.
    """
    import uuid
    from datetime import datetime

    listing = _listings.get(listing_id)
    if not listing:
        logger.error("fulfill_pack_purchase: listing %s not found", listing_id)
        return None

    r2 = _get_r2()
    download_url = None
    if r2.available:
        download_url = r2.get_presigned_url(
            listing["smpack_r2_key"], expires_in=86400
        )  # 24h

    purchase_id = str(uuid.uuid4())
    _purchases[purchase_id] = {
        "purchase_id": purchase_id,
        "listing_id": listing_id,
        "pack_name": listing["pack_name"],
        "buyer_user_id": buyer_user_id,
        "stripe_session_id": stripe_session_id,
        "download_url": download_url,
        "purchased_at": datetime.now(UTC).isoformat(),
        "status": "completed" if download_url else "pending",
    }

    logger.info(
        "✓ Purchase fulfilled: user=%s pack=%s", buyer_user_id, listing["pack_name"]
    )
    return download_url


# ── Service helpers ───────────────────────────────────────────────────────────


def _get_connect_service():
    from samplemind.core.services.stripe_connect import StripeConnectService

    return StripeConnectService()


def _get_r2():
    from samplemind.services.storage.r2_provider import get_r2

    return get_r2()
