FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости ПЕРВЫМИ (для кеширования)
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY src/ ./src/
COPY config/ ./config/

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app/src

# Запускаем
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]