"""
storage.py
==========
A simplified SM-2 spaced-repetition scheduler plus a JSON-backed store for
per-question progress and user-added custom questions.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

from engines import Question, question_to_dict, question_from_dict

QUALITY_AGAIN, QUALITY_HARD, QUALITY_GOOD, QUALITY_EASY = 0, 1, 2, 3
QUALITY_LABELS = {0: "Again", 1: "Hard", 2: "Good", 3: "Easy"}


def sm2_update(state: dict, quality: int) -> None:
    """Mutates `state` in place. quality: 0=Again(fail) 1=Hard 2=Good 3=Easy."""
    now = datetime.now()
    if quality == QUALITY_AGAIN:
        state["reps"] = 0
        state["interval_days"] = 0
        state["due"] = (now + timedelta(minutes=10)).isoformat()
        state["ease"] = max(1.3, state.get("ease", 2.5) - 0.2)
    else:
        ease = state.get("ease", 2.5)
        q5 = {QUALITY_HARD: 3, QUALITY_GOOD: 4, QUALITY_EASY: 5}[quality]
        ease = max(1.3, ease + (0.1 - (5 - q5) * (0.08 + (5 - q5) * 0.02)))
        reps = state.get("reps", 0) + 1
        prev_interval = state.get("interval_days", 0)
        if reps == 1:
            interval = 1
        elif reps == 2:
            interval = 6
        else:
            interval = max(prev_interval + 1, round(prev_interval * ease))
        if quality == QUALITY_HARD:
            interval = max(1, round(interval * 0.6))
        elif quality == QUALITY_EASY:
            interval = max(interval + 1, round(interval * 1.3))
        state["ease"] = ease
        state["reps"] = reps
        state["interval_days"] = interval
        state["due"] = (now + timedelta(days=interval)).isoformat()
    state["last_result"] = quality
    state["last_reviewed"] = now.isoformat()


class ProgressStore:
    """Everything that needs to survive a restart: SM-2 state per question,
    and any custom questions the user has added."""

    def __init__(self, path: str):
        self.path = path
        self.data = {"progress": {}, "custom_questions": [], "streak": {"current": 0, "best": 0,
                                                                          "last_active_date": None}}
        self.load()

    def load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self.data = loaded
            except Exception:
                pass
        self.data.setdefault("progress", {})
        self.data.setdefault("custom_questions", [])
        self.data.setdefault("streak", {"current": 0, "best": 0, "last_active_date": None})

    def save(self) -> None:
        try:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            os.replace(tmp, self.path)
        except Exception:
            pass

    # -- per-question SM-2 state ----------------------------------------
    def get_state(self, qid: str) -> dict:
        if qid not in self.data["progress"]:
            self.data["progress"][qid] = {
                "ease": 2.5, "reps": 0, "interval_days": 0,
                "due": datetime.now().isoformat(),
                "last_result": None, "last_reviewed": None,
            }
        return self.data["progress"][qid]

    def is_new(self, qid: str) -> bool:
        return self.get_state(qid)["last_result"] is None

    def is_due(self, qid: str) -> bool:
        state = self.get_state(qid)
        try:
            due = datetime.fromisoformat(state["due"])
        except Exception:
            return True
        return due <= datetime.now()

    def due_in_words(self, qid: str) -> str:
        state = self.get_state(qid)
        if state["last_result"] is None:
            return "new"
        try:
            due = datetime.fromisoformat(state["due"])
        except Exception:
            return "due"
        delta = due - datetime.now()
        if delta.total_seconds() <= 0:
            return "due now"
        if delta.days >= 1:
            return f"due in {delta.days}d"
        hours = int(delta.total_seconds() // 3600)
        if hours >= 1:
            return f"due in {hours}h"
        minutes = max(1, int(delta.total_seconds() // 60))
        return f"due in {minutes}m"

    def update(self, qid: str, quality: int) -> None:
        state = self.get_state(qid)
        sm2_update(state, quality)
        self._bump_streak()
        self.save()

    # -- streak (simple "did you review anything today" counter) --------
    def _bump_streak(self) -> None:
        today = datetime.now().date().isoformat()
        streak = self.data["streak"]
        last = streak.get("last_active_date")
        if last == today:
            return
        if last is not None:
            try:
                gap = (datetime.now().date() - datetime.fromisoformat(last).date()).days
            except Exception:
                gap = 2
        else:
            gap = 1
        streak["current"] = streak.get("current", 0) + 1 if gap == 1 else 1
        streak["best"] = max(streak.get("best", 0), streak["current"])
        streak["last_active_date"] = today

    def streak_info(self) -> dict:
        return dict(self.data.get("streak", {"current": 0, "best": 0}))

    # -- custom questions -------------------------------------------------
    def add_custom_question(self, q: "Question") -> None:
        self.data["custom_questions"].append(question_to_dict(q))
        self.save()

    def load_custom_questions(self) -> list:
        out = []
        for d in self.data.get("custom_questions", []):
            try:
                out.append(question_from_dict(d))
            except Exception:
                continue
        return out

    # -- stats --------------------------------------------------------
    def mastered_count(self, questions) -> int:
        return sum(1 for q in questions if self.get_state(q.id).get("reps", 0) >= 2
                   and self.get_state(q.id).get("last_result", 0) >= QUALITY_GOOD)