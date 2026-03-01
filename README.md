# Tiktoken ARM64 Wheel Build Project

## Goal
Build and distribute pre-compiled tiktoken wheels for ARM64 architectures, addressing a long-standing gap in the official tiktoken package.

## Background

The official [openai/tiktoken](https://github.com/openai/tiktoken) repository does not provide comprehensive ARM64 wheel support. Two key issues document the community need:

### Issue #23 — "wheels for ARM64 Linux" (Closed)
- **Opened:** Jan 23, 2023 by @dalberto
- **Problem:** Installing `tiktoken` on ARM64 (e.g., `python:3.11-slim` Docker on Apple Silicon) fails with `error: can't find Rust compiler` because no pre-built wheel exists for `aarch64`.
- **Maintainer response:** Initially declined due to slow QEMU-based CI emulation. Later acknowledged community demand and invited PRs, but full support was never shipped.
- **Community workaround — install Rust toolchain at build time:**
  ```dockerfile
  apt-get update && apt-get install -y --no-install-recommends curl gcc \
    && curl https://sh.rustup.rs -sSf | sh -s -- -y \
    && apt-get install --reinstall libc6-dev -y
  export PATH="/root/.cargo/bin:$PATH"
  pip install tiktoken
  ```
- **Multi-stage Docker workaround** (avoids Rust in final image):
  ```dockerfile
  FROM python:3.11-slim-bullseye AS builder
  RUN apt-get update && apt-get install -y gcc curl
  RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && apt-get install --reinstall libc6-dev -y
  ENV PATH="/root/.cargo/bin:${PATH}"
  RUN pip install --upgrade pip && pip install tiktoken

  FROM python:3.11-slim-bullseye
  COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
  ```

### Issue #486 — "Add comprehensive wheel support for ARM64 architectures" (Closed as not planned)
- **Opened:** Feb 2026 by @swamy18
- **Request:** Comprehensive ARM64 support for Windows ARM64, Linux ARM64 (Apple Silicon, Graviton), and embedded systems.
- **Proposed solution:**
  1. Build and distribute ARM64 wheels for all supported Python versions
  2. Support Windows ARM64, Linux ARM64, macOS ARM64
  3. Add ARM64 CI/CD pipeline for automated testing
  4. Ensure Rust compilation optimizes for ARM64 targets
  5. Test performance across ARM architectures
  6. Document ARM64 installation and usage
  7. Add ARM64 to binary compatibility matrix
- **Outcome:** Closed as **not planned** by maintainer.

## Target Platforms

| Platform             | Architecture       | Notes                                    |
|----------------------|--------------------|------------------------------------------|
| Linux ARM64          | `aarch64`          | Docker, AWS Graviton, Raspberry Pi       |
| macOS ARM64          | `arm64` (Apple Si) | M1/M2/M3/M4 Macs                        |
| Windows ARM64        | `aarch64`          | Surface Pro X, Snapdragon laptops, etc.  |

## Key Technical Notes

- **tiktoken** is a Rust-based Python package (uses `pyo3` + `maturin`/`setuptools-rust`).
- Building from source requires:
  - A Rust compiler (`rustup`)
  - C build tools (`gcc`, `libc6-dev`)
- Cross-compilation for ARM64 can use:
  - QEMU emulation in GitHub Actions (slow but functional)
  - Native ARM64 runners (faster, e.g., GitHub ARM64 runners, Cirrus CI)
  - `cross` or `cargo-zigbuild` for cross-compilation from x86_64

## Project Roadmap

- [ ] Set up Rust cross-compilation environment for ARM64
- [ ] Build tiktoken wheel for Linux aarch64 (manylinux)
- [ ] Build tiktoken wheel for macOS arm64
- [ ] Build tiktoken wheel for Windows ARM64
- [ ] Test wheels across Python 3.9–3.13
- [ ] Create CI/CD pipeline for automated ARM64 wheel builds
- [ ] Publish wheels (PyPI or custom index)
- [ ] Document installation instructions

## References

- https://github.com/openai/tiktoken
- https://github.com/openai/tiktoken/issues/23
- https://github.com/openai/tiktoken/issues/486
- https://github.com/openai/tiktoken/pull/54 (early QEMU CI attempt)
