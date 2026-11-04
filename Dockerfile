FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE /app/
COPY harbor_aiops /app/harbor_aiops
RUN pip install --no-cache-dir /app
ENTRYPOINT ["harbor-aiops-mcp"]
