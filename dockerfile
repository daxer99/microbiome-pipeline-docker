# Dockerfile
FROM biocontainers/kneaddata:v0.12.0_cv1

LABEL maintainer="rodrigo.peralta@uner.edu.ar"
LABEL org.opencontainers.image.source="https://github.com/daxer99/microbiome-pipeline-docker"

# Cambiar a usuario root para instalar más herramientas
USER root

# Instalar Python 3.10 + pip (ya está en biocontainers, pero aseguramos)
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Crear entorno virtual
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar MetaPhlAn y HUMAnN
RUN pip install metaphlan==4.2.2 humann==3.9 biopython pandas pyyaml

# Copiar código del proyecto
COPY . /home/biodocker/microbiome-pipeline

# Activar entorno virtual por defecto
ENV PYTHONPATH="/home/biodocker/microbiome-pipeline:$PYTHONPATH"

# Cambiar a usuario biodocker (usuario por defecto en biocontainers)
USER biodocker
WORKDIR /home/biodocker/microbiome-pipeline

# Instalar tu paquete
RUN pip install -e .

# Volumen para datos
VOLUME ["/data", "/databases"]

# Entrypoint y comando
ENTRYPOINT []
CMD ["python"]