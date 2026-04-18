---
applyTo: "src/samplemind/core/packs/**/*.py,src/samplemind/core/services/**/*.py"
---

# Marketplace & Packs Instructions

- Pack builder: `core/packs/pack_builder.py` — `.smpack` ZIP builder with manifest
- Stripe Connect: `core/services/stripe_connect.py` — Express marketplace
- R2 Storage: `services/storage/r2_provider.py` — Cloudflare R2 (boto3 S3-compatible)
- API routes: `interfaces/api/routes/marketplace.py`, `billing.py`
- Pack manifest includes: name, author, tags, BPM range, key, sample list
- Stripe webhook verification required for purchase completion
- Always validate file sizes and types before upload
