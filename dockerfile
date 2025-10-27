FROM mambaorg/micromamba:1.5.1

USER root

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    gcc \
    g++ \
    make \
    openjdk-17-jdk \
    gzip \
    bzip2 \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 -s /bin/bash microbiome && \
    mkdir -p /home/microbiome && \
    chown -R microbiome:microbiome /home/microbiome

# Crear directorios para bases de datos y darles permisos amplios
RUN mkdir -p /databases /data && \
    chmod -R 777 /databases /data

USER microbiome
WORKDIR /home/microbiome

# Configurar micromamba
ENV MAMBA_USER=microbiome
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV PATH=/opt/conda/bin:$PATH

# Crear environment de conda con todas las herramientas
RUN micromamba create -n pipeline -c conda-forge -c bioconda -c defaults -y \
    python=3.9 \
    kneaddata=0.12.0 \
    metaphlan=4.1.1 \
    humann=3.9 \
    bowtie2=2.5.1 \
    trimmomatic=0.39 \
    trf=4.09.1 \
    samtools=1.18 \
    click=8.1.7 \
    pyyaml=6.0 \
    pandas=2.1.3 \
    biopython=1.81 \
    && micromamba clean -a -y

# Activar el environment
ENV PATH=/opt/conda/envs/pipeline/bin:$PATH
ENV CONDA_DEFAULT_ENV=pipeline
SHELL ["/bin/bash", "-c"]

# Copiar código del proyecto
COPY --chown=microbiome:microbiome . /home/microbiome/microbiome-pipeline/

# Instalar el paquete
RUN cd /home/microbiome/microbiome-pipeline && \
    /opt/conda/envs/pipeline/bin/pip install -e .

# Variables de entorno para HUMAnN3
# Estas variables permiten que HUMAnN encuentre las bases de datos sin necesidad de configurar archivos
ENV HUMANN_NUCLEOTIDE_DATABASE=/databases/chocophlan
ENV HUMANN_PROTEIN_DATABASE=/databases/uniref

# Configuración de directorios de trabajo
WORKDIR /home/microbiome/microbiome-pipeline

# El contenedor puede correr con cualquier usuario gracias a los permisos 777
# No necesitamos cambiar permisos de archivos de configuración de HUMAnN
# porque pasaremos las rutas directamente como parámetros

# Punto de entrada
ENTRYPOINT ["/opt/conda/envs/pipeline/bin/python", "-m", "microbiome_pipeline.cli"]
CMD ["--help"]