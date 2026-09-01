from pathlib import Path

import pytest

import sport_rent_hsqldb_sync.main as main_module
from sport_rent_hsqldb_sync.models import HsqldbDatabaseState


def test_run_sync_once_builds_and_sends_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_path = Path("rental-data/rental")
    backend_url = "http://127.0.0.1:8000/sync/reservations"
    database_state = HsqldbDatabaseState(
        reservation_positions={},
        abstract_positions={},
    )
    reservations = {}
    payload = {"reservations": []}
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        main_module,
        "load_consistent_snapshot",
        lambda received_path: (
            captured.update(database_path=received_path) or database_state
        ),
    )
    monkeypatch.setattr(
        main_module,
        "build_reservations",
        lambda received_state: (
            captured.update(database_state=received_state) or reservations
        ),
    )
    monkeypatch.setattr(
        main_module,
        "build_sync_payload",
        lambda received_reservations: (
            captured.update(reservations=received_reservations) or payload
        ),
        raising=False,
    )
    monkeypatch.setattr(
        main_module,
        "send_sync_payload",
        lambda received_url, received_payload: captured.update(
            backend_url=received_url,
            payload=received_payload,
        ),
        raising=False,
    )

    main_module.run_sync_once(database_path, backend_url)

    assert captured == {
        "database_path": database_path,
        "database_state": database_state,
        "reservations": reservations,
        "backend_url": backend_url,
        "payload": payload,
    }
