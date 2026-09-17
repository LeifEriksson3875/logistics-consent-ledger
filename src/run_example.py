from datetime import datetime, timezone

from consent_service import ConsentLedger, ConsentRequest, ShipmentEvent


class DemoCaptcha:
    def verify_captcha(self, token: str, ip: str, action: str) -> dict[str, bool]:
        return {"verified": bool(token and ip and action)}


def main() -> None:
    ledger = ConsentLedger()
    request = ConsentRequest("user-42", ("shipment.read", "pod.read"), "demo-token", "203.0.113.10")
    print("granted:", sorted(ledger.grant(request, DemoCaptcha())))
    ledger.events.append(ShipmentEvent("ship-100", "delivered", datetime.now(timezone.utc), {"pod": "available"}))
    print("pod allowed:", ledger.can_deliver("user-42", "pod.read"))
    print("after revoke:", sorted(ledger.revoke("user-42", ("pod.read",))))


if __name__ == "__main__":
    main()
