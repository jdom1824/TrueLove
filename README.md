# True Love

True Love is an experimental crypto-art project about an impossible search: a public network of people and machines keeping a signal alive around the 31 random Ethereum addresses associated with Dmitri Cherniak's *Dead Ringers*.

```text
coordinator/     Raspberry Pi coordinator for the MVP
worker/          Search engine boundary and client
targets/         Public target addresses and sandbox test targets
tests/           Protocol and sandbox integration tests
docs/            Architecture, protocol and operations
```

## Current MVP direction

- The Raspberry Pi is the coordinator, not the mining device.
- Workers may run in a browser, desktop app, mobile app or another physical node.
- Jobs, heartbeats and proofs are public protocol events.
- The public landing is maintained in a separate project/repository.
- Cloudflare Tunnel will expose the coordinator without exposing the Raspberry Pi directly.
- SQLite is the first coordinator database; the protocol is designed to migrate to Radxa or a larger server.
- The system never asks participants for private keys or seed phrases.

## Search engines

The worker supports three pluggable engines via `--engine`:

| Engine     | Description                                            |
|------------|--------------------------------------------------------|
| `demo`     | Deterministic hash exercise. Safe, no wallets.         |
| `sandbox`  | Test wallet with coordinator integration. For local dev. |
| `user`     | Locked interface for a future authorized implementation. |

### Sandbox engine

The sandbox engine scans 31 deterministic test wallets from `targets/sandbox_wallets.json`. Their keys are public test fixtures with no value; they are never logged or transmitted.

```bash
pip install -r requirements-sandbox.txt
```

Run the client with the sandbox engine:

```bash
PYTHONPATH=. python3 -m worker.client --engine sandbox --target-id 1 --range-start 0 --range-end 199
```

### Connecting an authorized algorithm

To connect a new search algorithm:

1. Create a class inheriting from `SearchEngine` in `worker/search_engine.py`.
2. Implement the `search` method returning a `SearchResult`.
3. Register it in `worker/client.py` by adding a new `--engine` choice.
4. Never persist or transmit private keys; return only public match data.

## Run the coordinator locally

```bash
python3 -m coordinator
```

The coordinator defaults to `http://127.0.0.1:8787` and creates its SQLite database under `coordinator/data/`.

## Run tests

```bash
# Compile check
python3 -m py_compile coordinator/server.py worker/*.py tests/test_protocol.py tests/test_sandbox.py

# Run all tests
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Coordinator MVP](coordinator/README.md)

The former landing and prototype API remain only as local historical material and are intentionally excluded from this repository. The public codebase is reserved for the coordinator, workers, protocol and operational tooling.
