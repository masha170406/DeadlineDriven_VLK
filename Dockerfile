# --- Stage 1: Build ---
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use copy instead of hardlink for portability within Docker
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (leverage Docker layer caching)
# We mount the cache to speed up subsequent builds
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
ADD . /app

# Sync the project (installs the current package)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# --- Stage 2: Final Runtime ---
FROM python:3.14-slim-bookworm

WORKDIR /app

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the environment and application from the builder
COPY --from=builder --chown=appuser:appuser /app /app

# Place the virtualenv in the path
ENV PATH="/app/.venv/bin:$PATH"

# Ensure the database directory is writable by our non-root user
RUN mkdir -p /app/vlk_chroma_db && chown appuser:appuser /app/vlk_chroma_db

USER appuser

# Expose Streamlit port
EXPOSE 8501

# Run the app. Note: We use "src/app.py" as per your structure.
# We run the database builder script first to ensure DB exists on startup.
CMD python src/build_database.py && streamlit run src/app.py --server.address=0.0.0.0
