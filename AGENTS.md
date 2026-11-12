# Repository Guidelines

## Project Structure & Module Organization

Proyecta implements demand and revenue forecasting in `src/proyecta/`:

- `domain/`: entities, value objects, and the calculation engine in `domain/engine/`.
- `application/`: use cases, ports, and audit services.
- `infrastructure/`: adapters for AI, persistence, authentication, and exports; several areas remain scaffolding.
- `interfaces/`: FastAPI routes and web templates under `interfaces/web/templates/`.
- `seed/`: synthetic data generators and demo fixtures.

Tests live in `tests/unit/domain/` and `tests/integration/`. Supporting requirements, team ownership, architecture decisions, and demo instructions live in `docs/`. Read `src/proyecta/README.md`, `tests/README.md`, and `docs/equipo.md` before changing their areas. The specification lives in `specs/001-proyecta-mvp/` and the requirements in `docs/fuentes/requerimientos.md`.

## Build, Test, and Development Commands

Run from the repository root with Python 3.12 as the documented target:

- `python -m pytest tests -q`: run the available test suite.
- `python -m pytest tests/unit/domain -q`: run domain tests.
- `python -m pytest tests/integration -q`: exercise use cases and adapters.
- `python -m pytest tests --cov=proyecta.domain --cov-fail-under=90`: check domain coverage; requires `pytest-cov`.
- `python scripts/seed_synthetic.py --fixture four-records --salida fixture.json`: generate the demo fixture.

Install with `pip install -e '.[dev]'` (`pyproject.toml`). Run the app with `uvicorn proyecta.main:app --reload` and build the image with `docker build -f deploy/Dockerfile -t proyecta .`. Persistence is in memory (`infrastructure/memoria.py`) until the Datastore adapters exist.

## Coding Style & Naming Conventions

Use four-space indentation, type hints, `snake_case` modules/functions, `PascalCase` classes, and `UPPER_SNAKE_CASE` constants. Follow existing Spanish business terminology and focused module responsibilities. No formatter or linter configuration is checked in.

Keep dependencies flowing from interfaces through application to domain. Domain code must avoid framework, database, and cloud imports. Store CLP totals as integers, rates in centavos, and probabilities in basis points; preserve established rounding rules.

## Testing Guidelines

Use pytest with `test_*.py` files and `test_*` functions. Write failing tests before implementing stories. Maintain at least 90% domain coverage and preserve engine regressions C-01 through C-08. Use synthetic fixtures and in-memory fakes.

## Commit & Pull Request Guidelines

History contains brief messages such as `Dominio, motor, IA/simulacion y carga inicial US11`; no consistent commit format is established. Use descriptive, scoped messages and reference relevant task/story IDs. PRs should explain behavior changes, link applicable requirements or issues, report test results, and include screenshots for UI changes.

## Security & Data Handling

Never commit credentials, `.env`, or real client, rate, or revenue data. Relevant writes must generate audit records; avoid physical deletion of business records.
