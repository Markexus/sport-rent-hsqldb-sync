from datetime import datetime

from sport_rent_hsqldb_sync.models import (
    HsqldbItemIdentity,
    HsqldbReservation,
)
from sport_rent_hsqldb_sync.payload import build_sync_payload


def test_builds_payload_for_reservation_with_identified_item() -> None:
    reservations = {
        1001: HsqldbReservation(
            source_position_id=1001,
            begin_at=datetime.fromisoformat("2026-09-01T10:00:00"),
            end_at=datetime.fromisoformat("2026-09-05T18:00:00"),
            source_rent_object_id=3001,
            source_status=1,
            item=HsqldbItemIdentity(
                source_name="Kije Dynafit/004",
                product_name="Kije Dynafit",
                inventory_code="004",
            ),
        )
    }

    payload = build_sync_payload(reservations)

    assert payload == {
        "reservations": [
            {
                "source_position_id": 1001,
                "begin_at": "2026-09-01T10:00:00",
                "end_at": "2026-09-05T18:00:00",
                "source_rent_object_id": 3001,
                "source_status": 1,
                "source_name": "Kije Dynafit/004",
                "product_name": "Kije Dynafit",
                "inventory_code": "004",
            }
        ]
    }


def test_builds_payload_when_dates_and_item_are_missing() -> None:
    reservations = {
        1002: HsqldbReservation(
            source_position_id=1002,
            begin_at=None,
            end_at=None,
            source_rent_object_id=None,
            source_status=0,
            item=None,
        )
    }

    payload = build_sync_payload(reservations)

    assert payload == {
        "reservations": [
            {
                "source_position_id": 1002,
                "begin_at": None,
                "end_at": None,
                "source_rent_object_id": None,
                "source_status": 0,
                "source_name": None,
                "product_name": None,
                "inventory_code": None,
            }
        ]
    }


def test_sorts_payload_reservations_by_source_position_id() -> None:
    reservations = {
        source_position_id: HsqldbReservation(
            source_position_id=source_position_id,
            begin_at=None,
            end_at=None,
            source_rent_object_id=None,
            source_status=1,
            item=None,
        )
        for source_position_id in (1002, 1001)
    }

    payload = build_sync_payload(reservations)

    assert [
        reservation["source_position_id"] for reservation in payload["reservations"]
    ] == [1001, 1002]


def test_builds_empty_payload() -> None:
    assert build_sync_payload({}) == {"reservations": []}
