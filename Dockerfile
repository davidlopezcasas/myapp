# Usar una imagen base de Python 3.9 en Debian Buster
FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    libgirepository1.0-dev \
    libcairo2 \
    libcairo2-dev \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libglib2.0-0 \
    libglib2.0-dev \
    libpango1.0-0 \
    libpango1.0-dev \
    && apt-get clean

# Crear el directorio de la aplicación
WORKDIR /clientes

# Copiar archivos de requerimientos
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Comando para ejecutar tu aplicación
CMD ["python", "app.py"]
