import argparse
from pathlib import Path

from sport_rent_hsqldb_sync.api import send_sync_payload
from sport_rent_hsqldb_sync.payload import build_sync_payload
from sport_rent_hsqldb_sync.reservations import build_reservations
from sport_rent_hsqldb_sync.snapshot import load_consistent_snapshot


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize HSQLDB reservations")
    parser.add_argument(
        "--database-path",
        required=True,
        type=Path,
        help="Path to the HSQLDB database without an extension",
    )
    parser.add_argument(
        "--backend-url",
        required=True,
        help="Backend synchronization endpoint URL",
    )
    return parser.parse_args()


def run_sync_once(database_path: Path, backend_url: str) -> None:
    database_state = load_consistent_snapshot(database_path)
    reservations = build_reservations(database_state)
    payload = build_sync_payload(reservations)

    send_sync_payload(backend_url, payload)

    print(f"Sent {len(reservations)} reservations")


def main() -> None:
    arguments = parse_arguments()
    run_sync_once(arguments.database_path, arguments.backend_url)
