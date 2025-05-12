FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Ensure scripts are executable
RUN chmod +x /app/scripts/*.sh

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Use our custom entrypoint
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "/app/src/main.py", "--port", "3000", "--host", "0.0.0.0"]
