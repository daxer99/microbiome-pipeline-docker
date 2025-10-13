FROM ubuntu:22.04

# Evitar preguntas interactivas durante la instalación
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    locales \
    && rm -rf /var/lib/apt/lists/*

# Configurar locale
RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Crear usuario microbiome
RUN useradd -m -s /bin/bash microbiome && \
    mkdir -p /home/microbiome/microbiome-pipeline && \
    chown -R microbiome:microbiome /home/microbiome

WORKDIR /home/microbiome

# Instalar Python 3.10 y herramientas básicas
RUN apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3-pip openjdk-17-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear entorno virtual
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instalar paquetes Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    kneaddata==0.12.3 \
    metaphlan==4.2.2 \
    humann==3.7 \
    biom-format==2.1.16 \
    numpy==1.24.3 \
    pandas==2.0.3 \
    click==8.1.7 \
    pyyaml==6.0

# PARCHEAR KNEADDATA - Reemplazar -Xmx500m con -Xmx8G
RUN find /opt/venv/lib/python3.10/site-packages/kneaddata -name "*.py" -type f -exec sed -i 's/-Xmx500m/-Xmx8G/g' {} \; && \
    find /opt/venv/lib/python3.10/site-packages/kneaddata -name "*.py" -type f -exec sed -i 's/"-Xmx500m"/"-Xmx8G"/g' {} \;

# Limpiar archivos innecesarios de kneaddata para reducir tamaño
RUN rm -rf /opt/venv/lib/python*/site-packages/kneaddata/java

# Instalar Trimmomatic
RUN mkdir -p /opt/trimmomatic && \
    curl -L -o Trimmomatic-0.40.zip "http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.40.zip" && \
    unzip Trimmomatic-0.40.zip -d /opt/trimmomatic && \
    rm Trimmomatic-0.40.zip

# Crear un wrapper mejorado para Java que sea más robusto
RUN mkdir -p /opt/bin && \
    echo '#!/bin/bash' > /opt/bin/java && \
    echo '# Wrapper para forzar memoria Java' >> /opt/bin/java && \
    echo 'for arg in "$@"; do' >> /opt/bin/java && \
    echo '  if [[ "$arg" == "-Xmx"* ]]; then' >> /opt/bin/java && \
    echo '    echo "⚠️  Sobrescribiendo opción de memoria: $arg con -Xmx8G"' >> /opt/bin/java && \
    echo '    continue' >> /opt/bin/java && \
    echo '  fi' >> /opt/bin/java && \
    echo '  NEW_ARGS+=("$arg")' >> /opt/bin/java && \
    echo 'done' >> /opt/bin/java && \
    echo 'echo "🔥 Ejecutando Java con -Xmx8G"' >> /opt/bin/java && \
    echo 'exec /usr/lib/jvm/java-17-openjdk-amd64/bin/java -Xmx8G "${NEW_ARGS[@]}"' >> /opt/bin/java && \
    chmod +x /opt/bin/java

# Asegurarse de que nuestro wrapper tenga prioridad
ENV PATH="/opt/bin:$PATH"

# Instalar DIAMOND para alignment rápido
RUN wget -O /tmp/diamond-linux64.tar.gz https://github.com/bbuchfink/diamond/releases/download/v2.1.8/diamond-linux64.tar.gz && \
    tar xzf /tmp/diamond-linux64.tar.gz -C /usr/local/bin && \
    rm /tmp/diamond-linux64.tar.gz

# Copiar código del pipeline
COPY --chown=microbiome:microbiome . /home/microbiome/microbiome-pipeline

WORKDIR /home/microbiome/microbiome-pipeline

# Instalar el pipeline en modo desarrollo
RUN pip install -e .

# Cambiar a usuario microbiome
USER microbiome

# Configurar variables de entorno para el usuario
ENV PATH="/opt/venv/bin:$PATH"
ENV JAVA_TOOL_OPTIONS="-Xmx8G"

CMD ["microbiome-cli", "--help"]