#!/usr/bin/env python3
"""
Test script to validate a tiktoken ARM64 wheel.

This script installs a wheel from the wheelhouse and runs a comprehensive
suite of smoke tests to verify correctness.

Usage:
    python scripts/test_wheel.py
    python scripts/test_wheel.py --wheel wheelhouse/tiktoken-0.12.0-cp312-cp312-linux_aarch64.whl
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WHEELHOUSE = REPO_ROOT / "wheelhouse"


def find_wheel(wheel_path: str | None = None) -> Path:
    """Find a tiktoken wheel to test."""
    if wheel_path:
        p = Path(wheel_path)
        if not p.exists():
            print(f"ERROR: Wheel not found: {p}")
            sys.exit(1)
        return p

    wheels = sorted(WHEELHOUSE.glob("tiktoken-*.whl"))
    if not wheels:
        print(f"ERROR: No tiktoken wheels found in {WHEELHOUSE}")
        print("  Run build_local.py first, or specify --wheel")
        sys.exit(1)

    # Prefer wheel matching current Python version
    py_tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    for w in wheels:
        if py_tag in w.name:
            return w

    return wheels[-1]  # latest


def install_wheel(wheel: Path) -> None:
    """Install the wheel into current environment."""
    print(f"\nInstalling: {wheel.name}")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--force-reinstall", str(wheel)],
        check=True,
    )
    # Ensure requests is available for tiktoken's BPE file downloads
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "requests"],
        check=True,
        capture_output=True,
    )


def run_tests() -> bool:
    """Run smoke tests against the installed tiktoken wheel."""
    print("\n" + "=" * 60)
    print("  Running tiktoken ARM64 smoke tests")
    print("=" * 60)

    results = []

    # Test 1: Basic import
    print("\n[1/6] Import test...", end=" ")
    try:
        import tiktoken
        print(f"OK (version: {getattr(tiktoken, '__version__', 'unknown')})")
        results.append(True)
    except Exception as e:
        print(f"FAIL: {e}")
        results.append(False)
        return False  # Can't continue without import

    # Test 2: Get encoding
    print("[2/6] Get encoding (cl100k_base)...", end=" ")
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        print(f"OK (name: {enc.name})")
        results.append(True)
    except Exception as e:
        print(f"FAIL: {e}")
        results.append(False)
        return False

    # Test 3: Encode/decode roundtrip
    print("[3/6] Encode/decode roundtrip...", end=" ")
    try:
        test_string = "Hello, world! This is a test of tiktoken on ARM64."
        tokens = enc.encode(test_string)
        decoded = enc.decode(tokens)
        assert decoded == test_string, f"Mismatch: {decoded!r} != {test_string!r}"
        print(f"OK ({len(tokens)} tokens)")
        results.append(True)
    except Exception as e:
        print(f"FAIL: {e}")
        results.append(False)

    # Test 4: Known encoding values
    print("[4/6] Known token values...", end=" ")
    try:
        tokens = enc.encode("hello world")
        assert tokens == [15339, 1917], f"Unexpected: {tokens}"
        print("OK")
        results.append(True)
    except Exception as e:
        print(f"FAIL: {e}")
        results.append(False)

    # Test 5: Multiple encodings
    print("[5/6] Multiple encodings...", end=" ")
    try:
        for name in ["cl100k_base", "p50k_base", "r50k_base"]:
            e = tiktoken.get_encoding(name)
            t = e.encode("test")
            assert len(t) > 0
        print("OK (cl100k_base, p50k_base, r50k_base)")
        results.append(True)
    except Exception as e:
        print(f"FAIL: {e}")
        results.append(False)

    # Test 6: Unicode handling
    print("[6/6] Unicode handling...", end=" ")
    try:
        test_strings = [
            "こんにちは世界",  # Japanese
            "مرحبا بالعالم",  # Arabic
            "🎉🚀✨",          # Emoji
            "Héllo wörld",    # Accented Latin
        ]
        for s in test_strings:
            tokens = enc.encode(s)
            decoded = enc.decode(tokens)
            assert decoded == s, f"Unicode roundtrip failed for {s!r}"
        print("OK")
        results.append(True)
    except Exception as e:
        print(f"FAIL: {e}")
        results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"  Platform: {platform.machine()} / {platform.platform()}")
    print(f"  Python: {sys.version}")
    print(f"{'='*60}")

    return all(results)


def main():
    parser = argparse.ArgumentParser(description="Test a tiktoken ARM64 wheel")
    parser.add_argument(
        "--wheel", "-w",
        default=None,
        help="Path to specific wheel to test (default: auto-detect from wheelhouse/)",
    )
    parser.add_argument(
        "--no-install",
        action="store_true",
        help="Skip installation, just run tests against already-installed tiktoken",
    )
    args = parser.parse_args()

    if not args.no_install:
        wheel = find_wheel(args.wheel)
        install_wheel(wheel)

    success = run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
