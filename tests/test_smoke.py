"""
Smoke tests for validating tiktoken ARM64 wheels.

These tests verify that a tiktoken installation works correctly on the
current platform. Run with:
    pytest tests/test_smoke.py -v
"""

import platform
import sys

import pytest


@pytest.fixture(scope="session")
def tiktoken():
    """Import and return tiktoken, skipping if not installed."""
    try:
        import tiktoken
        return tiktoken
    except ImportError:
        pytest.skip("tiktoken not installed")


@pytest.fixture(scope="session")
def cl100k(tiktoken):
    """Get the cl100k_base encoding."""
    return tiktoken.get_encoding("cl100k_base")


class TestBasicFunctionality:
    """Core encoding/decoding tests."""

    def test_import(self, tiktoken):
        assert hasattr(tiktoken, "get_encoding")
        assert hasattr(tiktoken, "encoding_for_model")

    def test_version_attribute(self, tiktoken):
        version = getattr(tiktoken, "__version__", None)
        # __version__ was added in v0.8.0
        if version:
            assert isinstance(version, str)

    def test_get_encoding_cl100k(self, cl100k):
        assert cl100k.name == "cl100k_base"

    def test_get_encoding_p50k(self, tiktoken):
        enc = tiktoken.get_encoding("p50k_base")
        assert enc.name == "p50k_base"

    def test_get_encoding_r50k(self, tiktoken):
        enc = tiktoken.get_encoding("r50k_base")
        assert enc.name == "r50k_base"

    def test_encoding_for_model_gpt4(self, tiktoken):
        enc = tiktoken.encoding_for_model("gpt-4")
        assert enc.name == "cl100k_base"


class TestEncodeDecode:
    """Encode and decode roundtrip tests."""

    def test_hello_world_known_tokens(self, cl100k):
        tokens = cl100k.encode("hello world")
        assert tokens == [15339, 1917]

    def test_roundtrip_ascii(self, cl100k):
        text = "The quick brown fox jumps over the lazy dog."
        assert cl100k.decode(cl100k.encode(text)) == text

    def test_roundtrip_empty(self, cl100k):
        assert cl100k.encode("") == []
        assert cl100k.decode([]) == ""

    def test_roundtrip_whitespace(self, cl100k):
        text = "  hello  \n  world  \t  "
        assert cl100k.decode(cl100k.encode(text)) == text

    def test_roundtrip_long_text(self, cl100k):
        text = "Hello world! " * 1000
        assert cl100k.decode(cl100k.encode(text)) == text

    @pytest.mark.parametrize(
        "text",
        [
            "こんにちは世界",          # Japanese
            "مرحبا بالعالم",          # Arabic
            "Привет мир",             # Russian
            "🎉🚀✨🌍",               # Emoji
            "Héllo wörld café",       # Accented Latin
            "中文测试",                # Chinese
            "한국어 테스트",           # Korean
        ],
        ids=["japanese", "arabic", "russian", "emoji", "accented", "chinese", "korean"],
    )
    def test_roundtrip_unicode(self, cl100k, text):
        assert cl100k.decode(cl100k.encode(text)) == text


class TestEdgeCases:
    """Edge case and robustness tests."""

    def test_single_character(self, cl100k):
        for char in "abcABC123!@#":
            tokens = cl100k.encode(char)
            assert len(tokens) >= 1
            assert cl100k.decode(tokens) == char

    def test_newlines(self, cl100k):
        text = "line1\nline2\r\nline3"
        assert cl100k.decode(cl100k.encode(text)) == text

    def test_special_characters(self, cl100k):
        text = "Hello <|endoftext|> World"
        # With no special tokens allowed, this should encode as normal text
        tokens = cl100k.encode(text, disallowed_special=())
        assert len(tokens) > 0


class TestPlatformInfo:
    """Not really tests — just report platform info for debugging CI."""

    def test_report_platform(self):
        print(f"\n  Machine: {platform.machine()}")
        print(f"  Platform: {platform.platform()}")
        print(f"  Python: {sys.version}")
        print(f"  Byte order: {sys.byteorder}")
        # This always passes; it's just for CI output
        assert True
