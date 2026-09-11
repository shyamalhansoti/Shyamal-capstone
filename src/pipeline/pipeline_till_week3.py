"""pipeline.py — Week 2 hands-on starter.

We'll fill in the TODOs together during the live session. The pieces:

    Step 2 — async def ask_llm                 (one call)
    Step 3 — ask_llm_with_retry                (exponential backoff)
    Step 4 — run_batch with asyncio.gather     (parallel fan-out)
    Step 5 — JSON-formatted structured logging

For the live demo we call ``fake_ask_llm`` from ``fake_llm.py`` —
no API quota, no network flakiness, and a ``fail_rate`` knob so retries
fire on demand. In the lab you'll swap to the real ``AsyncOpenAI`` client
(same ``Question``/``Answer`` shape — only one import changes).

Run it (after the TODOs are filled):
    python pipeline.py           # fail_rate = 0.0  (clean parallel run)
    python pipeline.py 0.4       # fail_rate = 0.4  (forces retries)
"""
from __future__ import annotations
import asyncio
import json
import logging
import time
import csv
from pathlib import Path

# Live-session stand-in. Same Pydantic shape as the real call.
#from .fake_llm import Question, Answer, fake_ask_llm, FakeLLMError

from .logging_config import get_logger
from .settings import Settings, RunSummary 
# ─────────────────────────────────────────────────────────────────────────────
# Logger — shared across the package
# ─────────────────────────────────────────────────────────────────────────────
log = get_logger()

_settings_for_import = Settings()

if _settings_for_import.use_fake:
    from .fake_llm import Question, Answer, fake_ask_llm, FakeLLMError
else:
    from dotenv import load_dotenv
    from openai import AsyncOpenAI
    from pydantic import BaseModel

    load_dotenv()
    _client = AsyncOpenAI()

    class Question(BaseModel):
        text: str

    class Answer(BaseModel):
        question: str
        text:     str
        cost_usd: float
        retries:  int = 0


def load_questions(path: str | Path = "data/questions.csv") -> list[Question]:
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return [Question(text=row["text"]) for row in rows if row.get("text")]

# ---------- Step 2: one async call ----------
async def ask_llm(q: Question, fail_rate: float = 0.0) -> Answer:
    """One call. Live demo: fake. Lab: real AsyncOpenAI (same signature)."""
    # TODO (Step 2): return await fake_ask_llm(q, fail_rate=fail_rate)
    # TODO (Step 5): once logging is configured, also log here, e.g.
    #                log.info(f"asked: {q.text[:40]}")
    #raise NotImplementedError("Step 2 — call fake_ask_llm and return the Answer")
    #return await fake_ask_llm(q, fail_rate=fail_rate)
    if _settings_for_import.use_fake:
        ans=await fake_ask_llm(q, fail_rate=fail_rate)
    else:
        resp = await _client.chat.completions.create(
            model=_settings_for_import.model,
            messages=[{"role": "user", "content": q.text}],
        )
        ans = Answer(
            question=q.text,
            text=resp.choices[0].message.content,
            cost_usd=0.0001,                  # real cost-from-usage lands in W25
        )   
    
    log.info(f"asked: {q.text[:40]}")
    return ans

# ---------- Step 3: retry with exponential backoff ----------
async def ask_llm_with_retry(
    q: Question, tries: int = 3, fail_rate: float = 0.0
) -> Answer:
    """Retry up to ``tries`` times. Wait 1 s, 2 s, 4 s between attempts.
    Re-raises the last exception if all attempts fail (no silent failures)."""
    # TODO (Step 3):  
    for attempt in range(tries):
        try:
            ans = await ask_llm(q, fail_rate=fail_rate)
            ans.retries = attempt
            return ans
        except Exception as exc:
            if attempt == tries - 1:
                raise
            log.warning(f"retry {attempt + 1} for: {q.text[:40]} ({exc})")            
            await asyncio.sleep(2 ** attempt)
    raise RuntimeError("unreachable")          # pragma: no cover


# ---------- Step 4: gather it all together ----------
async def run_batch(
    questions: list[Question], fail_rate: float = 0.0
) -> list[Answer]:
    """Fire all questions in parallel via ``asyncio.gather``."""
    # TODO (Step 4):
    tasks = [ask_llm_with_retry(q, fail_rate=fail_rate) for q in questions]
    return await asyncio.gather(*tasks)
    #raise NotImplementedError("Step 4 — build the tasks list and gather them")


async def run_in_batches(questions, batch_size=5, fail_rate=0.0)->list[Answer]:
    out: list[Answer]=[]

    for i in range(0,len(questions),batch_size):

        chunk=questions[i:i+batch_size]
        log.info(f"batch {i // batch_size + 1}: {len(chunk)} questions")
        batch_answers=await asyncio.gather(*(ask_llm_with_retry(q, fail_rate=fail_rate) for q in chunk))
        out.extend(batch_answers)
        await asyncio.sleep(0.1)
    return out

def  summarise_run(answers:list[Answer], *, started_at: float, elapsed: float, fail_rate: float,use_fake: bool) -> RunSummary:

    return RunSummary(
        started_at      = started_at,
        elapsed_seconds = elapsed,
        n_questions     = len(answers),
        n_succeeded     = len(answers),
        n_retries_total = sum(a.retries  for a in answers),
        total_cost_usd  = sum(a.cost_usd for a in answers),
        fail_rate       = fail_rate,
        use_fake        = use_fake,
    )


# ---------- Step 5: structured (JSON) logging ----------
# TODO (Step 5):
#   * class JsonFormatter(logging.Formatter): ...
#       (emit one JSON record per call with ts / level / msg)
#   * log = logging.getLogger("pipeline"); log.setLevel(logging.INFO)
#   * handler = logging.StreamHandler(); handler.setFormatter(JsonFormatter())
#   * log.addHandler(handler)
#   * Then go back to ask_llm() and add: log.info(f"asked: {q.text[:40]}")
    # class JsonFormatter(logging.Formatter):
    #     log = logging.getLogger("pipeline") 
    #     log.setLevel(logging.INFO)
    #     handler = logging.StreamHandler(); 
    #     handler.setFormatter(JsonFormatter())
    #     log.addHandler(handler)

# ---------- main ----------
if __name__ == "__main__":
    import sys
    import argparse

    #fail_rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    settings = Settings()
    log.info(f"config:{settings.model_dump(mode='json')}")
    # sample = [
    #     Question(text="What is RAG in one sentence?"),
    #     Question(text="Name three uses of vector databases."),
    #     Question(text="Why might an LLM hallucinate?"),
    # ]
    questions=load_questions(settings.questions_csv)
    log.info(f"loaded {len(questions)}questions")

    parser = argparse.ArgumentParser(description="Run the RAG pipeline")
    parser.add_argument("--limit", "-n",type=int,help="Process only the first N questions (>=0). If omitted, process all questions.")
    args = parser.parse_args()

    if args.limit is not None:
        questions = questions[: args.limit]
        log.info(f"limiting questions to first {args.limit}")
    
    started=time.time()
    #answers = asyncio.run(run_batch(sample, fail_rate=settings.fail_rate))
    answers=asyncio.run(run_in_batches(questions,settings.batch_size,fail_rate=settings.fail_rate))
    
    elapsed = time.time() - started
    summary=summarise_run(answers, started_at=started,elapsed=elapsed, fail_rate=settings.fail_rate,use_fake=settings.use_fake)
    log.info(f"summary: {summary.model_dump_json()}")
    
      # Write the structured artefact
    settings.results_json.write_text(
        json.dumps({
            "summary": summary.model_dump(mode="json"),
            "answers": [a.model_dump() for a in answers],
        }, indent=2),
        encoding="utf-8",
    )

    print(f"\n{len(answers)} answers to {settings.results_json} in {elapsed:.2f}s\n")
    for a in answers:
        print(f"- {a.text[:180]}")
    
    from .store import connect , write_run ,write_answers 

    with connect(settings.results_db) as con:
        run_id = write_run(con, summary)
        n = write_answers(con, run_id, answers)

    log.info(f"persisted run {run_id} with {n} answers to{settings.results_db}")