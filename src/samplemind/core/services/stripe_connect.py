"""
Stripe Connect Service — SampleMind Phase 15

Handles Stripe Connect Express for the pack marketplace:
  - Creator onboarding (account creation + account links)
  - Product/Price creation per pack listing
  - Checkout session creation for buyers
  - Payout routing via application_fee_amount

Platform take rate: 20% (configurable via STRIPE_PLATFORM_FEE_PCT env var).

Configuration (env vars):
    STRIPE_SECRET_KEY          — Stripe secret key
    STRIPE_CONNECT_WEBHOOK_SECRET — Connect webhook signing secret
    STRIPE_PLATFORM_FEE_PCT    — Platform fee percentage (default: 20)

Usage::

    svc = StripeConnectService()

    # Onboard a creator
    account_id = await svc.create_connected_account(user_id, email)
    url = await svc.create_account_link(account_id, return_url, refresh_url)

    # Publish a pack
    product_id, price_id = await svc.create_pack_product(name, desc, price_usd, metadata)

    # Buyer checkout
    session_id, url = await svc.create_pack_checkout(price_id, buyer_user_id, listing_id, ...)
"""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

PLATFORM_FEE_PCT = float(os.getenv("STRIPE_PLATFORM_FEE_PCT", "20"))


class StripeConnectService:
    """Stripe Connect Express integration for the SampleMind marketplace."""

    def __init__(self) -> None:
        self._stripe_key = os.getenv("STRIPE_SECRET_KEY", "")

    def _get_stripe(self):
        if not self._stripe_key:
            raise RuntimeError(
                "STRIPE_SECRET_KEY not set — Stripe Connect unavailable"
            )
        try:
            import stripe
            stripe.api_key = self._stripe_key
            return stripe
        except ImportError:
            raise RuntimeError("stripe not installed — run: uv add stripe")

    # ── Creator onboarding ────────────────────────────────────────────────────

    async def create_connected_account(self, user_id: str, email: str) -> str:
        """
        Create a Stripe Connect Express account for a creator.

        Returns:
            Stripe Connected Account ID (acct_xxx).
        """
        import asyncio

        stripe = self._get_stripe()
        loop = asyncio.get_event_loop()

        def _create():
            account = stripe.Account.create(
                type="express",
                email=email,
                metadata={"samplemind_user_id": user_id},
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
            )
            return account.id

        account_id = await loop.run_in_executor(None, _create)
        logger.info("✓ Stripe Connect account created: %s (user: %s)", account_id, user_id)
        return account_id

    async def create_account_link(
        self,
        account_id: str,
        return_url: str,
        refresh_url: str,
    ) -> str:
        """
        Create a Stripe Account Link URL for onboarding.

        Returns:
            Hosted onboarding URL (valid for ~5 minutes).
        """
        import asyncio

        stripe = self._get_stripe()
        loop = asyncio.get_event_loop()

        def _link():
            link = stripe.AccountLink.create(
                account=account_id,
                return_url=return_url,
                refresh_url=refresh_url,
                type="account_onboarding",
            )
            return link.url

        url = await loop.run_in_executor(None, _link)
        return url

    async def get_account_status(self, account_id: str) -> dict:
        """
        Check if a connected account has completed onboarding.

        Returns:
            dict with keys: charges_enabled, payouts_enabled, details_submitted
        """
        import asyncio

        stripe = self._get_stripe()
        loop = asyncio.get_event_loop()

        def _get():
            acct = stripe.Account.retrieve(account_id)
            return {
                "charges_enabled": acct.charges_enabled,
                "payouts_enabled": acct.payouts_enabled,
                "details_submitted": acct.details_submitted,
            }

        return await loop.run_in_executor(None, _get)

    # ── Pack product management ───────────────────────────────────────────────

    async def create_pack_product(
        self,
        pack_name: str,
        description: str,
        price_usd: float,
        metadata: Optional[dict] = None,
    ) -> tuple[str, str]:
        """
        Create a Stripe Product + one-time Price for a pack listing.

        Returns:
            (product_id, price_id)
        """
        import asyncio

        stripe = self._get_stripe()
        loop = asyncio.get_event_loop()
        price_cents = int(price_usd * 100)

        def _create():
            product = stripe.Product.create(
                name=pack_name,
                description=description or f"SampleMind pack: {pack_name}",
                metadata=metadata or {},
            )
            price = stripe.Price.create(
                product=product.id,
                unit_amount=price_cents,
                currency="usd",
            )
            return product.id, price.id

        product_id, price_id = await loop.run_in_executor(None, _create)
        logger.info("✓ Stripe product created: %s / price: %s", product_id, price_id)
        return product_id, price_id

    async def archive_pack_product(self, product_id: str) -> bool:
        """Archive (delist) a pack product from Stripe."""
        import asyncio

        stripe = self._get_stripe()
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: stripe.Product.modify(product_id, active=False),
            )
            return True
        except Exception as exc:
            logger.error("Failed to archive product %s: %s", product_id, exc)
            return False

    # ── Buyer checkout ────────────────────────────────────────────────────────

    async def create_pack_checkout(
        self,
        price_id: str,
        buyer_user_id: str,
        listing_id: str,
        success_url: str,
        cancel_url: str,
        connected_account_id: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Create a Stripe Checkout Session for buying a pack.

        Uses `payment_intent_data.application_fee_amount` to collect
        the platform's share when a connected account is specified.

        Returns:
            (session_id, checkout_url)
        """
        import asyncio

        stripe = self._get_stripe()
        loop = asyncio.get_event_loop()

        def _create():
            params: dict = {
                "mode": "payment",
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": success_url + "?session_id={CHECKOUT_SESSION_ID}",
                "cancel_url": cancel_url,
                "metadata": {
                    "buyer_user_id": buyer_user_id,
                    "listing_id": listing_id,
                    "platform": "samplemind_marketplace",
                },
            }

            # Route payment to connected account with platform fee
            if connected_account_id:
                # Retrieve price to calculate fee
                price_obj = stripe.Price.retrieve(price_id)
                amount = price_obj.unit_amount or 0
                fee = int(amount * PLATFORM_FEE_PCT / 100)
                params["payment_intent_data"] = {
                    "application_fee_amount": fee,
                    "transfer_data": {"destination": connected_account_id},
                }

            session = stripe.checkout.Session.create(**params)
            return session.id, session.url

        session_id, url = await loop.run_in_executor(None, _create)
        logger.info(
            "✓ Checkout session created: %s (buyer: %s, listing: %s)",
            session_id, buyer_user_id, listing_id,
        )
        return session_id, url

    # ── Payout info ───────────────────────────────────────────────────────────

    async def get_balance(self, account_id: str) -> dict:
        """
        Get the available and pending balance for a connected account.

        Returns:
            dict with 'available' and 'pending' lists (currency → amount in cents).
        """
        import asyncio

        stripe = self._get_stripe()
        loop = asyncio.get_event_loop()

        def _get():
            balance = stripe.Balance.retrieve(stripe_account=account_id)
            return {
                "available": [
                    {"currency": b.currency, "amount": b.amount}
                    for b in balance.available
                ],
                "pending": [
                    {"currency": b.currency, "amount": b.amount}
                    for b in balance.pending
                ],
            }

        return await loop.run_in_executor(None, _get)
