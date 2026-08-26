"""Typed configuration + run summary — Pydantic v2 models.

Two models with different roles:
  - Settings:    config (same every run; loaded at module init)
  - RunSummary:  observation (one row per execution; produced at run end)
"""
from __future__ import annotations
from pathlib import Path
from pydantic import BaseModel,Field

class Settings(BaseModel):
    questions_csv: Path  = Path("data/questions.csv")
    results_json:  Path  = Path("results.json")
    results_db:    Path  = Path("results.db")
    batch_size:    int   = Field(5,   gt=0, le=20)
    fail_rate:     float = Field(0.0, ge=0.0, le=1.0)
    model:         str   = "gpt-4o-mini"
    use_fake:      bool  = True 