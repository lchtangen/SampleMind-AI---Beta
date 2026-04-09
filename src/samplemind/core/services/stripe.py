"""
Stripe Monetization Service — SampleMind v3.0 (Step 25).

Implements the 3-tier SaaS pricing model:
  - free:  5 analyses / day,   0 GB cloud storage
  - pro:   unlimited analyses, 10 GB cloud storage  ($9/month)
  - team:  unlimited analyses, 100 GB cloud storage ($49/month)

Responsibilities:
  1. Create/retrieve Stripe Customers
  2. Create checkout sessions for pro/team upgrades
  3. Handle webhook events (checkout.session.completed, subscription updates)
  4. Usage gate: raise UsageLimitError when free user exceeds daily limit
  5. Usage metering: record analysis calls for billing dashboards

Configuration (env vars):
  STRIPE_SECRET_KEY     — Stripe secret key (sk_live_... or sk_test_...)
  STRIPE_WEBHOOK_SECRET — Stripe webhook signing secret (whsec_...)
  STRIPE_PRO_PRICE_ID   — Stripe Price ID for pro monthly plan
  STRIPE_TEAM_PRICE_ID  — Stripe Price ID for team monthly plan

Usage::

    from samplemind.core.services.stripe import StripeService, UsageLimitError

    svc = StripeService()

    # Check if user can make an analysis call
    svc.check_usage(user_id="user123", tier="free", api_calls_today=4)

    # Create upgrade checkout session
    session = await svc.create_checkout_session(
        user_id="user123",
        email="user@example.com",
        plan="pro",
        success_url="https://app.samplemind.ai/billing/success",
        cancel_url="https://app.samplemind.ai/billing",
    )
    print(session.url)  # Redirect user here
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ── Tier limits ───────────────────────────────────────────────────────────────

TIER_LIMITS: Dict[str, Dict[str, Any]] = {
    "free": {
        "analyses_per_day": 5,
        "storage_gb": 0,
        "ai_coaching": False,
        "priority_queue": False,
        "price_monthly_usd": 0,
    },
    "pro": {
        "analyses_per_day": -1,       # unlimited
        "storage_gb": 10,
        "ai_coaching": True,
        "priority_queue": False,
        "price_monthly_usd": 9,
    },
    "team": {
        "analyses_per_day": -1,       # unlimited
        "storage_gb": 100,
        "ai_coaching": True,
        "priority_queue": True,
        "price_monthly_usd": 49,
    },
}


class UsageLimitError(Exception):
    """Raised when a user exceeds their tier's usage limit."""

    def __init__(self, tier: str, limit: int) -> None:
        self.tier = tier
        self.limit = limit
        super().__init__(
            f"Daily analysis limit reached ({limit}/day on {tier} plan). "
            "Upgrade to Pro for unlimited analyses."
        )


# ── Stripe service ────────────────────────────────────────────────────────────


@dataclass
class CheckoutSession:
    """Minimal checkout session result."""

    session_id: str
    url: str


class StripeService:
    """
    Stripe integration for SampleMind SaaS billing.

    Requires `stripe` Python SDK: pip install stripe
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ) -> None:
        self.secret_key = secret_key or os.getenv("STRIPE_SECRET_KEY", "")
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self._pro_price_id = os.getenv("STRIPE_PRO_PRICE_ID", "")
        self._team_price_id = os.getenv("STRIPE_TEAM_PRICE_ID", "")

        if not self.secret_key:
            logger.warning(
                "STRIPE_SECRET_KEY not set — Stripe features disabled. "
                "Set the env var to enable billing."
            )

    # ── Usage gate ────────────────────────────────────────────────────────────

    @staticmethod
    def check_usage(user_id: str, tier: str, api_calls_today: int) -> None:
        """
        Raise UsageLimitError if the user has exceeded their daily limit.

        Args:
            user_id: User identifier (for logging).
            tier: User's subscription tier ("free", "pro", "team").
            api_calls_today: Number of analysis calls already made today.

        Raises:
            UsageLimitError: If the free daily limit is exceeded.
        """
        limit = TIER_LIMITS.get(tier, TIER_LIMITS["free"])["analyses_per_day"]
        if limit == -1:
            return  # unlimited tier
        if api_calls_today >= limit:
            logger.warning(
                "Usage limit hit: user=%s tier=%s calls=%d limit=%d",
                user_id,
                tier,
                api_calls_today,
                limit,
            )
            raise UsageLimitError(tier=tier, limit=limit)

    # ── Customer management ───────────────────────────────────────────────────

    def get_or_create_customer(
        self, user_id: str, email: str, name: str = ""
    ) -> str:
        """
        Get or create a Stripe Customer for the given user.

        Returns the Stripe customer ID (cus_...).
        """
        if not self.secret_key:
            return ""

        try:
            import stripe

            stripe.api_key = self.secret_key

            # Search for existing customer by metadata
            existing = stripe.Customer.search(
                query=f'metadata["samplemind_user_id"]:"{user_id}"',
                limit=1,
            )
            if existing.data:
                return existing.data[0].id

            # Create new customer
            customer = stripe.Customer.create(
                email=email,
                name=name or email,
                metadata={"samplemind_user_id": user_id},
            )
            logger.info("Created Stripe customer %s for user %s", customer.id, user_id)
            return customer.id

        except ImportError:
            logger.warning("stripe SDK not installed — run: pip install stripe")
            return ""
        except Exception as exc:
            logger.error("Stripe customer creation failed: %s", exc)
            return ""

    # ── Checkout ──────────────────────────────────────────────────────────────

    async def create_checkout_session(
        self,
        user_id: str,
        email: str,
        plan: str,
        success_url: str,
        cancel_url: str,
        name: str = "",
    ) -> Optional[CheckoutSession]:
        """
        Create a Stripe Checkout Session for a plan upgrade.

        Args:
            user_id: Internal user ID.
            email: User email.
            plan: "pro" or "team".
            success_url: Redirect URL on successful payment.
            cancel_url: Redirect URL if user cancels.
            name: Optional display name.

        Returns:
            CheckoutSession with .url to redirect the user, or None on error.
        """
        if not self.secret_key:
            logger.warning("Stripe not configured — checkout session skipped")
            return None

        price_id = self._pro_price_id if plan == "pro" else self._team_price_id
        if not price_id:
            logger.error("STRIPE_%s_PRICE_ID not set", plan.upper())
            return None

        try:
            import stripe
            import asyncio

            stripe.api_key = self.secret_key

            customer_id = self.get_or_create_customer(user_id, email, name)

            # Run synchronous stripe call in thread pool
            loop = asyncio.get_event_loop()
            session = await loop.run_in_executor(
                None,
                lambda: stripe.checkout.Session.create(
                    customer=customer_id or None,
                    customer_email=None if customer_id else email,
                    mode="subscription",
                    line_items=[{"price": price_id, "quantity": 1}],
                    success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                    cancel_url=cancel_url,
                    metadata={
                        "samplemind_user_id": user_id,
                        "plan": plan,
                    },
                    subscription_data={
                        "metadata": {"samplemind_user_id": user_id, "plan": plan}
                    },
                ),
            )

            logger.info(
                "Checkout session created: %s for user=%s plan=%s",
                session.id,
                user_id,
                plan,
            )
            return CheckoutSession(session_id=session.id, url=session.url)

        except ImportError:
            logger.warning("stripe SDK not installed — run: pip install stripe")
            return None
        except Exception as exc:
            logger.error("Stripe checkout session failed: %s", exc)
            return None

    # ── Webhook handling ──────────────────────────────────────────────────────

    def handle_webhook(
        self, payload: bytes, signature: str
    ) -> Optional[Dict[str, Any]]:
        """
        Verify and parse a Stripe webhook event.

        Args:
            payload: Raw request body bytes.
            signature: Value of Stripe-Signature header.

        Returns:
            Parsed event dict, or None if verification fails.
        """
        if not self.secret_key or not self.webhook_secret:
            logger.warning("Stripe webhook secret not configured")
            return None

        try:
            import stripe

            stripe.api_key = self.secret_key
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event

        except ImportError:
            logger.warning("stripe SDK not installed")
            return None
        except Exception as exc:
            logger.warning("Stripe webhook verification failed: %s", exc)
            return None

    def extract_subscription_update(
        self, event: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """
        Extract user_id and new plan from a subscription webhook event.

        Handles:
          - checkout.session.completed
          - customer.subscription.updated
          - customer.subscription.deleted

        Returns:
            {"user_id": "...", "plan": "pro"|"team"|"free"} or None.
        """
        event_type = event.get("type", "")
        obj = event.get("data", {}).get("object", {})
        metadata = obj.get("metadata", {})
        user_id = metadata.get("samplemind_user_id", "")

        if not user_id:
            return None

        if event_type == "checkout.session.completed":
            plan = metadata.get("plan", "pro")
            logger.info("Subscription activated: user=%s plan=%s", user_id, plan)
            return {"user_id": user_id, "plan": plan}

        if event_type == "customer.subscription.deleted":
            logger.info("Subscription cancelled: user=%s", user_id)
            return {"user_id": user_id, "plan": "free"}

        if event_type == "customer.subscription.updated":
            # Plan name is in the price metadata — use tier from items
            items = obj.get("items", {}).get("data", [])
            plan = "pro"  # default
            if items:
                price_id = items[0].get("price", {}).get("id", "")
                if price_id == self._team_price_id:
                    plan = "team"
            return {"user_id": user_id, "plan": plan}

        return None
