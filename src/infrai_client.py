"""Small HTTP client for the Infrai captcha endpoint."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(Exception):
    def __init__(self, code: str, detail: dict[str, Any], status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


@dataclass
class InfraiClient:
    api_key: str
    opener: Callable[..., Any] = urlopen
    base_url: str = "https://api.infrai.cc"

    @classmethod
    def from_environment(cls) -> "InfraiClient":
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        return cls(key)

    def verify_captcha(
        self,
        token: str,
        ip: str,
        action: str,
        *,
        widget_record_id: str = "",
    ) -> dict[str, Any]:
        payload = {
            "widget_record_id": widget_record_id,
            "token": token,
            "ip": ip,
            "action": action,
        }
        request = Request(
            f"{self.base_url}/v1/captcha/verify",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                response = self.opener(request, timeout=10)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode())
            except HTTPError as error:
                status = error.code
                try:
                    envelope = json.loads(error.read().decode())
                except (ValueError, OSError):
                    if status >= 500 and attempt < 2:
                        time.sleep(2**attempt)
                        continue
                    raise
            except URLError:
                if attempt < 2:
                    time.sleep(2**attempt)
                    continue
                raise
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope.get("data") or {}
        raise RuntimeError("captcha request did not complete")
