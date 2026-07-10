# Imagen propia de myapp_container (Flask)
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias primero (aprovecha la cache de capas de Docker)
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/app.py .

EXPOSE 5000

CMD ["python", "app.py"]
