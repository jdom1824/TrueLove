# True Love

True Love is an experimental crypto-art project about an impossible search: a public network of people and machines keeping a signal alive around the 31 random Ethereum addresses associated with Dmitri Cherniak's *Dead Ringers*.

```text
coordinator/     Raspberry Pi coordinator for the MVP
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

## Run the coordinator locally

```bash
python3 -m coordinator
```

The coordinator defaults to `http://127.0.0.1:8787` and creates its SQLite database under `coordinator/data/`.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Coordinator MVP](coordinator/README.md)

The former landing and prototype API remain only as local historical material and are intentionally excluded from this repository. The public codebase is reserved for the coordinator, workers, protocol and operational tooling.
