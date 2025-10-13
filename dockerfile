# Dockerfile
FROM ubuntu:22.04

LABEL maintainer="rodrigo.peralta@uner.edu.ar"
LABEL org.opencontainers.image.source="https://github.com/daxer99/microbiome-pipeline-docker"

ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC

# Instalar herramientas básicas (ahora incluye 'unzip')
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
ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

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

# Entorno virtual
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

# --- ELIMINAR VERSION INTERNA DE KNEADDATA ---
RUN rm -rf /opt/venv/lib/python*/site-packages/kneaddata/java/Trimmomatic-* && \
    echo "✅ Eliminado Trimmomatic interno empaquetado"

# --- INSTALAR TRIMMOMATIC DESDE GITHUB ---
ENV TRIMMOMATIC_DIR=/opt/trimmomatic
RUN mkdir -p $TRIMMOMATIC_DIR && \
    curl -L -o Trimmomatic-0.40.zip \
         "https://github.com/usadellab/Trimmomatic/releases/download/v0.40/Trimmomatic-0.40.zip" && \
    unzip Trimmomatic-0.40.zip -d $TRIMMOMATIC_DIR && \
    rm Trimmomatic-0.40.zip && \
    echo "✅ Trimmomatic instalado en $TRIMMOMATIC_DIR"

# --- CREAR WRAPPER PARA JAVA CON MÁS MEMORIA ---
RUN mkdir -p /opt/bin && \
    echo '#!/bin/bash' > /opt/bin/java && \
    echo 'echo "WRAPPER: Ejecutando Java con -Xmx8g"' >> /opt/bin/java && \
    echo 'exec /usr/lib/jvm/java-17-openjdk-amd64/bin/java -Xmx8g "$@"' >> /opt/bin/java && \
    chmod +x /opt/bin/java

# Prioridad al wrapper de java
ENV PATH="/opt/bin:$PATH"

# --- INSTALAR DIAMOND ---
RUN wget -O /tmp/diamond-linux64.tar.gz https://github.com/bbuchfink/diamond/releases/download/v2.1.8/diamond-linux64.tar.gz && \
    tar -xzf /tmp/diamond-linux64.tar.gz -C /tmp && \
    mv /tmp/diamond /usr/local/bin/diamond && \
    chmod +x /usr/local/bin/diamond && \
    rm -rf /tmp/diamond-linux64.tar.gz

# Copiar código del proyecto
COPY --chown=microbiome:microbiome . /home/microbiome/microbiome-pipeline

# Cambiar al directorio del proyecto
WORKDIR /home/microbiome/microbiome-pipeline

# Instalar el paquete en modo desarrollo
RUN pip install -e .

# Cambiar a usuario no-root
USER microbiome

# Volumen para datos y bases de datos
VOLUME ["/data", "/databases"]

# Entrypoint por defecto
ENTRYPOINT []
CMD ["python"]