FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl

COPY deapp/ta-lib_0.6.4_amd64.deb /tmp/ta-lib_0.6.4_amd64.deb

# Устанавливаем .deb-пакет
RUN dpkg -i /tmp/ta-lib_0.6.4_amd64.deb && \
    rm /tmp/ta-lib_0.6.4_amd64.deb

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY deapp .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота
CMD ["python", "main.py"]
