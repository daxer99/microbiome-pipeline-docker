#!/bin/bash
set -e

echo "📁 Creando directorios..."
mkdir -p databases/{kneaddata,metaphlan,chocophlan,uniref,utility_mapping}

echo "⬇️ Descargando KneadData (hg37)..."
docker run --rm --user root \
  -v $(pwd)/databases/kneaddata:/db \
  microbiome-pipeline:latest \
  sh -c "chown -R microbiome:microbiome /db && \
         micromamba run -n microbiome-pipeline kneaddata_database --download human_genome bowtie2 /db"

echo "⬇️ Descargando MetaPhlAn..."
docker run --rm --user root \
  -v $(pwd)/databases/metaphlan:/db \
  microbiome-pipeline:latest \
  sh -c "chown -R microbiome:microbiome /db && \
         micromamba run -n microbiome-pipeline metaphlan --install --index mpa_vJun23_CHOCOPhlAnSGB_202307 --db_dir /db"

echo "⬇️ Descargando ChocoPhlAn..."
docker run --rm --user root \
  -v $(pwd)/databases/chocophlan:/db \
  microbiome-pipeline:latest \
  sh -c "chown -R microbiome:microbiome /db && \
         micromamba run -n microbiome-pipeline humann_databases --download chocophlan full /db"

echo "⬇️ Descargando UniRef90..."
docker run --rm --user root \
  -v $(pwd)/databases/uniref:/db \
  microbiome-pipeline:latest \
  sh -c "chown -R microbiome:microbiome /db && \
         micromamba run -n microbiome-pipeline humann_databases --download uniref uniref90_diamond /db"

echo "⬇️ Descargando Utility Mapping..."
docker run --rm --user root \
  -v $(pwd)/databases/utility_mapping:/db \
  microbiome-pipeline:latest \
  sh -c "chown -R microbiome:microbiome /db && \
         micromamba run -n microbiome-pipeline humann_databases --download utility_mapping full /db"

echo "✅ Todas las bases de datos descargadas en: $(pwd)/databases"