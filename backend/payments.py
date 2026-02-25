"""
Gab44 Stripe Payment Integration
==================================
Handles subscription checkout, webhook processing, and tier management.

Requires environment variables:
  STRIPE_SECRET_KEY - Stripe API secret key
  STRIPE_WEBHOOK_SECRET - Stripe webhook signing secret
  FRONTEND_URL - Frontend URL for checkout redirects

Subscription tiers map to Stripe Price IDs set via:
  STRIPE_PRICE_ENTHUSIAST
  STRIPE_PRICE_ADVANCED
  STRIPE_PRICE_PROFESSIONAL
"""

import os
import logging

import stripe

logger = logging.getLogger(__name__)

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# Stripe Price IDs for each subscription tier (set in environment)
PRICE_IDS = {
    "enthusiast": os.environ.get("STRIPE_PRICE_ENTHUSIAST", ""),
    "advanced": os.environ.get("STRIPE_PRICE_ADVANCED", ""),
    "professional": os.environ.get("STRIPE_PRICE_PROFESSIONAL", ""),
}

# Map Stripe Price IDs back to tier names
PRICE_TO_TIER = {v: k for k, v in PRICE_IDS.items() if v}

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY


def is_configured() -> bool:
    """Check if Stripe is properly configured."""
    return bool(STRIPE_SECRET_KEY)


def create_checkout_session(
    user_id: str,
    user_email: str,
    tier: str,
    stripe_customer_id: str = None,
) -> dict:
    """
    Create a Stripe Checkout session for a subscription upgrade.

    Returns {"url": "https://checkout.stripe.com/...", "session_id": "cs_..."}
    """
    if not is_configured():
        raise ValueError("Stripe is not configured. Set STRIPE_SECRET_KEY.")

    price_id = PRICE_IDS.get(tier)
    if not price_id:
        raise ValueError(f"No Stripe Price ID configured for tier '{tier}'. Set STRIPE_PRICE_{tier.upper()}.")

    session_params = {
        "mode": "subscription",
        "payment_method_types": ["card"],
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{FRONTEND_URL}/dashboard?upgrade=success&tier={tier}",
        "cancel_url": f"{FRONTEND_URL}/pricing?upgrade=cancelled",
        "metadata": {"user_id": user_id, "tier": tier},
        "client_reference_id": user_id,
    }

    if stripe_customer_id:
        session_params["customer"] = stripe_customer_id
    else:
        session_params["customer_email"] = user_email

    session = stripe.checkout.Session.create(**session_params)

    return {"url": session.url, "session_id": session.id}


def create_billing_portal_session(stripe_customer_id: str) -> dict:
    """
    Create a Stripe Billing Portal session for managing subscriptions.

    Returns {"url": "https://billing.stripe.com/..."}
    """
    if not is_configured():
        raise ValueError("Stripe is not configured.")

    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=f"{FRONTEND_URL}/settings",
    )

    return {"url": session.url}


def verify_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Verify and parse a Stripe webhook event.

    Returns the parsed event dict.
    Raises ValueError if verification fails.
    """
    if not STRIPE_WEBHOOK_SECRET:
        raise ValueError("Stripe webhook secret not configured.")

    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )

    return event


def handle_checkout_completed(event: dict) -> dict:
    """
    Handle a checkout.session.completed event.

    Returns {"user_id": ..., "tier": ..., "stripe_customer_id": ..., "stripe_subscription_id": ...}
    """
    session = event["data"]["object"]

    user_id = session.get("client_reference_id") or session.get("metadata", {}).get("user_id")
    tier = session.get("metadata", {}).get("tier", "enthusiast")
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")

    return {
        "user_id": user_id,
        "tier": tier,
        "stripe_customer_id": customer_id,
        "stripe_subscription_id": subscription_id,
    }


def handle_subscription_updated(event: dict) -> dict:
    """
    Handle a customer.subscription.updated event (upgrade/downgrade).

    Returns {"stripe_customer_id": ..., "tier": ..., "status": ...}
    """
    subscription = event["data"]["object"]
    customer_id = subscription.get("customer")
    status = subscription.get("status")  # active, past_due, canceled, etc.

    # Determine the tier from the price ID
    tier = "seeker"  # Default fallback
    items = subscription.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id", "")
        tier = PRICE_TO_TIER.get(price_id, "seeker")

    return {
        "stripe_customer_id": customer_id,
        "tier": tier if status == "active" else "seeker",
        "status": status,
    }


def handle_subscription_deleted(event: dict) -> dict:
    """
    Handle a customer.subscription.deleted event (cancellation).

    Returns {"stripe_customer_id": ..., "tier": "seeker"}
    """
    subscription = event["data"]["object"]
    customer_id = subscription.get("customer")

    return {
        "stripe_customer_id": customer_id,
        "tier": "seeker",
    }
