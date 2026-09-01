import json
from collections.abc import Mapping
from urllib.request import Request, urlopen


def send_sync_payload(
    backend_url: str,
    payload: Mapping[str, object],
    timeout_seconds: float = 10.0,
) -> None:
    encoded_payload = json.dumps(payload).encode("utf-8")

    request = Request(
        backend_url,
        data=encoded_payload,
        headers={
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )

    with urlopen(request, timeout=timeout_seconds):
        pass
