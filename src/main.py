from fastapi import FastAPI
from pydantic import BaseModel
from .idempotency import dedupe, with_retry

app = FastAPI(title="Intelligent Approvals API")

class DocIn(BaseModel):
    text: str
    idempotency_key: str | None = None

class RiskIn(BaseModel):
    amount: float
    vendor: str = ""
    idempotency_key: str | None = None

def _extract(text: str) -> dict:
    # Production: AI Builder / document intelligence + field validation.
    return {"vendor": "Acme Corp", "amount": 1250.0,
            "summary": "Invoice for services; totals match line items."}

@app.post("/extract")
def extract(doc: DocIn):
    result = with_retry(lambda: _extract(doc.text))
    dup, out = dedupe(doc.idempotency_key, result)
    return out

@app.post("/risk-score")
def risk_score(req: RiskIn):
    score = min(1.0, req.amount / 10000)
    signals = []
    if req.amount > 5000:
        signals.append("high_amount")
    if not req.vendor:
        signals.append("missing_vendor")
    decision = "human_approval" if score > 0.3 or signals else "auto_approve"
    result = {"risk_score": round(score, 2), "signals": signals, "decision": decision}
    dup, out = dedupe(req.idempotency_key, result)
    return out
