# True Love Scan Coordinator

This is the dependency-free coordinator MVP intended to run on the Raspberry Pi 3 and later migrate to Radxa without changing the worker protocol.

## Run

From the repository root:

```bash
python3 -m coordinator
```

The default address is `http://127.0.0.1:8787`.

## Environment

```text
TRUELOVE_HOST=127.0.0.1
TRUELOVE_PORT=8787
TRUELOVE_DB=./data/scan.db
TRUELOVE_ALGORITHM=truelove-v0.1.0
```

## Endpoints

```text
GET  /health
GET  /api/status
POST /api/heartbeat
POST /api/jobs/claim
POST /api/proofs
```

The current proof handler validates job ownership, expiry, duplicate submission, payload shape and the reproducible digest defined in `docs/PROTOCOL.md`. This MVP intentionally does not generate or receive private keys.
