from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Intelligent Approvals API")

class DocIn(BaseModel):
    text: str

class RiskIn(BaseModel):
    amount: float
    vendor: str = ""

@app.post("/extract")
def extract(doc: DocIn):
    # Production: AI Builder / document intelligence + validation.
    return {"vendor": "Acme Corp", "amount": 1250.0, "summary": "Invoice for services; totals match."}

@app.post("/risk-score")
def risk_score(req: RiskIn):
    score = min(1.0, req.amount / 10000)
    decision = "human_approval" if score > 0.3 else "auto_approve"
    return {"risk_score": round(score, 2), "decision": decision}
