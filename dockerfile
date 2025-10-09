FROM quay.io/biocontainers/kneaddata:0.12.0--pyhdfd78af_1

LABEL maintainer="rodrigo.peralta@uner.edu.ar"

USER root

# Instalar Python y pip si no están presentes
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Instalar MetaPhlAn y HUMAnN
RUN pip3 install metaphlan==4.2.2 humann==3.9 pyyaml pandas biopython

# Copiar tu código
COPY . /home/biodocker/microbiome-pipeline
WORKDIR /home/biodocker/microbiome-pipeline

# Instalar tu CLI
RUN pip3 install -e .

# Cambiar a usuario biodocker
USER biodocker

# Entrypoint
ENTRYPOINT ["python"]