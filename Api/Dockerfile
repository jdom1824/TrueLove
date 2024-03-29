# Primera etapa: construir la aplicación con pyinstaller
FROM python:3.11.7-slim as builder

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el contenido del directorio actual al contenedor en /app
COPY . .

# Instalar las dependencias del sistema
RUN apt-get update && \
    apt-get install -y gcc libc-dev curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    apt-get install -y git

# Configurar el entorno de Rust
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustup default nightly

# Instalar ethers-py y otras dependencias de Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install pyinstaller && \
    pip install git+https://github.com/elyase/ethers-py

# Generar el ejecutable con pyinstaller
RUN pyinstaller --onefile Init.py

# Segunda etapa: crear la imagen final mínima
FROM arm64v8/ubuntu:latest

# Copiar el ejecutable generado por pyinstaller desde la etapa anterior al directorio raíz del contenedor
COPY --from=builder /app/dist/Init /

RUN chmod +x /Init

# Establecer el comando predeterminado para ejecutar la aplicación cuando se inicie el contenedor
CMD ls -l
