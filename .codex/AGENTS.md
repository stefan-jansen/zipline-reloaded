# AGENTS.md — Guidance for OpenAI Codex

## Environment bootstrap

- Create a clean virtual environment.
- Install all build, runtime, and test dependencies:

```bash
  pip install -e .[dev,test]
```

- Ensure the TA-Lib C library is available
  - Linux: `sudo ./tools/install_talib.sh`
  - macOS: `brew install ta-lib`
  - Windows: `tools\install_talib.bat`
- Set `MPLBACKEND=Agg` to avoid GUI requirements during testing.

## Success criteria

1. The following command must exit with status 0 and emit no warnings or errors:

   ```bash
   pytest -n auto --reruns 5 --strict-markers --disable-warnings -q
   ```

2. Static analysis must pass [this is a medium term goal since we just added ruff and there is a large number of errors at this point]:

   ```bash
   ruff check src/
   ```

3. You may iterate with a narrower environment, but the primary check above must remain green:

   ```bash
   tox -e py311-pandas2
   ```

## Coding conventions

- Follow ruff formatting rules from `pyproject.toml`.
- Do **not** add broad warning filters. If a third-party package raises unavoidable warnings, mark them locally with `pytest.warns`.
- Keep public API behaviour unchanged; update or add tests to validate fixes.
- Commit messages: `<scope>: <brief description>`.

## Recommended workflow

1. Run the full suite once to reproduce failures: `pytest -n auto --reruns 5 --strict-markers --disable-warnings -q`.
2. Use `pytest --lf` or target a single failing module while iterating.
3. Replace deprecated NumPy or pandas APIs instead of suppressing warnings.
4. Group related changes in a single commit; keep patches focused.

## References

- The full tox matrix is defined in `[tool.tox]` inside `pyproject.toml`.
- CI installation and test commands are documented in `.github/workflows/`.
