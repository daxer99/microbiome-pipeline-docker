# Dockerfile
FROM mambaorg/micromamba:1.5

LABEL maintainer="rodrigo.peralta@uner.edu.ar"

# Crear usuario no-root
USER root
RUN useradd -m -s /bin/bash microbiome && \
    mkdir -p /home/microbiome/work && \
    chown -R microbiome:microbiome /home/microbiome

# Cambiar a usuario no-root
USER microbiome
WORKDIR /home/microbiome

# Copiar environment.yml
COPY --chown=microbiome:microbiome environment.yml /tmp/environment.yml

# Crear entorno sin inicializar micromamba en el shell
RUN micromamba create -n microbiome-pipeline -f /tmp/environment.yml && \
    echo "Micromamba installed, but NOT auto-activated." > ~/.bashrc

# Establecer PATH directamente (clave)
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV PATH=/opt/conda/envs/microbiome-pipeline/bin:$PATH

# Instalar humann desde pip
RUN pip install humann==3.9

# Copiar código del proyecto
COPY --chown=microbiome:microbiome . /home/microbiome/microbiome-pipeline

# Instalar el paquete DENTRO del entorno, usando python directamente
RUN micromamba run -n microbiome-pipeline python -m pip install -e /home/microbiome/microbiome-pipeline

# Volumen para datos
VOLUME ["/data", "/databases"]

# Directorio de trabajo
WORKDIR /home/microbiome/microbiome-pipeline

# Entrypoint: evita activar el entorno
ENTRYPOINT ["sh", "-c"]
CMD ["exec bash"]