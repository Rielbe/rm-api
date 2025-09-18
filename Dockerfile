FROM python:3.13-slim AS base
RUN apt-get update && apt-get install -y curl

WORKDIR /w
RUN curl -fsSL https://astral.sh/uv/install.sh | sh \
    && mv $HOME/.local/bin/uv /usr/local/bin/

COPY pyproject.toml uv.lock ./
RUN uv export --no-dev | uv pip install --no-cache-dir --target /deps -r /dev/stdin


FROM python:3.13-slim AS app
COPY --from=base /deps /usr/local/lib/python3.13/site-packages/
WORKDIR /app
COPY main.py ./
COPY src ./src/

ENTRYPOINT [ "python" ]
CMD ["-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
