# Используется базовый образ Python
FROM python:3.10

# Установка рабочего каталога в контейнере
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY ./project ./project
COPY main.py .
COPY .env .

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
