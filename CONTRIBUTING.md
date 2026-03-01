# Contributing to Tiktoken ARM64

Thank you for your interest in contributing!

## Development Setup

### Prerequisites

- Python 3.9+
- Docker with `buildx` (for cross-platform builds)
- Rust toolchain (for native builds): `curl https://sh.rustup.rs -sSf | sh`
- Git

### Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/TheMemeConstable/Tiktoken_ARM64.git
   cd Tiktoken_ARM64
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Install dev dependencies:
   ```bash
   pip install pytest requests
   ```

## Building Wheels

### Native Build (on ARM64 machine)

```bash
python scripts/build_local.py --version 0.12.0 --platform native
```

### Docker Build (cross-compile via QEMU)

```bash
# Linux aarch64 (glibc)
python scripts/build_local.py --version 0.12.0 --platform linux-aarch64

# Linux aarch64 (musl/Alpine)
python scripts/build_local.py --version 0.12.0 --platform musllinux-aarch64
```

## Testing

```bash
# Test with an already-installed tiktoken
pytest tests/ -v

# Install a wheel and test it
python scripts/test_wheel.py --wheel wheelhouse/tiktoken-*.whl
```

## CI/CD

The GitHub Actions workflow (`.github/workflows/build-wheels.yml`) runs
automatically on push to `main` and on pull requests. It builds wheels for:

- Linux aarch64 (manylinux2014)
- Linux aarch64 (musllinux)
- macOS arm64 (Apple Silicon)
- Windows ARM64

You can also trigger a build manually via the Actions tab with a specific
tiktoken version.

## Reporting Issues

- Include your platform (`python -c "import platform; print(platform.machine(), platform.platform())"`)
- Include the tiktoken version you're trying to build
- Include the full error output
