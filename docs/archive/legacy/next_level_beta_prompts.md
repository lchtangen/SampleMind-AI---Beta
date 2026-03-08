# 🔮 Next-Level Beta Readiness Prompts

Each prompt is engineered to drive deep, cross-functional progress toward a fast, smooth beta launch. Use them verbatim with your AI copilots, or adapt the context blocks to the latest state of the repo.

---

## 1. Full-Stack Regression & Coverage Uplift
**Prompt:**
> “You are the QA lead for SampleMind AI, with the goal of raising automated coverage from 40% → 70%. Review the latest FastAPI and Next.js code (hooks, pages, WebSocket glue) and propose a prioritized list of high-value Pytest suites and Playwright/Testing Library specs. Include: specific modules, assertions, seed data requirements, and CI annotations. Then draft the actual test skeletons with fixtures and example asserts so the dev team can copy-paste and iterate.”

---

## 2. Auth & Session Hardening Playbook
**Prompt:**
> “Act as the security engineer preparing SampleMind AI for public beta. Audit the FastAPI auth stack, TokenManager, and Next.js AuthContext implementation. Identify attack surfaces (token reuse, refresh flow, storage, WebSocket auth). Produce a mitigation checklist with code snippets, env toggles, and automated guardrails (lint rules, pytest plugins). Conclude with a validation matrix (manual + automated steps) to sign off the hardening work.”

---

## 3. Real-Time Telemetry & Observability Sprint
**Prompt:**
> “You are the observability architect. Design and partially implement a minimal telemetry stack for SampleMind AI covering backend API latency, WebSocket events, and frontend hook health (useAudio/useWebSocket). Leverage existing dependencies (structlog, loguru, PostHog if possible). Deliver: instrumentation diff suggestions, sample dashboards (Grafana/Loki or lightweight alternative), alert triggers, and a local verification script that proves metrics flow end-to-end.”

---

## 4. Beta Environment Deployment Wizard
**Prompt:**
> “Step into the DevOps engineer role tasked with bootstrapping a managed beta environment within 48 hours. Produce an IaC-lite playbook: Docker Compose overrides, optional Terraform stubs, secret management (Vault or SSM), CDN & TLS guidance. Include migration steps for SQLite → PostgreSQL, Redis provisioning, and smoke-test commands. End with a rollback plan and success criteria checklist.”

---

## 5. Audio Pipeline Stress & Performance Lab
**Prompt:**
> “As the performance specialist, design a stress campaign for the audio upload/analyze pipeline. Generate Locust or k6 scripts (or suggest alternatives) that simulate concurrent creators pushing multi-format audio. Include targets for throughput, acceptable error budgets, and instrumentation hooks to capture CPU/mem hotspots. Produce a remediation backlog ranked by impact with quick fixes (e.g., chunked uploads, async Celery hand-off) vs. long-term refactors.”

---

## 6. Frontend Experience Polish & Accessibility Crusade
**Prompt:**
> “Adopt the role of UX engineer finishing the polish pass before beta. Review the Next.js pages (landing, dashboard, upload, library, analysis) and propose a11y, responsiveness, and animation refinements. Provide component-level diffs using Tailwind & Framer Motion best practices, color-contrast adjustments, and keyboard nav guidelines. Conclude with a QA script and Lighthouse metrics targets.”

---

## 7. Data Lifecycle & Privacy Compliance Audit
**Prompt:**
> “You are the compliance officer ensuring SampleMind AI meets data retention and privacy obligations for beta testers. Map every touchpoint where user/audio data is stored (DB, S3/local storage, caches, logs). Recommend retention policies, automated scrubbing jobs, and updates to `SECURITY.md` & user-facing docs. Draft opt-in/out flows and consent language, plus DevSecOps hooks to verify compliance in CI.”

---

## 8. Beta Onboarding & Support Simulation
**Prompt:**
> “As the product operations lead, build a beta onboarding packet. Include: walkthrough scripts for onboarding sessions, FAQs sourced from current docs, templated Zendesk/Linear macros, and a fallback escalation matrix. Generate a test schedule for dogfooding with internal accounts, capturing success signals (activation metrics) and red flags to monitor during the beta window.”

---

## 9. Feature Flag & Rollout Orchestration
**Prompt:**
> “Play the role of release engineer orchestrating feature-flag-driven rollouts. Audit existing flag usage in backend/frontend, propose a consistent naming taxonomy, and codify a rollout workflow (staging → canary → beta). Provide sample config files, monitoring hooks, and a ‘kill switch’ implementation. Finish with a decision matrix that helps stakeholders choose between flags, env toggles, or A/B experiments.”

---

## 10. Executive Readout & Risk Radar
**Prompt:**
> “Pretend you are preparing the executive weekly readout. Summarize current progress (phases, %, blockers), surface the top 5 beta risks (technical, operational, UX), and propose mitigations with owners and deadlines. Include a visuals section (charts or tables) and a next-week action plan aligned to the new Phase Tracker. Deliver it as a ready-to-send Markdown brief.”

---

**Usage Tips:**
- Pair prompts with the new `docs/phase_alignment_2025-11-09.md` objectives and `PROJECT_PHASE_TRACKER.md` to enforce accountability.
- Encourage teams to paste the resulting AI responses back into the repo (under `/docs/strategic/`) for traceability.
- Re-run prompts after major merges to keep recommendations fresh as code evolves.
