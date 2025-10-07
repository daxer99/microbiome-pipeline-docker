# microbiome_cli/config_manager.py
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "paths": {
        "kneaddata_db": "/ruta/a/kneaddata_db",
        "metaphlan_db": "/ruta/a/metaphlan_db",
        "humann_nucleotide_db": "/ruta/a/chocophlan",
        "humann_protein_db": "/ruta/a/uniref",
        "humann_go_db": "/ruta/a/utility_mapping/map_go_uniref90.txt.gz",
        "humann_ko_db": "/ruta/a/utility_mapping/map_ko_uniref90.txt.gz",
        "humann_ec_db": "/ruta/a/utility_mapping/map_level4ec_uniref90.txt.gz",
        "humann_pfam_db": "/ruta/a/utility_mapping/map_pfam_uniref90.txt.gz",
        "humann_eggnog_db": "/ruta/a/utility_mapping/map_eggnog_uniref90.txt.gz"
    },
    "tools": {
        "threads": 8,
        "kneaddata_env": "microbiome-pipeline",
        "metaphlan_env": "microbiome-pipeline",
        "humann3_env": "microbiome-pipeline"
    },
    "samples_dir": "/ruta/a/muestras"
}

def find_repo_root():
    """
    Busca la raíz del repositorio buscando 'pyproject.toml' o '.git'.
    Comienza desde el directorio actual y sube hasta encontrarlo.
    """
    current = Path.cwd()
    # Puedes agregar más indicadores si lo deseas: 'setup.py', 'Dockerfile', etc.
    while current != current.parent:
        if (current / "pyproject.toml").exists() or (current / ".git").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("No se encontró la raíz del repositorio (falta pyproject.toml o .git)")

def load_config(config_file="config.yaml"):
    """
    Carga el config.yaml desde la raíz del repositorio.
    """
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de estar en un subdirectorio del repositorio.")
        exit(1)

    config_path = repo_root / config_file

    if not config_path.exists():
        create_default_config(config_path)
        print(f"✅ {config_file} creado en: {config_path}")
        print("📌 Ábrelo con un editor de texto y ajusta las rutas antes de continuar.")
        exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            print(f"🔧 Configuración cargada desde: {config_path}")
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error al leer {config_path}: {e}")
        exit(1)


def create_default_config(config_path):
    """Crea un config.yaml por defecto en la raíz del repositorio"""
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(DEFAULT_CONFIG, f, indent=2, sort_keys=False, allow_unicode=True)