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

SANDBOX_TARGETS_PATH = Path(__file__).parent.parent / "targets" / "sandbox_targets.json"

# Deterministic seed for the sandbox test wallet.
# This is a PUBLIC constant used ONLY for reproducible sandbox testing.
# The derived private key is never stored, logged, or transmitted.
_SANDBOX_SEED = b"truelove-sandbox-test-target-2024"
_SANDBOX_SALT = b"truelove-sandbox"
_SANDBOX_KDF_ITERATIONS = 100_000


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


def _load_sandbox_targets() -> list[str]:
    if not SANDBOX_TARGETS_PATH.exists():
        return []
    data = json.loads(SANDBOX_TARGETS_PATH.read_text())
    return [t["address"].lower() for t in data.get("targets", [])]


def _derive_sandbox_address() -> str:
    """Derive the sandbox test wallet address from the deterministic seed.

    The private key exists only ephemerally during derivation and is never
    stored, logged, printed, or transmitted.
    """
    key_bytes = hashlib.pbkdf2_hmac(
        "sha256", _SANDBOX_SEED, _SANDBOX_SALT, _SANDBOX_KDF_ITERATIONS
    )
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

    - Uses a fixed seed to derive a test wallet address.
    - The private key is derived ephemerally and never stored.
    - Compares the derived address against sandbox_targets.json.
    - Produces valid proof digests compatible with the coordinator.
    """

    def __init__(self) -> None:
        self._sandbox_address = _derive_sandbox_address()
        self._sandbox_targets = _load_sandbox_targets()

    @property
    def address(self) -> str:
        """Public address of the sandbox test wallet (read-only)."""
        return self._sandbox_address

    def search(self, challenge: str, start: int, end: int) -> SearchResult:
        if start < 0 or end < start:
            raise ValueError("invalid search range")
        operations = end - start + 1
        digest = hashlib.sha256(f"{challenge}:{start}:{end}:{operations}".encode()).hexdigest()
        match_address: str | None = None
        if self._sandbox_address.lower() in self._sandbox_targets:
            match_address = self._sandbox_address
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
