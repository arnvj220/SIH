from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.api import experiments_run
from app.api.experiments_run import _persist_experiment_run
from app.db.database import get_database


def test_experiment_history_keeps_only_ten_newest_runs():
    database = get_database()
    now = datetime.now(timezone.utc)

    for index in range(12):
        _persist_experiment_run(
            database,
            {
                "experiment_id": f"run_{index}",
                "config": {},
                "metrics": {},
                "attack_evidence": {},
                "created_at": now + timedelta(seconds=index),
            },
        )

    history = list(
        database["experiment_runs"].find().sort("created_at", -1)
    )
    assert len(history) == 10
    assert [row["experiment_id"] for row in history] == [
        f"run_{index}" for index in range(11, 1, -1)
    ]


def test_repeated_identical_runs_are_saved_separately(client, monkeypatch):
    def fake_run(config, verifier_factory):
        return SimpleNamespace(
            config=SimpleNamespace(attack_type=config.attack_type),
            to_dict=lambda: {
                "config": config.to_dict(),
                "metrics": {"detection_rate": 0.5},
                "attack_evidence": {},
            },
        )

    monkeypatch.setattr(experiments_run, "run_attack_experiment", fake_run)
    payload = {
        "attack_type": "forgery",
        "parameters": {},
        "n_targets": 1,
        "seed": 42,
        "rounds": 1,
        "natural_error_rate": 0.01,
    }

    first = client.post("/api/experiments/run", json=payload)
    second = client.post("/api/experiments/run", json=payload)

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["experiment_id"] != second.json()["experiment_id"]
    history = client.get("/api/experiments")
    assert history.status_code == 200
    assert len(history.json()) == 2