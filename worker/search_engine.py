"""Search engine boundary.

The coordinator and worker protocol are independent from the search algorithm.
The default engine is safe deterministic demo work. Replace only
``UserSearchEngine.search`` with an authorized implementation; it must return
public results and must never persist or print private material.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

SANDBOX_WALLETS_PATH = Path(__file__).parent.parent / "targets" / "sandbox_wallets.json"

@dataclass(frozen=True)
class SearchResult:
    operations: int
    cursor: int
    result_digest: str
    match_address: str | None = None


class SearchEngine:
    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        raise NotImplementedError


class DemoSearchEngine(SearchEngine):
    """Safe engine used for client-server tests; it does not generate wallets."""

    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        if start < 0 or end < start:
            raise ValueError("invalid search range")
        operations = end - start + 1
        digest = hashlib.sha256(f"{challenge}:{start}:{end}:{operations}".encode()).hexdigest()
        return SearchResult(operations, end, digest)


def _load_sandbox_wallets() -> dict[int, dict[str, str]]:
    if not SANDBOX_WALLETS_PATH.exists():
        return []
    data = json.loads(SANDBOX_WALLETS_PATH.read_text())
    return {int(t["candidateIndex"]): t for t in data.get("targets", [])}


def _derive_sandbox_address() -> str:
    """Derive the sandbox test wallet address from the deterministic seed.

    The private key exists only ephemerally during derivation and is never
    stored, logged, printed, or transmitted.
    """
    wallets = _load_sandbox_wallets()
    key_bytes = bytes.fromhex(wallets[min(wallets)]["privateKey"][2:])
    try:
        from eth_account import Account
        account = Account.from_key(key_bytes)
        return account.address
    except ImportError:
        raise ImportError(
            "eth_account is required for SandboxSearchEngine. "
            "Install it with: pip install eth_account"
        )


class SandboxSearchEngine(SearchEngine):
    """Controlled sandbox engine with a deterministic test wallet.

    - Uses a public fixture containing 31 valueless test wallets.
    - Scans candidate indexes in the assigned range.
    - The private key is read ephemerally and never sent or logged.
    - Produces valid proof digests compatible with the coordinator.
    """

    def __init__(self) -> None:
        self._sandbox_address = _derive_sandbox_address()
        self._sandbox_wallets = _load_sandbox_wallets()

    @property
    def address(self) -> str:
        """Public address of the sandbox test wallet (read-only)."""
        return self._sandbox_address

    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        if start < 0 or end < start:
            raise ValueError("invalid search range")
        operations = end - start + 1
        match_address: str | None = None
        for candidate in range(start, end + 1):
            fixture = self._sandbox_wallets.get(candidate)
            if fixture is not None:
                try:
                    from eth_account import Account
                    address = Account.from_key(bytes.fromhex(fixture["privateKey"][2:])).address
                except ImportError as error:
                    raise ImportError("eth_account is required for SandboxSearchEngine") from error
                if address.lower() == fixture["address"].lower():
                    match_address = address
        digest = hashlib.sha256(f"{challenge}:{start}:{end}:{operations}".encode()).hexdigest()
        return SearchResult(operations, end, digest, match_address)


class UserSearchEngine(SearchEngine):
    """Locked interface for a future authorized implementation.

    This method intentionally fails closed until the implementation is supplied.
    Keep candidate secrets local and ephemeral; return only public match data.

    To connect an authorized algorithm:
      1. Create a new class that inherits from SearchEngine.
      2. Implement the ``search`` method returning a ``SearchResult``.
      3. Register it in worker/client.py by adding a new ``--engine`` choice.
    """

    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        raise NotImplementedError(
            "UserSearchEngine is not configured. "
            "See worker/search_engine.py for instructions on how to connect "
            "an authorized algorithm."
        )
