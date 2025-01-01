# Використовуємо базовий образ Python
FROM python:3.9-slim

# Встановлюємо необхідні бібліотеки
RUN pip install --no-cache-dir discord.py requests

# Копіюємо всі файли в контейнер
COPY . /app

# Встановлюємо робочу директорію
WORKDIR /app

# Вказуємо команду запуску
ENTRYPOINT ["python", "main.py"]
