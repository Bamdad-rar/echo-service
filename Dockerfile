FROM python:3.13

RUN apt-get update && apt-get install -y --no-install-recommends gcc net-tools iputils-ping vim curl ca-certificates
RUN rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /chronos

COPY pyproject.toml /chronos/
COPY uv.lock /chronos/
COPY .python-version /chronos/
COPY README.md /chronos/
COPY src/ /chronos/src/

RUN uv venv
RUN uv sync --frozen

ENV PATH="/chronos/.venv/bin:$PATH"

COPY . /chronos

RUN mkdir -p /var/log/chronos
