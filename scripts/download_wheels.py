#!/usr/bin/env python3
"""
Download tiktoken ARM64 wheel artifacts from GitHub Actions or GitHub Releases.

Usage:
    # From a GitHub Actions workflow run (requires token):
    python scripts/download_wheels.py --source actions --token GITHUB_TOKEN --run-id 12345

    # From a GitHub Release tag (public, no token needed):
    python scripts/download_wheels.py --source release --tag v0.12.0

    # From latest GitHub Release:
    python scripts/download_wheels.py --source release
"""

import argparse
import io
import os
import zipfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package required. Install with: pip install requests")
    raise SystemExit(1)

REPO_OWNER = "TheMemeConstable"
REPO_NAME = "Tiktoken_ARM64"
API_BASE = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


def _headers(token: str | None = None) -> dict[str, str]:
    """Build GitHub API request headers."""
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def download_from_actions(
    token: str,
    run_id: str,
    output_dir: Path,
) -> None:
    """Download all wheel artifacts from a GitHub Actions run."""
    output_dir.mkdir(parents=True, exist_ok=True)
    headers = _headers(token)

    url = f"{API_BASE}/actions/runs/{run_id}/artifacts"
    print(f"Fetching artifacts from: {url}")

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    artifacts = data.get("artifacts", [])
    if not artifacts:
        print("No artifacts found for this run.")
        return

    wheel_artifacts = [a for a in artifacts if a["name"].startswith("wheel-")]
    print(f"Found {len(wheel_artifacts)} wheel artifact(s)")

    for artifact in wheel_artifacts:
        name = artifact["name"]
        download_url = artifact["archive_download_url"]

        print(f"\n  Downloading: {name}...")
        resp = requests.get(download_url, headers=headers)
        resp.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            for f in zf.namelist():
                if f.endswith(".whl"):
                    print(f"    Extracting: {f}")
                    zf.extract(f, output_dir)

    _list_wheels(output_dir)


def download_from_release(
    tag: str | None,
    output_dir: Path,
    token: str | None = None,
) -> None:
    """Download wheel assets from a GitHub Release."""
    output_dir.mkdir(parents=True, exist_ok=True)
    headers = _headers(token)

    if tag:
        url = f"{API_BASE}/releases/tags/{tag}"
    else:
        url = f"{API_BASE}/releases/latest"

    print(f"Fetching release from: {url}")
    resp = requests.get(url, headers=headers)
    if resp.status_code == 404:
        print(f"ERROR: Release not found{f' for tag {tag}' if tag else ''}")
        raise SystemExit(1)
    resp.raise_for_status()
    release = resp.json()

    print(f"Release: {release['tag_name']} — {release['name']}")

    assets = [a for a in release.get("assets", []) if a["name"].endswith(".whl")]
    if not assets:
        print("No .whl assets found in this release.")
        return

    print(f"Found {len(assets)} wheel(s)")

    for asset in assets:
        name = asset["name"]
        download_url = asset["browser_download_url"]

        print(f"  Downloading: {name}...")
        resp = requests.get(download_url, headers=_headers(token), stream=True)
        resp.raise_for_status()

        dest = output_dir / name
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

    _list_wheels(output_dir)


def _list_wheels(output_dir: Path) -> None:
    """Print summary of downloaded wheels."""
    wheels = sorted(output_dir.glob("*.whl"))
    print(f"\nDownloaded {len(wheels)} wheel(s) to {output_dir}/")
    for w in wheels:
        size_kb = w.stat().st_size / 1024
        print(f"  {w.name}  ({size_kb:.0f} KB)")


def main():
    parser = argparse.ArgumentParser(
        description="Download tiktoken ARM64 wheels from GitHub Actions or Releases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --source release --tag v0.12.0
  %(prog)s --source release                          # latest release
  %(prog)s --source actions --token ghp_xxx --run-id 12345
""",
    )
    parser.add_argument(
        "--source", choices=["actions", "release"], default="release",
        help="Download from GitHub Actions artifacts or Releases (default: release)",
    )
    parser.add_argument("--tag", help="Release tag (e.g. v0.12.0). Omit for latest release.")
    parser.add_argument("--token", help="GitHub Personal Access Token (required for actions, optional for release)")
    parser.add_argument("--run-id", help="GitHub Actions workflow run ID (required for --source actions)")
    parser.add_argument("--output-dir", default="wheelhouse", help="Output directory (default: wheelhouse/)")

    args = parser.parse_args()

    if args.source == "actions":
        if not args.token:
            parser.error("--token is required when --source=actions")
        if not args.run_id:
            parser.error("--run-id is required when --source=actions")
        download_from_actions(args.token, args.run_id, Path(args.output_dir))
    else:
        download_from_release(args.tag, Path(args.output_dir), args.token)


if __name__ == "__main__":
    main()
