"""
Billing & Stripe webhook routes for SampleMind v3.0 (Step 25).

Endpoints:
  POST /billing/create-checkout   — Create a Stripe Checkout session
  POST /billing/webhook           — Handle Stripe webhook events
  GET  /billing/plans             — List available plans and pricing
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from samplemind.core.services.stripe import TIER_LIMITS, StripeService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])

_stripe = StripeService()


# ── Schemas ───────────────────────────────────────────────────────────────────


class CheckoutRequest(BaseModel):
    user_id: str
    email: str
    plan: str  # "pro" or "team"
    success_url: str
    cancel_url: str
    name: str | None = None


# ── Routes ────────────────────────────────────────────────────────────────────


@router.get("/plans")
async def list_plans() -> JSONResponse:
    """Return all available plans with pricing and feature limits."""
    return JSONResponse(
        {
            "plans": [
                {
                    "name": tier,
                    "price_monthly_usd": limits["price_monthly_usd"],
                    "analyses_per_day": (
                        limits["analyses_per_day"]
                        if limits["analyses_per_day"] != -1
                        else "unlimited"
                    ),
                    "storage_gb": limits["storage_gb"],
                    "ai_coaching": limits["ai_coaching"],
                    "priority_queue": limits["priority_queue"],
                }
                for tier, limits in TIER_LIMITS.items()
            ]
        }
    )


@router.post("/create-checkout")
async def create_checkout(body: CheckoutRequest) -> JSONResponse:
    """
    Create a Stripe Checkout Session and return the redirect URL.

    The client should redirect the user to the returned `url`.
    """
    if body.plan not in ("pro", "team"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan '{body.plan}'. Choose 'pro' or 'team'.",
        )

    session = await _stripe.create_checkout_session(
        user_id=body.user_id,
        email=body.email,
        plan=body.plan,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        name=body.name or "",
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing service unavailable. Please try again later.",
        )

    return JSONResponse({"session_id": session.session_id, "url": session.url})


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> JSONResponse:
    """
    Stripe webhook handler.

    Verifies the event signature and dispatches subscription updates
    in the background to avoid blocking Stripe's delivery timeout.
    """
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    event = _stripe.handle_webhook(payload, signature)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook verification failed",
        )

    update = _stripe.extract_subscription_update(event)
    if update:
        background_tasks.add_task(_apply_subscription_update, update)

    # Marketplace pack purchase fulfillment
    event_type = (
        event.get("type") if isinstance(event, dict) else getattr(event, "type", None)
    )
    if event_type == "checkout.session.completed":
        session_data = (
            event.get("data", {}).get("object", {})
            if isinstance(event, dict)
            else getattr(getattr(event, "data", None), "object", {})
        )
        meta = (
            session_data.get("metadata", {}) if isinstance(session_data, dict) else {}
        )
        if meta.get("platform") == "samplemind_marketplace":
            background_tasks.add_task(
                _fulfill_marketplace_purchase,
                session_id=session_data.get("id", ""),
                buyer_user_id=meta.get("buyer_user_id", ""),
                listing_id=meta.get("listing_id", ""),
            )

    return JSONResponse({"received": True})


# ── Background task ───────────────────────────────────────────────────────────


async def _fulfill_marketplace_purchase(
    session_id: str,
    buyer_user_id: str,
    listing_id: str,
) -> None:
    """Generate a signed R2 download URL and record the pack purchase."""
    if not listing_id or not buyer_user_id:
        return
    try:
        from samplemind.interfaces.api.routes.marketplace import fulfill_pack_purchase

        url = await fulfill_pack_purchase(session_id, buyer_user_id, listing_id)
        if url:
            logger.info(
                "Pack download URL generated for user=%s listing=%s",
                buyer_user_id,
                listing_id,
            )
        else:
            logger.warning(
                "No R2 URL generated for listing=%s (R2 may not be configured)",
                listing_id,
            )
    except Exception as exc:
        logger.error(
            "Marketplace fulfillment failed for session=%s: %s", session_id, exc
        )


async def _apply_subscription_update(update: dict) -> None:
    """
    Persist the plan change in the database.

    Called in the background so the webhook response is returned
    to Stripe within their 30-second timeout.
    """
    user_id = update.get("user_id", "")
    new_plan = update.get("plan", "free")

    if not user_id:
        logger.warning("Subscription update missing user_id: %s", update)
        return

    try:
        from samplemind.core.database.repositories.users import UserRepository

        repo = UserRepository()
        await repo.update_tier(user_id=user_id, tier=new_plan)
        logger.info("Subscription updated: user=%s tier=%s", user_id, new_plan)
    except Exception as exc:
        logger.error(
            "Failed to persist subscription update for user=%s: %s", user_id, exc
        )
