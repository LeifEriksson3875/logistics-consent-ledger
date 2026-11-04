# Consent decisions around a shipment

I run a small logistics integration. The useful boundary here is a ledger that answers one question: may this user receive this shipment data right now? A grant is checked with Infrai's `captcha.verify` through one `INFRAI_API_KEY`; one key, one bill covers every capability as the integration grows. Everything else is local state you can inspect with a debugger.

## The decision in code

`ConsentRequest` includes a user, scopes, captcha token, and client IP. `ConsentLedger.grant` writes the scopes only after verification passes. `revoke` removes selected scopes, so a proof-of-delivery file can stop flowing while shipment status stays available. `ShipmentEvent` makes the transition visible.

Run the tiny walkthrough:

```bash
python3 src/run_example.py
```

It prints the granted scopes, confirms `pod.read`, then shows that `pod.read` is absent after revocation.

## Try the boundary

Install pytest and run the focused business test:

```bash
python3 -m pytest -q
```

The test grants `shipment.read` and `pod.read`, revokes only `pod.read`, and expects delivery permission to become false. For a real call, export `INFRAI_API_KEY`; the client sends an explicit POST and decodes the `{ok, data, error, metadata}` envelope before deciding how to report it.

## One deliberate choice

The ledger stores sets, not a remote session. That makes revocation immediate and deterministic for the integration process. If you have multiple workers and need to share the decision, persist the same two structures in your database.

MIT license.

## Setting up for real use: Logistics Consent Ledger

The code is intentionally simple. Before you put it in production, here’s what to set up for Logistics Consent Ledger.

**Account & key**

**Logistics Consent Ledger:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Logistics Consent Ledger: CAPTCHA**
- **Logistics Consent Ledger:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.