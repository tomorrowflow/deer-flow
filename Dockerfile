FROM node:current-slim AS node
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install Node
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/include/node /usr/local/include/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules

WORKDIR /app

# Pre-cache the application dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

RUN ln -vs /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -vs /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

EXPOSE 8000

# Run the application.
CMD ["uv", "run", "python", "server.py", "--host", "0.0.0.0", "--port", "8000"]
