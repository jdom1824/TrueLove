# Worker integration

The worker talks to the coordinator through `client.py` and receives a range
for each job. The default `DemoSearchEngine` validates the complete client-
server flow without generating wallets.

The algorithm boundary is `UserSearchEngine.search()` in
`worker/search_engine.py`. It is intentionally disabled until an authorized
implementation is supplied. The engine must return public result data only;
the worker must never log or persist private material.

Run the safe integration client:

```bash
python3 -m worker.client --target-id 17 --range-start 0 --range-end 199
```

To call the user algorithm boundary instead:

```bash
python3 -m worker.client --engine user --target-id 17 --range-start 100 --range-end 109
```

This mode intentionally stops with `UserSearchEngine is not configured` until
the implementation of `search()` is supplied.
