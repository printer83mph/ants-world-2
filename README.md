# AntsWorld 2

CIS 1912 - DevOps

## Development

To run the development environment, simply cd into `backend` and run `docker compose up`.

Backend services will be available at:

- `http://localhost:8000/auth`
- `http://localhost:8000/stream`

And the Redis will be viewable at `redis://localhost:6379`.

Database migrations will be run automatically, and an instance of PGAdmin will be spun up at `localhost:5050` (with password "password").

## Devops-specific code

- CI checks
  - [`.github/workflows/code-quality-python.yml`](./.github/workflows/code-quality-python.yml)
- Dev environment with docker compose
  - [`backend/compose.yml`](./backend/compose.yml)
- Monorepo shared deps
  - [`backend/shared/repository/pyproject.toml`](./backend/shared/repository/pyproject.toml)
  - [`backend/shared/database/pyproject.toml`](./backend/shared/database/pyproject.toml)

kinda devops / systems code:

- Simulation vs streaming
  - [`backend/services/simulator/app/simulator.py`](./backend/services/simulator/app/simulator.py)
  - [`backend/services/stream/app/routers/stream.py`](./backend/services/stream/app/routers/stream.py)
