# Power Automate Intelligent Approvals

AI-assisted approval workflows: extract, summarize, risk-score, then route to humans.

## Problem
Approval bottlenecks come from missing context: approvers get raw documents with no summary or risk signal.

## What it includes
- Power Automate cloud flow blueprint: trigger -> AI extraction -> risk score -> approval
- Companion API stub for document extraction and risk scoring
- Human-in-the-loop for high-risk items; auto-approve low-risk with audit trail
- Dataverse/SharePoint integration notes and DLP considerations

## Architecture
See `docs/ARCHITECTURE.md`.

## Quickstart
```bash
pip install -r requirements.txt
uvicorn src.main:app --reload
```
