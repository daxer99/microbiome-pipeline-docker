# Dockerfile
FROM mambaorg/micromamba:1.5

LABEL maintainer="rodrigo.peralta@uner.edu.ar"
LABEL org.opencontainers.image.source="https://github.com/daxer99/microbiome-pipeline-docker"

# Configurar usuario no-root
USER root
RUN useradd -m -s /bin/bash microbiome && \
    mkdir -p /home/microbiome/work && \
    chown -R microbiome:microbiome /home/microbiome && \
    micromamba clean --all

# Cambiar a usuario no-root
USER microbiome
WORKDIR /home/microbiome

# Copiar environment.yml
COPY --chown=microbiome:microbiome environment.yml /tmp/environment.yml

# Crear entorno microbiome-pipeline
RUN micromamba create -n microbiome-pipeline -f /tmp/environment.yml && \
    echo "micromamba activate microbiome-pipeline" > ~/.bashrc

# Activar entorno por defecto
SHELL ["/usr/bin/micromamba", "run", "-n", "microbiome-pipeline", "/bin/bash", "-c"]
ENV CONDA_DEFAULT_ENV=microbiome-pipeline

# Establecer MAMBA_ROOT_PREFIX (ubicación predeterminada de micromamba)
ENV MAMBA_ROOT_PREFIX=/opt/conda

# Instalar humann desde pip (como solicitaste)
RUN pip install humann==3.9

# Copiar el código del proyecto
COPY --chown=microbiome:microbiome . /home/microbiome/microbiome-pipeline

# Instalar el paquete en modo desarrollo
RUN pip install -e /home/microbiome/microbiome-pipeline

# Volumen para datos y resultados
VOLUME ["/data", "/results"]

# Directorio de trabajo por defecto
WORKDIR /home/microbiome/microbiome-pipeline

# Entrypoint: asegura que el entorno esté activo
ENTRYPOINT ["micromamba", "run", "-n", "microbiome-pipeline"]

# Comando por defecto
CMD ["bash"]