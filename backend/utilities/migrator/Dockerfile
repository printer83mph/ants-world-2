FROM python:3.12-slim

# Set work directory
WORKDIR /backend/utilities/migrator

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy all files into container
COPY utilities/migrator .

# Copy the utilities folder into a similar structure on the container
# Note the /, this is an absolute path
COPY shared /backend/shared

# Install dependencies
RUN uv sync --no-cache --link-mode=copy
