
# Lab 2 — Copilot Coding-assistant verification note
## The change
Add a --limit N CLI flag that processes only the first N questions (useful during real-API debugging)

## The ask
Ask Mode -Examine the code and suggest change to add a --limit N CLI flag that processes only the first N questions (useful during real-API
debugging)

## What it produced
Implement parsing with `argparse` in `src/pipeline/pipeline.py`, slice the loaded question list after `load_questions(...)`
*Steps**
1. Add CLI parsing in `src/pipeline/pipeline.py`'s main section:
   - Import `argparse` near other imports.
   - Create an `ArgumentParser` and add `--limit` with `type=int` and `default=None`.
   - Parse args in the `if __name__ == '__main__'` block (before launching the run).
2. After `questions = load_questions(settings.questions_csv)` slice the list:
   - Validate `limit` is >= 0; if invalid, exit with an error message.
   - If `limit is not None`, set `questions = questions[:limit]`.

**Relevant files**
- [src/pipeline/pipeline.py](src/pipeline/pipeline.py#L168-L181) — Insert `argparse` parsing in the main block and slice after `load_questions(...)`.

## What I verified before accepting
- Diff read: Chang
- Test run: Result were expected both for limit and without limit tests
    With limit
    python -m src.pipeline.pipeline --limit 5
    Without limit
    python -m src.pipeline.pipeline
- Security check: <new deps? secret-handling changes? unsanitised input?
>
## What I changed before committing
Removed logic to throw error if the limit is not provided as want process all questions if no limit. 
