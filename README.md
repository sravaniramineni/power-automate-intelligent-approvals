# Power Automate Intelligent Approvals

AI-assisted approval workflows: extract fields from a document, summarize it, score the risk, then route — auto-approve low-risk items, send high-risk ones to a human with full context. The companion API demonstrates the idempotent, retry-safe backend a Power Automate flow calls.

## When to use this

Approval bottlenecks come from missing context: approvers get a raw invoice PDF with no summary and no risk signal, so everything queues behind a human. Pair this API with a Power Automate cloud flow (trigger → AI extraction → risk score → approval) and the flow can auto-approve the safe 80% while humans focus on the risky 20%.

## How it works

1. **Extract** — `POST /extract` pulls vendor, amount, and a summary from document text.
   (Starter: deterministic extraction — in production this is AI Builder / Document Intelligence.)
2. **Risk-score** — `POST /risk-score` returns a 0–1 score plus signals (`high_amount`, `missing_vendor`)
   and a decision: `auto_approve` or `human_approval`.
3. **Execute safely** — every call goes through `dedupe()` (idempotency keys, so flow
   re-runs never double-process) and `with_retry()` (exponential backoff on transient failures).
4. **Power Automate calls this API** — see `docs/ARCHITECTURE.md` for the flow blueprint:
   trigger → HTTP to this API → condition on `decision` → approval action or auto-post,
   with DLP and Dataverse/SharePoint integration notes.

## Project structure

```
src/main.py        FastAPI service: POST /extract, POST /risk-score
src/idempotency.py dedupe() + with_retry() helpers
docs/ARCHITECTURE.md   Flow blueprint: trigger → AI extraction → risk score → approval
docs/ADR-001.md        Why idempotency + retry live in the API, not the flow
Dockerfile           Container image
.github/workflows/ci.yml   CI on every push
```

## Prerequisites

- Python 3.11+

## Quickstart

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```

Extract fields from an invoice and risk-score it:

```bash
# 1. Extract (pass an idempotency key so flow re-runs are safe)
curl -X POST http://localhost:8000/extract -H "Content-Type: application/json" -d '{
  "text": "Invoice INV-2041 from Acme Corp for services rendered, total $1,250.",
  "idempotency_key": "inv-2041"
}'

# 2. Risk-score it
curl -X POST http://localhost:8000/risk-score -H "Content-Type: application/json" -d '{
  "amount": 1250.0,
  "vendor": "Acme Corp",
  "idempotency_key": "inv-2041-risk"
}'
```

Expected responses:

```json
// /extract
{"vendor": "Acme Corp", "amount": 1250.0, "summary": "Invoice for services; totals match line items."}

// /risk-score
{"risk_score": 0.12, "signals": [], "decision": "auto_approve"}
```

Try a high-risk case and watch it route to a human:

```bash
curl -X POST http://localhost:8000/risk-score -H "Content-Type: application/json" -d '{
  "amount": 8500.0, "vendor": "", "idempotency_key": "inv-2042-risk"
}'
# → {"risk_score": 0.85, "signals": ["high_amount", "missing_vendor"], "decision": "human_approval"}
```

Repeating a call with the same `idempotency_key` returns `{"status": "duplicate", ...}` — the work is never done twice.

## Running the tests / CI

Every push runs the test suite via `.github/workflows/ci.yml`. Run it locally:

```bash
python -m pytest  # add tests/ as the suite grows
```

## Deploy with Docker

```bash
docker build -t intelligent-approvals .
docker run -p 8000:8000 intelligent-approvals
```

## Taking this to production

- Replace `_extract()` with AI Builder's invoice processing (or Azure Document Intelligence) plus field validation rules.
- Store extracted docs and decisions in Dataverse for the audit trail your auditors will ask for.
- Tune the risk thresholds (`0.3` decision boundary, `$5,000` high-amount signal) against historical approval data.
- Add adaptive cards in the approval step showing summary + risk signals so approvers decide in one glance.

## Further reading

- `docs/ARCHITECTURE.md` — the full Power Automate flow blueprint
- `docs/ADR-001.md` — why idempotency + retry live in the API, not the flow
