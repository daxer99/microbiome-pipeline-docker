# microbiome_cli/config_manager.py
import yaml
from pathlib import Path

def find_repo_root():
    return Path("/home/microbiome/microbiome-pipeline")


def load_config(config_file="config.yaml"):
    """
    Carga el config.yaml desde la raíz del repositorio.
    El archivo DEBE existir. No se crea automáticamente.
    """
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de estar dentro del proyecto.")
        exit(1)

    config_path = repo_root / config_file

    if not config_path.exists():
        print(f"❌ Error: No se encuentra el archivo de configuración: {config_path}")
        print("Por favor, crea un archivo 'config.yaml' en la raíz del repositorio.")
        print("Puedes usar este ejemplo como base:")
        print("""
paths:
  kneaddata_db: "/ruta/a/kneaddata_db"
  metaphlan_db: "/ruta/a/metaphlan_db"
  humann_nucleotide_db: "/ruta/a/chocophlan"
  humann_protein_db: "/ruta/a/uniref"
  humann_go_db: "/ruta/a/utility_mapping/map_go_uniref90.txt.gz"
  humann_ko_db: "/ruta/a/utility_mapping/map_ko_uniref90.txt.gz"
  humann_ec_db: "/ruta/a/utility_mapping/map_level4ec_uniref90.txt.gz"
  humann_pfam_db: "/ruta/a/utility_mapping/map_pfam_uniref90.txt.gz"
  humann_eggnog_db: "/ruta/a/utility_mapping/map_eggnog_uniref90.txt.gz"

tools:
  threads: 8
  kneaddata_env: microbiome-pipeline
  metaphlan_env: microbiome-pipeline
  humann3_env: microbiome-pipeline

samples_dir: "/ruta/a/muestras"
        """)
        exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            print(f"🔧 Configuración cargada desde: {config_path}")
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error al leer {config_path}: {e}")
        exit(1)