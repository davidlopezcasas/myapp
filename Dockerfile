# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /clientes

# Copia los archivos de requisitos y la aplicación al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

# Copia el resto de tu aplicación al contenedor
COPY . .

# Expone el puerto en el que tu app estará corriendo
EXPOSE 5000

# Comando para ejecutar tu aplicación
CMD ["python", "app.py"]
