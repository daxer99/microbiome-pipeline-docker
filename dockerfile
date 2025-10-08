# Dockerfile
FROM ubuntu:22.04

LABEL maintainer="rodrigo.peralta@uner.edu.ar"
LABEL org.opencontainers.image.source="https://github.com/daxer99/microbiome-pipeline-docker"

# Evitar preguntas durante instalación
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC

# Instalar herramientas básicas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jre \
        ca-certificates \
        curl \
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
RUN chown -R microbiome:microbiome /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar herramientas bioinformáticas desde pip
RUN pip install \
    kneaddata==0.12.3 \
    metaphlan==4.2.2 \
    humann==3.9 \
    biopython \
    pandas \
    pyyaml

# Copiar código del proyecto
COPY --chown=microbiome:microbiome . /home/microbiome/microbiome-pipeline

# Activar entorno virtual por defecto
ENV PYTHONPATH="/home/microbiome/microbiome-pipeline:$PYTHONPATH"

# Cambiar a usuario no-root
USER microbiome
WORKDIR /home/microbiome/microbiome-pipeline

# Instalar el paquete en modo desarrollo
RUN pip install -e .

# Volumen para datos
VOLUME ["/data", "/databases"]

# Entrypoint y comando
ENTRYPOINT []
CMD ["python"]