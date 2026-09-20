# Architecture

## Flow
1. Trigger: new invoice/request in SharePoint or Dataverse.
2. AI extraction: pull vendor, amount, dates, line items.
3. Summarization: one-paragraph brief for the approver.
4. Risk scoring: amount thresholds, vendor history, missing fields.
5. Routing: auto-approve low risk; human approval for high risk.
6. Audit: every decision logged with inputs and model version.

## Power Automate design
- Scope actions with try/catch; configure run-after for failures.
- Use child flows for extraction and scoring to enable reuse.
- Store approvals and outcomes in Dataverse for reporting.

## Governance
- DLP: block exfiltration connectors in production.
- Least-privilege service principals for API access.
