from sport_rent_hsqldb_sync.models import HsqldbReservationPosition
from sport_rent_hsqldb_sync.parsing.values import (
    parse_optional_int,
    parse_timestamp,
    split_insert_values,
)

RESERVATION_POSITION_INSERT_PREFIX = "INSERT INTO RESERVATIONPOSITION VALUES("
RESERVATION_POSITION_DELETE_PREFIX = "DELETE FROM RESERVATIONPOSITION WHERE ID="
RESERVATION_POSITION_STATEMENT_PREFIXES = (
    RESERVATION_POSITION_INSERT_PREFIX,
    RESERVATION_POSITION_DELETE_PREFIX,
)


def parse_reservation_position_insert(
    statement: str,
) -> HsqldbReservationPosition:
    values = split_insert_values(statement, RESERVATION_POSITION_INSERT_PREFIX)
    return HsqldbReservationPosition(
        source_position_id=int(values[0]),
        begin_at=parse_timestamp(values[1]),
        end_at=parse_timestamp(values[2]),
        source_rent_object_id=parse_optional_int(values[4]),
        source_status=parse_optional_int(values[14]),
    )


def parse_reservation_position_delete(statement: str) -> int:
    source_position_id = statement.removeprefix(
        RESERVATION_POSITION_DELETE_PREFIX
    ).removesuffix(";")
    return int(source_position_id)
