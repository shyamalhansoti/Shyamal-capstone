# ADR 0002 — /ask API Contract

**Status:** Locked from Week 3.
**Defended at:** Design Review #1 (Week 5).
**Owners:** _[Shyamal Hansoti]_
**Date:** _[2026-09-04]_

## Context
AI pipeline exposed through stable Http interface ensuring seperation of concerns between UI and internal pipeline code. 

##Public Request
Question(question: str)

Answer(content: str,cost_usd: float,retries: int)

Keep v1 for compatible internal additive changes.


## Decision
API contracts changes should be done with due deliberation and communicated to all stackholder in timely manner. 
Validate behavior with Mock,Integration & Stress testing. 
Public /ask contract is considered stable and in use. Must ensure any change is non-impacting to consumers.

## Versioning Rule

- `/ask` is locked from Week 3.
- **Don't bump** for additive changes:
  - New optional fields on Answer
  - Internal model swaps (including changes to the W2 pipeline's `text`-named fields)
  - Logging / observability changes
  - Retry-policy tweaks
  - Internal prompt edits
- **Do bump to /v2/ask** for breaking changes:
  - Field removal or rename on the *public* shape (Question, Answer)
  - Type change on a public field
  - Required ↔ optional change
  - Semantic change to a field's meaning
  - Change to the error-response shape
- When `/v2/ask` ships, `/v1/ask` runs in parallel for **at least 2 weeks**
  before retirement; consumers get an `X-Deprecation` warning header.
- Schema versioning on the response body lands in W4 (`schema_version` field
  added to `Answer`). The endpoint contract is separate from the body schema.

## Consequences

- **Positive.** The Streamlit UI, the W5 eval harness, and any later consumer
  integrate once.
- **Negative.** We commit to maintaining `/ask` even when its internals
  become legacy. Acceptable cost.
- **Open.** Authentication is out of scope for v1. When we layer it in W28/W29
  it will require an `Authorization` header but won't change the request or
  response shape itself.

## Tests securing this contract

- `tests/test_api.py::test_ask_rejects_missing_question` — validation contract.
- `tests/test_api.py::test_health_returns_ok` — /health contract.

