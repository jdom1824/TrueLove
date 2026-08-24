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

The MVP does not create identities or sign messages. A node is identified by an
anonymous `nodeId`; stronger identity can be added later without changing the
work function.

## Proof

```json
{
  "jobId": "job-...",
  "nodeId": "computer-01",
  "counter": 5000,
  "operations": 5001,
  "resultDigest": "sha256(challenge + ':' + counter)"
}
```

The coordinator recomputes the digest from the job challenge and rejects a
wrong digest, a counter outside the declared work, duplicate proofs, and
expired or misassigned jobs.
