# FairDispatch -- Decision-Support Prototype (deployed bundle)
# Single-process app (in-memory SESSIONS/HISTORY) -- must run with exactly
# one uvicorn worker. See README.md for the limitation this implies.
FROM python:3.12-slim

WORKDIR /app

# System deps: none beyond what python:3.12-slim + pip wheels need for
# pyarrow/numpy/scipy (all ship manylinux wheels, no compiler required).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bundle content: backend, frontend, engine (src/policies.py, simulator.py,
# common_loader.py), data (test_eval.parquet, Q-table), artifacts
# (final_test CSVs). Raw train/val/test parquet, docs, and dev tooling are
# excluded via .dockerignore -- test_eval.parquet + its manifest already
# carry full provenance of the raw source it was built from.
COPY backend/ backend/
COPY frontend/ frontend/
COPY engine/ engine/
COPY data/ data/
COPY artifacts/ artifacts/

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend

EXPOSE 10000
ENV PORT=10000

# Exactly ONE worker: SESSIONS/HISTORY are in-process RAM state, not shared
# across workers -- a second worker would silently 404 on runs created by
# the first.
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1"]
