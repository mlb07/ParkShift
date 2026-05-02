# Contributing

ParkShift is early-stage. Small, focused changes are easiest to review.

## Local Setup

```bash
python -m pip install -e ".[dev,api,fetch]"
```

Run the checks before opening a pull request:

```bash
python -m pytest -q
node --check web/app.js
```

## Development Notes

- Keep generated files, downloaded Savant data, trained models, and local caches out of git.
- Prefer small tests next to the behavior being changed.
- Document assumptions when changing park geometry, source-team inference, or translation math.
- Treat results as estimates unless they are explicitly official values returned by public MLB/Savant endpoints.

## Data

Do not commit private datasets, paid data, credentials, or large downloaded files. If a fixture is needed, keep it small and synthetic unless it is already public and suitable for redistribution.
