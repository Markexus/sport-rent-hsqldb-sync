from sport_rent_hsqldb_sync.item_identity import extract_item_identity
from sport_rent_hsqldb_sync.models import (
    HsqldbDatabaseState,
    HsqldbReservation,
)


def build_reservations(
    database_state: HsqldbDatabaseState,
) -> dict[int, HsqldbReservation]:

    reservations: dict[int, HsqldbReservation] = {}
    for (
        source_position_id,
        reservation_position,
    ) in database_state.reservation_positions.items():
        abstract_position = database_state.abstract_positions.get(source_position_id)

        if abstract_position is None or abstract_position.source_name is None:
            item = None
        else:
            item = extract_item_identity(abstract_position.source_name)
        reservations[source_position_id] = HsqldbReservation(
            source_position_id=source_position_id,
            begin_at=reservation_position.begin_at,
            end_at=reservation_position.end_at,
            source_rent_object_id=reservation_position.source_rent_object_id,
            source_status=reservation_position.source_status,
            item=item,
        )
    return reservations
