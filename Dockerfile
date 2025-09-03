FROM ghcr.io/astral-sh/uv:0.8.14 AS uv

FROM python:3.13.7-alpine3.21 AS build
COPY --from=uv /uv /uvx /bin/
WORKDIR /app
COPY . .
RUN uv venv && \
    uv sync --frozen --no-cache --no-dev

FROM python:3.13.7-alpine3.21 AS runtime
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app /app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["fastapi", "run", "--host", "0.0.0.0"]
