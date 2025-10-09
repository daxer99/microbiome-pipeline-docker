# Dockerfile
FROM quay.io/biocontainers/kneaddata:0.12.0--pyhdfd78af_1

LABEL maintainer="rodrigo.peralta@uner.edu.ar"
LABEL org.opencontainers.image.source="https://github.com/daxer99/microbiome-pipeline-docker"

# Copiar código del proyecto
COPY . /home/biodocker/microbiome-pipeline

# Activar micromamba
SHELL ["/bin/bash", "-c"]
RUN eval "$(micromamba shell hook -s bash)" && \
    micromamba activate base

# Instalar MetaPhlAn y HUMAnN via conda
RUN micromamba install -y \
    metaphlan=4.2.2 \
    humann=3.9 && \
    echo "✅ MetaPhlAn y HUMAnN instalados"

# Cambiar a usuario biodocker (usuario por defecto en biocontainers)
USER biodocker

# Establecer PYTHONPATH
ENV PYTHONPATH="/home/biodocker/microbiome-pipeline:$PYTHONPATH"

# Ir al directorio del proyecto
WORKDIR /home/biodocker/microbiome-pipeline

# Instalar tu paquete en modo desarrollo
RUN pip install -e .

# Volumen para datos
VOLUME ["/data", "/databases"]

# Entrypoint y comando
ENTRYPOINT []
CMD ["python"]