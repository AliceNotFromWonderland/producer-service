#!/bin/sh
# Runs before any command in this image's containers (see Dockerfile's
# ENTRYPOINT). Applies pending Alembic migrations, then execs whatever CMD
# was actually requested (the API server by default, or e.g.
# `python -m app.outbox_relay` when docker-compose overrides `command:`).
#
# `alembic upgrade head` is idempotent — running it again when already at
# the latest revision is a fast no-op, so it's safe for every service that
# shares this image to run it on startup.
set -e

echo "Applying database migrations (alembic upgrade head)..."
alembic upgrade head

echo "Starting: $*"
exec "$@"
