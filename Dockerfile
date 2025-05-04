# Base enxuta
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

WORKDIR /app

# Instala libs do sistema (como build-essential, gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Cria um usuário não-root
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Copia e instala dependências
COPY --chown=appuser:appuser requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install "uvicorn[standard]"  # força instalação correta do binário

# Copia o resto da aplicação
COPY --chown=appuser:appuser . .

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
