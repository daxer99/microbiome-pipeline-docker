
# microbiome-pipeline-docker

Es un flujo de trabajo completo capaz de obtener resultados de abundancia relativa de microorganismos, genes y rutas metabolicas de muestras de microbiota a partir de secuencias de material genetico.

Este pipeline permite procesar datos de metagenómica mediante una interfaz modular y reproducible. Está diseñado para ejecutar:

- Control de calidad (QC) con KneadData
- Clasificación taxonómica con MetaPhlAn4
- Perfilado funcional con HUMAnN3

## Requerimientos
- Sistema Operativo Linux (recomendado) o WSL2 en Windows
- Python: 3.8 o superior
- docker
- Espacio en disco: ~50 GB (para bases de datos)
- Sistema de gestion de versiones (GIT)

## Instalacion

1. Clonar el repositorio.
```bash
git clone https://github.com/daxer99/microbiome-pipeline-docker.git
cd microbiome-pipeline-docker
```
2. Construir imagen del entorno a partir del dockerfile.
```bash
docker build --no-cache -t microbiome-pipeline:latest .
```
3. Identificar adecuadamente las rutas de acceso a bases de datos y directorio de muestras en el host a la hora de definir los volumenes del contenedor en docker.

4. Crear e inicializar un contenedor a partir de la imagen creada, definiendo volumenes para las bases de datos y muestras a procesar
```bash
docker run --rm   
-u $(id -u):$(id -g)   
-v /home/user/samples:/data   
-v /media/user/dbs:/databases   
-v $(pwd)/config.yaml:/home/microbiome/microbiome-pipeline/config.yaml   microbiome-pipeline:latest   microbiome-cli --help
```
## Licencia

[MIT](https://choosealicense.com/licenses/mit/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)


## Autor

- [@Rodrigo Peralta](https://www.github.com/daxer99)

