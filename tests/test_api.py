import json
from types import TracebackType
from typing import Self
from urllib.request import Request

import pytest

from sport_rent_hsqldb_sync.api import send_sync_payload


class FakeResponse:
    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


def test_sends_payload_as_json_post(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("sport_rent_hsqldb_sync.api.urlopen", fake_urlopen)
    payload = {
        "reservations": [
            {
                "source_position_id": 1001,
                "product_name": "Uprząż wspinaczkowa",
            }
        ]
    }

    send_sync_payload(
        "http://127.0.0.1:8000/sync/reservations",
        payload,
        timeout_seconds=5.0,
    )

    request = captured["request"]
    assert isinstance(request, Request)
    assert request.full_url == "http://127.0.0.1:8000/sync/reservations"
    assert request.get_method() == "POST"
    assert request.get_header("Content-type") == "application/json; charset=utf-8"
    assert request.data is not None
    assert json.loads(request.data.decode("utf-8")) == payload
    assert captured["timeout"] == 5.0
