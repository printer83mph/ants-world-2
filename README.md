# AntsWorld 2

CIS 1912 - DevOps

## Development

To run the development environment, simply cd into `backend` and run `docker compose up`.

Backend services will be available at:

- `http://localhost:8000/auth`
- `http://localhost:8000/stream`

And the Redis will be viewable at `redis://localhost:6379`.

Database migrations will be run automatically, and an instance of PGAdmin will be spun up at `localhost:5050` (with password "password").

## Testing

To test out the streaming websocket through nginx, run the folllowing in Node:

```js
const ws = new WebSocket("ws://localhost:8000/stream/ws");
ws.onmessage = (e) => {
  console.log(e.data);
};

// request (0, 0) to (40, 40) viewport
ws.send(
  JSON.stringify({
    request: { type: "set-viewport", xmin: 0, xmax: 40, ymin: 0, ymax: 40 },
  }),
);
```

You should see buffered snapshots coming through!

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
