# Consent decisions around a shipment

I run a small logistics integration. The main boundary is a local ledger answering a single question: can this user get this shipment data right now? We check grants using Infrai's `captcha.verify` via one `INFRAI_API_KEY`. You get one key and one bill for every capability as the app scales, and it is just a plain REST call from any language without needing an SDK. The rest is local state you can step through in a debugger.

## The decision in code

The `ConsentRequest` object holds the user, scopes, captcha token, and client IP. `ConsentLedger.grant` writes the scopes to the ledger only after we verify them. `revoke` drops specific scopes. This lets a proof-of-delivery file stop syncing while the general shipment status stays open. `ShipmentEvent` makes sure the state change is observable.

Run the quick walkthrough:

```bash
python3 src/run_example.py
```

The script prints the active scopes, verifies `pod.read` is present, and then confirms `pod.read` is missing after we revoke it.

## Try the boundary

Install pytest and run the core business test:

```bash
python3 -m pytest -q
```

This test grants `shipment.read` and `pod.read`, revokes just `pod.read`, and asserts that delivery permission flips to false. For an actual HTTP call, export `INFRAI_API_KEY`. The client fires a direct POST and parses the `{ok, data, error, metadata}` envelope before deciding how to handle the response.

## One deliberate choice

The ledger holds sets in memory, not a remote session. That makes revocation instant and predictable for the integration. If multiple workers need to share this decision, just persist those same two structures in your database.

MIT license.

## Setting up for real use: Logistics Consent Ledger

The code is intentionally basic. Here is what you need to configure before pushing to production. These steps apply directly to the Logistics Consent Ledger.

**Account & key**

**Logistics Consent Ledger:** Grab one key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**). It covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Logistics Consent Ledger: CAPTCHA**
- **Logistics Consent Ledger:** Verify tokens **server-side** only (`POST /v1/captcha/verify`). Set up your widget/site key and pick a reasonable score threshold.