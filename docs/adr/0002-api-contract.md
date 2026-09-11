# ADR 0002 — API contract for /ask and /ask_batched

**Status:** Accepted (W3) · Extended W4
**Defended at:** Design Review #1 (Week 5).
**Owners:** _[Shyamal Hansoti]_
**Date:** _[2026-09-04]_

## Context
AI pipeline exposed through stable Http interface ensuring seperation of concerns between UI and internal pipeline code. 

## Decision
API contracts changes should be done with due deliberation and communicated to all stackholder in timely manner. 
Validate behavior with Mock,Integration & Stress testing. 
Public /ask contract is considered stable and in use. Must ensure any change is non-impacting to consumers.

### Endpoints (locked W3)

- `POST /ask` — request: `{"question": "..."}`; response: `text/plain` stream
- `POST /ask_batched` — request: `{"question": "..."}`; response: `Answer` JSON
- `GET  /health` — response: `{"status": "ok"}`

### Pydantic shapes (W3, additively extended W4)
```
Question:
  question: str  (min_length=1)

Answer (W3 fields):
  content: str
  cost_usd: float
  retries: int

Answer (W4 additive fields):
  confidence: float = 1.0        # 0.0 to 1.0
  sources: list[str] = []
  schema_version: str = "v1"
```

### Schema versioning rule (added W4)

Every `Answer` carries a `schema_version` field.

**Today's shape is `v1`.** It stays `v1` through any additive change:
new optional fields with defaults, new endpoints at different paths,
internal model swaps, prompt edits that don't change the output shape,
retry / logging / observability changes.

**Breaking changes ship as a new `schema_version`** (`v2`, `v3`, …):
removing a required field, renaming a public field, changing a field's
type, making an optional field required, semantic changes (e.g.,
`cost_usd` repurposed to mean something other than USD), changing the
error-response shape.

When `v2` ships:
- `/ask` and `/ask_batched` still return `v1` by default.
- A header `X-Schema-Version: v2` (or `?schema_version=v2`) opts the
  caller into the new shape.
- Both versions are supported in parallel for at least two weeks before
  `v1` is retired.
- The deprecation date is announced in the ADR before removal.

### Cost budget (added W4)
Followin models confidence/accuracy and cost were evaluated with batch of 10 questions.
gpt-4o-mini(Input Rate-0.15, Output Rate-0.60) 
gpt-4o(Input Rate-2.50,Output Rate-10.00)

### Chosen default model (added W4)
The default `Settings.model` is **`gpt-4o-mini`** for the lab. 
gpt-4o cost _20.0x more than gpt-4o-mini on the same questions.
gpt-4o confidence is on higher side nominally but still obervation is that mini's explanation is more meaning full and concise. gpt-4o-mini was picked due to lower cost and not much difference in accuracy between both models.

Model            n    Total $     Avg $/q     Time
---------------------------------------------------
gpt-4o-mini     10     0.000765   0.000077     14.64s 
gpt-4o          10     0.015277   0.001528     21.78s 
```
## Consequences

- **Positive.** The Streamlit UI, the W5 eval harness, and any later consumer integrate once.
- **Negative.** We commit to maintaining `/ask` even when its internalsbecome legacy. Acceptable cost.
- **Open.** Authentication is out of scope for v1. When we layer it in W28/W29
  it will require an `Authorization` header but won't change the request or
  response shape itself.

## Tests securing this contract

- `tests/test_api.py::test_ask_rejects_missing_question` — validation contract.
- `tests/test_api.py::test_health_returns_ok` — /health contract.

## Notes
- JSON + Pydantic carries the cohort through the rest of the
  programme. 