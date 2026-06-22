# Contributing to TETRA OS

Thank you for your interest in contributing. TETRA OS is maintained by **Walter Calmels** and released under the MIT License.

## Getting Started

1. Fork [wcalmels/tetra-os](https://github.com/wcalmels/tetra-os) and clone your fork
2. Create a branch: `git checkout -b feature/my-feature`
3. Install dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
4. Make your changes and ensure tests pass
5. Push and open a Pull Request against `main`

## Running Tests

```bash
# Primary integration suite (required — must be 7/7)
python tetra_first_test.py

# Pytest suite (when tests are added)
pytest tests/ --cov=tetra_os
```

## Code Style

- Follow PEP 8; format with `black` and sort imports with `isort`
- Use Google-style docstrings on public APIs
- Add type hints on public functions
- Keep changes focused — one feature or fix per PR

## Commit Messages

Use conventional prefixes:

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `test:` — tests only
- `refactor:` — code change without behavior change
- `ci:` — CI/CD changes

## Pull Request Checklist

- [ ] `python tetra_first_test.py` passes (7/7)
- [ ] CHANGELOG.md updated for user-visible changes
- [ ] README updated if public API or usage changed
- [ ] No secrets or credentials committed

## Questions?

Open a [Discussion](https://github.com/wcalmels/tetra-os/discussions) or an [Issue](https://github.com/wcalmels/tetra-os/issues).
