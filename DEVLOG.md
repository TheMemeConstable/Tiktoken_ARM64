# Development Log — Tiktoken ARM64

## Session 1 — March 1, 2026

### Context & Motivation

The official [openai/tiktoken](https://github.com/openai/tiktoken) package lacks comprehensive pre-built ARM64 wheel support. Two GitHub issues document the community need:

- **[#23](https://github.com/openai/tiktoken/issues/23)** — "wheels for ARM64 Linux" (Closed). Opened Jan 2023. Maintainer acknowledged demand but never fully shipped ARM64 wheels. Community workarounds involve installing Rust toolchain at build time or multi-stage Docker builds.
- **[#486](https://github.com/openai/tiktoken/issues/486)** — "Add comprehensive wheel support for ARM64 architectures" (Closed as **not planned**). Opened Feb 2026. Requested support for Windows ARM64, Linux ARM64, macOS ARM64. Maintainer closed without action.

**tiktoken** is a Rust-based Python package using `pyo3` + `setuptools-rust`. Building from source requires a Rust compiler and C build tools. The upstream `setup.py` uses `RustExtension("tiktoken._tiktoken", binding=Binding.PyO3, debug=False, features=["python"])`.

Per the CHANGELOG, upstream *did* start building some aarch64 wheels at v0.3.1 and added musllinux aarch64 in v0.12.0, but coverage is incomplete (especially Windows ARM64) and the maintainer has declined to expand support.

### What Was Built

This project is a **wheel-building infrastructure** — it does NOT fork tiktoken. It downloads the upstream tiktoken source and compiles it into ARM64 wheels. Everything works **100% locally** — no server or hosting required. The GitHub Actions CI/CD is an optional automation layer.

### Project Structure

```
C:\OpenAI_Custom\Tiktoken_ARM64\
├── .github/
│   └── workflows/
│       └── build-wheels.yml          # CI/CD: builds wheels for all ARM64 platforms
├── docker/
│   ├── Dockerfile.linux-aarch64      # manylinux aarch64 build via Docker/QEMU
│   └── Dockerfile.musllinux-aarch64  # Alpine/musl aarch64 build via Docker/QEMU
├── scripts/
│   ├── build_local.py                # Local build script (Docker or native)
│   ├── download_wheels.py            # Download wheel artifacts from GitHub Actions
│   └── test_wheel.py                 # Install + smoke test a built wheel
├── tests/
│   ├── __init__.py
│   └── test_smoke.py                 # pytest suite: encode/decode, unicode, edge cases
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE                           # MIT
├── README.md                         # Full background, roadmap, references
├── pyproject.toml                    # cibuildwheel config + pytest config
└── DEVLOG.md                         # This file
```

### GitHub Repository

- **Repo:** https://github.com/TheMemeConstable/Tiktoken_ARM64
- **Visibility:** Public
- **Branch:** `main`
- **Auth:** `gh` CLI authenticated as `TheMemeConstable`

### Remaining TODO from this session

1. **Update placeholder usernames** — `CONTRIBUTING.md` still has `YOUR_USERNAME` in the clone URL. `scripts/download_wheels.py` was already updated to `TheMemeConstable` but that change hasn't been committed/pushed yet.

2. **Commit & push** the `download_wheels.py` fix and this DEVLOG.

3. **Next steps for the project:**
   - [ ] Install Rust toolchain locally and attempt a native build test
   - [ ] Test Docker builds with `build_local.py`
   - [ ] Validate the GitHub Actions workflow runs on push
   - [ ] Test wheels on actual ARM64 hardware
   - [ ] Consider hosting pre-built wheels as GitHub Releases
   - [ ] Update `download_wheels.py` if switching to GitHub Releases

### Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Use `cibuildwheel` in CI | Industry standard for building Python wheels across platforms |
| QEMU emulation for Linux ARM64 | GitHub Actions doesn't have native ARM64 Linux runners (free tier) |
| `macos-14` runner for macOS arm64 | GitHub provides native Apple Silicon runners |
| `CARGO_BUILD_JOBS=2` under QEMU | Prevents OOM — emulated builds are memory-constrained |
| Docker multi-stage builds | Keeps final validation image clean, separates build from test |
| Smoke tests check known token values | `enc.encode("hello world") == [15339, 1917]` for cl100k_base — ensures correctness, not just "it imports" |

### Tools & Versions

- **GitHub CLI:** v2.87.3 (installed via winget)
- **Target tiktoken version:** 0.12.0 (configurable)
- **Python targets:** 3.9, 3.10, 3.11, 3.12, 3.13
- **CI tool:** cibuildwheel 2.22.0
