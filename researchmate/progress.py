"""Local, answer-free history for the ResearchMate learning dashboard."""

import json
import sqlite3
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "viva_progress.sqlite3"


def _connect() -> sqlite3.Connection:
    try:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(_DB_PATH, timeout=10)
    except Exception:
        # Fallback to /tmp or memory if workspace directory is read-only
        tmp_db = Path("/tmp") / "viva_progress.sqlite3"
        try:
            connection = sqlite3.connect(tmp_db, timeout=10)
        except Exception:
            connection = sqlite3.connect(":memory:")

    connection.row_factory = sqlite3.Row
    connection.execute(
        """CREATE TABLE IF NOT EXISTS viva_sessions (
            session_id TEXT PRIMARY KEY,
            paper_name TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            average_score REAL NOT NULL,
            question_count INTEGER NOT NULL,
            topic_scores TEXT NOT NULL
        )"""
    )
    connection.commit()
    return connection


def save_completed_viva(paper_name: str, turns: List[Dict[str, Any]]) -> None:
    """Store aggregate scores and topic labels, never students' answers."""
    if not turns:
        return
    by_topic: Dict[str, List[int]] = defaultdict(list)
    scores = []
    for index, turn in enumerate(turns, start=1):
        score = max(1, min(5, int(turn.get("score", 1))))
        scores.append(score)
        topic = str(turn.get("focus") or f"Question {index}").strip()
        by_topic[topic].append(score)
    topic_scores = {
        topic: round(sum(values) / len(values), 2)
        for topic, values in by_topic.items()
    }
    connection = _connect()
    try:
        connection.execute(
            """INSERT INTO viva_sessions
            (session_id, paper_name, completed_at, average_score, question_count, topic_scores)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                uuid.uuid4().hex,
                paper_name,
                datetime.now().astimezone().isoformat(timespec="minutes"),
                round(sum(scores) / len(scores), 2),
                len(scores),
                json.dumps(topic_scores, ensure_ascii=False),
            ),
        )
        connection.commit()
    finally:
        connection.close()


def load_viva_history(limit: int = 200) -> List[Dict[str, Any]]:
    """Return recent completed session summaries for the dashboard."""
    connection = _connect()
    try:
        rows = connection.execute(
            """SELECT paper_name, completed_at, average_score, question_count, topic_scores
            FROM viva_sessions ORDER BY completed_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    finally:
        connection.close()
    return [
        {
            "paper_name": row["paper_name"],
            "completed_at": row["completed_at"],
            "average_score": row["average_score"],
            "question_count": row["question_count"],
            "topic_scores": json.loads(row["topic_scores"]),
        }
        for row in rows
    ]
