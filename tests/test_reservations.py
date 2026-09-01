from datetime import UTC, datetime

from sport_rent_hsqldb_sync.models import (
    HsqldbAbstractPosition,
    HsqldbDatabaseState,
    HsqldbItemIdentity,
    HsqldbReservation,
    HsqldbReservationPosition,
)
from sport_rent_hsqldb_sync.reservations import build_reservations

BEGIN_AT = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)
END_AT = datetime(2026, 9, 5, 18, 0, tzinfo=UTC)


def test_builds_reservation_from_matching_positions() -> None:
    database_state = HsqldbDatabaseState(
        reservation_positions={
            1001: HsqldbReservationPosition(
                source_position_id=1001,
                begin_at=BEGIN_AT,
                end_at=END_AT,
                source_rent_object_id=3001,
                source_status=1,
            )
        },
        abstract_positions={
            1001: HsqldbAbstractPosition(
                source_position_id=1001,
                source_name="Kije Dynafit/004",
            )
        },
    )

    reservations = build_reservations(database_state)

    assert reservations == {
        1001: HsqldbReservation(
            source_position_id=1001,
            begin_at=BEGIN_AT,
            end_at=END_AT,
            source_rent_object_id=3001,
            source_status=1,
            item=HsqldbItemIdentity(
                source_name="Kije Dynafit/004",
                product_name="Kije Dynafit",
                inventory_code="004",
            ),
        )
    }


def test_keeps_reservation_when_abstract_position_is_missing() -> None:
    database_state = HsqldbDatabaseState(
        reservation_positions={
            1001: HsqldbReservationPosition(
                source_position_id=1001,
                begin_at=BEGIN_AT,
                end_at=END_AT,
                source_rent_object_id=3001,
                source_status=1,
            )
        },
        abstract_positions={},
    )

    reservations = build_reservations(database_state)

    assert reservations[1001].item is None


def test_keeps_reservation_when_source_name_is_null() -> None:
    database_state = HsqldbDatabaseState(
        reservation_positions={
            1001: HsqldbReservationPosition(
                source_position_id=1001,
                begin_at=BEGIN_AT,
                end_at=END_AT,
                source_rent_object_id=None,
                source_status=0,
            )
        },
        abstract_positions={
            1001: HsqldbAbstractPosition(
                source_position_id=1001,
                source_name=None,
            )
        },
    )

    reservations = build_reservations(database_state)

    assert reservations[1001].item is None


def test_ignores_abstract_position_without_reservation_position() -> None:
    database_state = HsqldbDatabaseState(
        reservation_positions={},
        abstract_positions={
            1001: HsqldbAbstractPosition(
                source_position_id=1001,
                source_name="Kije Dynafit/004",
            )
        },
    )

    reservations = build_reservations(database_state)

    assert reservations == {}
