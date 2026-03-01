#!/usr/bin/env python3
"""
Local build script for tiktoken ARM64 wheels.

This script automates downloading the tiktoken source and building ARM64 wheels
using either Docker (cross-platform via QEMU) or native compilation.

Usage:
    python scripts/build_local.py --version 0.12.0 --platform linux-aarch64
    python scripts/build_local.py --version 0.12.0 --platform musllinux-aarch64
    python scripts/build_local.py --version 0.12.0 --platform native
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WHEELHOUSE = REPO_ROOT / "wheelhouse"
DOCKER_DIR = REPO_ROOT / "docker"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a command, printing it first."""
    print(f"\n{'='*60}")
    print(f"  Running: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    return subprocess.run(cmd, check=True, **kwargs)


def build_docker(
    version: str,
    platform: str,
    python_version: str = "3.12",
) -> None:
    """Build a tiktoken wheel using Docker (QEMU emulation for ARM64)."""
    dockerfile = DOCKER_DIR / f"Dockerfile.{platform}"
    if not dockerfile.exists():
        print(f"ERROR: Dockerfile not found: {dockerfile}")
        sys.exit(1)

    WHEELHOUSE.mkdir(exist_ok=True)

    run([
        "docker", "buildx", "build",
        "--platform", "linux/arm64",
        "-f", str(dockerfile),
        "--build-arg", f"PYTHON_VERSION={python_version}",
        "--build-arg", f"TIKTOKEN_VERSION={version}",
        "--output", f"type=local,dest={WHEELHOUSE}",
        str(REPO_ROOT),
    ])

    wheels = list(WHEELHOUSE.glob("*.whl"))
    if wheels:
        print(f"\nSUCCESS: Built {len(wheels)} wheel(s):")
        for w in wheels:
            print(f"  {w.name}")
    else:
        print("\nWARNING: No .whl files found in wheelhouse/")


def build_native(version: str) -> None:
    """Build a tiktoken wheel natively (requires Rust toolchain)."""
    WHEELHOUSE.mkdir(exist_ok=True)
    src_dir = REPO_ROOT / "source"
    src_dir.mkdir(exist_ok=True)

    # Download source
    run([
        sys.executable, "-m", "pip", "download",
        "--no-binary", ":all:", "--no-deps",
        f"tiktoken=={version}",
        "-d", str(src_dir),
    ])

    # Extract
    import glob
    archives = glob.glob(str(src_dir / "*.tar.gz"))
    if not archives:
        print("ERROR: No source archive found")
        sys.exit(1)

    import tarfile
    with tarfile.open(archives[0]) as tar:
        tar.extractall(path=str(src_dir))

    # Find extracted dir
    extracted = [d for d in src_dir.iterdir() if d.is_dir() and d.name.startswith("tiktoken-")]
    if not extracted:
        print("ERROR: Could not find extracted tiktoken source")
        sys.exit(1)

    # Build wheel
    run([
        sys.executable, "-m", "pip", "wheel",
        str(extracted[0]),
        "--no-deps",
        "-w", str(WHEELHOUSE),
    ])

    wheels = list(WHEELHOUSE.glob("tiktoken-*.whl"))
    if wheels:
        print(f"\nSUCCESS: Built {len(wheels)} wheel(s):")
        for w in wheels:
            print(f"  {w.name}")
    else:
        print("\nWARNING: No tiktoken .whl files found in wheelhouse/")


def main():
    parser = argparse.ArgumentParser(
        description="Build tiktoken ARM64 wheels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Platforms:
  linux-aarch64       Build manylinux aarch64 wheel via Docker + QEMU
  musllinux-aarch64   Build musllinux aarch64 wheel via Docker + QEMU
  native              Build natively on current machine (requires Rust)

Examples:
  python scripts/build_local.py --version 0.12.0 --platform linux-aarch64
  python scripts/build_local.py --version 0.12.0 --platform native
  python scripts/build_local.py --version 0.12.0 --platform linux-aarch64 --python 3.11
""",
    )
    parser.add_argument(
        "--version", "-v",
        default="0.12.0",
        help="Tiktoken version to build (default: 0.12.0)",
    )
    parser.add_argument(
        "--platform", "-p",
        choices=["linux-aarch64", "musllinux-aarch64", "native"],
        default="native",
        help="Target platform (default: native)",
    )
    parser.add_argument(
        "--python",
        default="3.12",
        help="Python version for Docker builds (default: 3.12)",
    )

    args = parser.parse_args()

    print(f"Building tiktoken {args.version} for {args.platform}")

    if args.platform == "native":
        build_native(args.version)
    else:
        build_docker(args.version, args.platform, args.python)


if __name__ == "__main__":
    main()
