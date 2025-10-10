# Dockerfile
FROM ubuntu:22.04

LABEL maintainer="rodrigo.peralta@uner.edu.ar"
LABEL org.opencontainers.image.source="https://github.com/daxer99/microbiome-pipeline-docker"

# Evitar preguntas durante instalación
ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC

# Actualizar sistema e instalar dependencias básicas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        curl \
        unzip \
        openjdk-17-jre \
        ca-certificates \
        locales && \
    rm -rf /var/lib/apt/lists/*

# Configurar UTF-8
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Crear usuario no-root
RUN useradd -m -s /bin/bash microbiome && \
    mkdir -p /home/microbiome/work && \
    chown -R microbiome:microbiome /home/microbiome

WORKDIR /home/microbiome

# Instalar Python 3.10
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev && \
    ln -sf python3.10 /usr/bin/python && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python

# Crear entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN chown -R microbiome:microbiome /opt/venv

# Instalar dependencias principales
RUN pip install \
    kneaddata==0.12.3 \
    metaphlan==4.2.2 \
    humann==3.9 \
    biopython \
    pandas \
    pyyaml

# --- INSTALAR TRIMMOMATIC ---
ENV TRIMMOMATIC_ORIG=/opt/trimmomatic
RUN mkdir -p $TRIMMOMATIC_ORIG && \
    curl -L -o Trimmomatic-0.40.zip \
         "https://github.com/usadellab/Trimmomatic/releases/download/v0.40/Trimmomatic-0.40.zip" && \
    unzip Trimmomatic-0.40.zip -d /tmp/trimmomatic-extract && \
    cp -r /tmp/trimmomatic-extract/* $TRIMMOMATIC_ORIG/ && \
    rm -rf Trimmomatic-0.40.zip /tmp/trimmomatic-extract

# --- CREAR WRAPPER CON MÁS MEMORIA PARA TRIMMOMATIC ---
RUN mkdir -p /opt/trimmomatic-wrapper && \
    echo '#!/bin/bash' > /opt/trimmomatic-wrapper/trimmomatic-0.40.jar && \
    echo 'echo "🔧 Usando java con -Xmx8g"' >> /opt/trimmomatic-wrapper/trimmomatic-0.40.jar && \
    echo 'exec java -Xmx4g -jar "$TRIMMOMATIC_ORIG/trimmomatic-0.40.jar" "$@"' >> /opt/trimmomatic-wrapper/trimmomatic-0.40.jar && \
    chmod +x /opt/trimmomatic-wrapper/trimmomatic-0.40.jar

# Apuntar kneaddata al wrapper
ENV TRIMMOMATIC_DIR=/opt/trimmomatic-wrapper

# --- INSTALAR DIAMOND (para HUMAnN) ---
RUN wget -O /tmp/diamond-linux64.tar.gz https://github.com/bbuchfink/diamond/releases/download/v2.1.8/diamond-linux64.tar.gz && \
    tar -xzf /tmp/diamond-linux64.tar.gz -C /tmp && \
    mv /tmp/diamond /usr/local/bin/diamond && \
    chmod +x /usr/local/bin/diamond && \
    rm -rf /tmp/diamond-linux64.tar.gz && \
    echo "✅ DIAMOND instalado en /usr/local/bin/diamond"

# Copiar código del proyecto (después de instalar dependencias)
COPY --chown=microbiome:microbiome . /home/microbiome/microbiome-pipeline

# Cambiar al directorio del proyecto
WORKDIR /home/microbiome/microbiome-pipeline

# Instalar el paquete en modo desarrollo (ahora SÍ tiene código)
# Usa src/ layout para evitar conflicto con 'configs/'
RUN pip install -e .

# Cambiar a usuario no-root
USER microbiome

# Volumen para datos y bases de datos
VOLUME ["/data", "/databases"]

# Entrypoint por defecto (permite ejecutar comandos directamente)
ENTRYPOINT []
CMD ["python"]