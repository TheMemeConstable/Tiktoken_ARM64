#!/usr/bin/env python3
"""
Download wheel artifacts from a GitHub Actions workflow run.

Usage:
    python scripts/download_wheels.py --token GITHUB_TOKEN --run-id 12345
    python scripts/download_wheels.py --token GITHUB_TOKEN --run-id 12345 --output-dir dist/
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

REPO_OWNER = "YOUR_GITHUB_USERNAME"  # TODO: Update after repo creation
REPO_NAME = "Tiktoken_ARM64"


def download_artifacts(
    token: str,
    run_id: str,
    output_dir: Path,
    owner: str = REPO_OWNER,
    repo: str = REPO_NAME,
) -> None:
    """Download all wheel artifacts from a GitHub Actions run."""
    output_dir.mkdir(parents=True, exist_ok=True)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # List artifacts for the run
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
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

        # Artifacts are zipped
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            for f in zf.namelist():
                if f.endswith(".whl"):
                    print(f"    Extracting: {f}")
                    zf.extract(f, output_dir)

    # List what we got
    wheels = list(output_dir.glob("*.whl"))
    print(f"\nDownloaded {len(wheels)} wheel(s) to {output_dir}/")
    for w in sorted(wheels):
        print(f"  {w.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Download tiktoken ARM64 wheel artifacts from GitHub Actions"
    )
    parser.add_argument("--token", required=True, help="GitHub Personal Access Token")
    parser.add_argument("--run-id", required=True, help="GitHub Actions workflow run ID")
    parser.add_argument("--output-dir", default="wheelhouse", help="Output directory (default: wheelhouse/)")
    parser.add_argument("--owner", default=REPO_OWNER, help="GitHub repo owner")
    parser.add_argument("--repo", default=REPO_NAME, help="GitHub repo name")

    args = parser.parse_args()
    download_artifacts(
        token=args.token,
        run_id=args.run_id,
        output_dir=Path(args.output_dir),
        owner=args.owner,
        repo=args.repo,
    )


if __name__ == "__main__":
    main()
