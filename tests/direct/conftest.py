"""Shared helpers for direct mode tests."""


def to_hex(addr_bytes):
    """Convert address bytes to checksummed hex matching contract output.

    The contract's get_bets()/get_points() return keys via Address.as_hex,
    which produces EIP-55 checksummed hex. Call after direct_deploy so the
    SDK is on sys.path.
    """
    if hasattr(addr_bytes, "as_hex"):
        return addr_bytes.as_hex
    from genlayer.types import Address

    return Address(addr_bytes).as_hex


# Compatibility shim for genlayer-test 0.30.0rc2 + GenVM v0.6.
# The direct-mode LLM mock currently JSON-decodes mock responses too early,
# while the current GenLayer runtime expects response_format="json" data
# to arrive as text and performs json.loads itself.
import gltest.direct.wasi_mock as _wasi_mock


def _bluff_handle_llm_request(vm, data):
    prompt = data.get("prompt", "")
    response = vm._match_llm_mock(prompt)

    if response is not None:
        return {"ok": response}

    return _original_handle_llm_request(vm, data)


_original_handle_llm_request = _wasi_mock._handle_llm_request
_wasi_mock._handle_llm_request = _bluff_handle_llm_request
