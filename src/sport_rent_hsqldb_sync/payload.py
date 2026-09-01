from sport_rent_hsqldb_sync.models import HsqldbReservation


def build_sync_payload(
    reservations: dict[int, HsqldbReservation],
) -> dict[str, list[dict[str, object]]]:
    payload_reservations: list[dict[str, object]] = []

    for source_position_id in sorted(reservations):
        reservation = reservations[source_position_id]
        if reservation.item is None:
            source_name = None
            product_name = None
            inventory_code = None
        else:
            source_name = reservation.item.source_name
            product_name = reservation.item.product_name
            inventory_code = reservation.item.inventory_code
        payload_reservations.append(
            {
                "source_position_id": reservation.source_position_id,
                "begin_at": (
                    reservation.begin_at.isoformat()
                    if reservation.begin_at is not None
                    else None
                ),
                "end_at": (
                    reservation.end_at.isoformat()
                    if reservation.end_at is not None
                    else None
                ),
                "source_rent_object_id": reservation.source_rent_object_id,
                "source_status": reservation.source_status,
                "source_name": source_name,
                "product_name": product_name,
                "inventory_code": inventory_code,
            }
        )
    return {"reservations": payload_reservations}
