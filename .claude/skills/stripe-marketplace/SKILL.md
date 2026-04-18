---
name: stripe-marketplace
description: Stripe Connect Express marketplace with .smpack packs and R2 storage
---

## Stripe Marketplace

### Key Files
- Stripe Connect: `src/samplemind/core/services/stripe_connect.py`
- Pack builder: `src/samplemind/core/packs/pack_builder.py`
- R2 storage: `src/samplemind/services/storage/r2_provider.py`
- API routes: `interfaces/api/routes/marketplace.py`, `billing.py`

### Pack Format
`.smpack` — ZIP archive with manifest:
- name, author, tags, BPM range, key, sample list

### Stripe Connect Flow
1. Creator onboards via Stripe Connect Express
2. Creator uploads pack → stored on Cloudflare R2
3. Buyer purchases → Stripe handles payment split
4. Webhook confirms purchase → unlock download

### Rules
- Stripe webhook verification required for purchase completion
- Validate file sizes and types before upload
- R2 storage uses boto3 S3-compatible API
- Always handle Stripe webhook signature verification
- Test with Stripe test mode keys
