from consent_service import ConsentLedger, ConsentRequest


class CaptchaOK:
    def __init__(self):
        self.calls = []

    def verify_captcha(self, token, ip, action):
        self.calls.append((token, ip, action))
        return {"verified": True}


def test_revoke_removes_only_selected_scope():
    client = CaptchaOK()
    ledger = ConsentLedger()
    request = ConsentRequest("u1", ("shipment.read", "pod.read"), "token", "127.0.0.1")
    assert ledger.grant(request, client) == {"shipment.read", "pod.read"}
    assert ledger.revoke("u1", ("pod.read",)) == {"shipment.read"}
    assert ledger.can_deliver("u1", "pod.read") is False
    assert client.calls == [("token", "127.0.0.1", "consent_grant")]
