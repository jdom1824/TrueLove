# True Love

True Love is an experimental crypto-art project about an impossible search: a public network of people and machines keeping a signal alive around the 31 random Ethereum addresses associated with Dmitri Cherniak's *Dead Ringers*.

```text
dashboard/       Public bilingual landing + scan UI
coordinator/     Raspberry Pi coordinator for the MVP
docs/            Architecture, protocol and operations
Api/             Legacy prototype; not used by the new system
```

## Current MVP direction

- The Raspberry Pi is the coordinator, not the mining device.
- Workers may run in a browser, desktop app, mobile app or another physical node.
- Jobs, heartbeats and proofs are public protocol events.
- Firebase Hosting serves the web frontend.
- Cloudflare Tunnel will expose the coordinator without exposing the Raspberry Pi directly.
- SQLite is the first coordinator database; the protocol is designed to migrate to Radxa or a larger server.
- The system never asks participants for private keys or seed phrases.

## Run the landing locally

```bash
cd dashboard
npm install
npm start
```

Build and deploy the current frontend:

```bash
cd dashboard
npm run build
firebase deploy --only hosting
```

## Run the coordinator locally

```bash
python3 -m coordinator
```

The coordinator defaults to `http://127.0.0.1:8787` and creates its SQLite database under `coordinator/data/`.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Coordinator MVP](coordinator/README.md)

## Legacy code

The original `Api/` prototype is retained only as historical material. It must not be used in production: it generates and stores private keys and does not implement the new public proof-of-work protocol.
