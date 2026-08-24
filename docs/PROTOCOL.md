# True Love Scan protocol v0.1

This first protocol is intentionally small. It proves that a worker can receive
work, report liveness, and submit a reproducible result without sending private
keys, seed phrases, or wallet secrets.

## Flow

```text
worker -> POST /api/heartbeat
worker -> POST /api/jobs/claim
worker -> local deterministic work
worker -> POST /api/proofs
```

The current work function is a safe test function: it hashes the coordinator's
challenge with a counter. It is not the real wallet-search algorithm.

The worker creates a separate Ed25519 identity key for this test. It publishes
the public key in the heartbeat and signs the proof payload. This identity key
is unrelated to Ethereum wallets and is never used to search for or control
funds.

## Proof

```json
{
  "jobId": "job-...",
  "nodeId": "computer-01",
  "counter": 5000,
  "operations": 5001,
  "resultDigest": "sha256(challenge + ':' + counter)"
  ,"signature": "base64(ed25519-signature)"
}
```

The coordinator recomputes the digest from the job challenge and rejects a
wrong digest, a counter outside the declared work, duplicate proofs, and
expired or misassigned jobs.
