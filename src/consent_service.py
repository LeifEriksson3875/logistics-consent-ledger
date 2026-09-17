from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from infrai_client import InfraiClient, InfraiError


@dataclass(frozen=True)
class ShipmentEvent:
    shipment_id: str
    kind: str
    occurred_at: datetime
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConsentRequest:
    user_id: str
    scopes: tuple[str, ...]
    captcha_token: str
    client_ip: str


@dataclass
class ConsentLedger:
    grants: dict[str, set[str]] = field(default_factory=dict)
    events: list[ShipmentEvent] = field(default_factory=list)

    def grant(self, request: ConsentRequest, client: InfraiClient) -> set[str]:
        try:
            client.verify_captcha(request.captcha_token, request.client_ip, "consent_grant")
        except InfraiError as error:
            if 400 <= error.status < 500:
                raise ValueError(f"captcha rejected: {error.code}") from error
            raise
        current = self.grants.setdefault(request.user_id, set())
        current.update(request.scopes)
        self.events.append(ShipmentEvent(request.user_id, "consent_granted", datetime.now(timezone.utc), {"scopes": sorted(current)}))
        return set(current)

    def revoke(self, user_id: str, scopes: tuple[str, ...]) -> set[str]:
        current = self.grants.setdefault(user_id, set())
        current.difference_update(scopes)
        self.events.append(ShipmentEvent(user_id, "consent_revoked", datetime.now(timezone.utc), {"scopes": list(scopes)}))
        return set(current)

    def can_deliver(self, user_id: str, scope: str) -> bool:
        return scope in self.grants.get(user_id, set())
