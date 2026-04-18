---
name: stripe-marketplace
description: Guide for Stripe Connect marketplace integration. Use when working on pack publishing, purchases, or billing.
---

## Stripe Connect Marketplace

### Architecture
- **Stripe Connect:** `src/samplemind/core/services/stripe_connect.py`
- **API routes:** `src/samplemind/interfaces/api/routes/marketplace.py`, `billing.py`
- **Pack builder:** `src/samplemind/core/packs/pack_builder.py`
- **R2 Storage:** `src/samplemind/services/storage/r2_provider.py`

### Flow
1. Creator publishes sample pack → `.smpack` ZIP built with manifest
2. Pack uploaded to Cloudflare R2 (S3-compatible)
3. Stripe Express account created for creator
4. Buyer purchases via Stripe Checkout
5. Webhook confirms payment → pack access granted
6. Stripe Connect handles revenue split

### Webhook Pattern
```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    event = stripe.Webhook.construct_event(payload, sig, webhook_secret)
    # Handle event...
```

### Security
- Always verify webhook signatures
- Validate file sizes and types before upload
- Use Stripe's idempotency keys for payment operations
