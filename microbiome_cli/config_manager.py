# microbiome_cli/config_manager.py
import yaml
from pathlib import Path


def find_repo_root():
    """
    Devuelve la raíz esperada dentro del contenedor Docker.
    Fuera del contenedor, puedes modificar esta función si es necesario.
    """
    # Ruta fija dentro del contenedor
    container_root = Path("/home/microbiome/microbiome-pipeline")
    if container_root.is_dir():
        return container_root

    # Fallback: buscar pyproject.toml (para desarrollo local)
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists() or (current / ".git").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("No se encontró la raíz del repositorio")


def load_config(config_file="config.yaml"):
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as e:
        raise RuntimeError(f"❌ Error: {e}") from e

    config_path = repo_root / config_file

    if not config_path.exists():
        raise FileNotFoundError(
            f"❌ No se encuentra el archivo de configuración: {config_path}\n"
            "Por favor, asegúrate de montarlo en el contenedor.\n"
            "Ejemplo:\n"
            "  -v $(pwd)/config.yaml:/home/microbiome/microbiome-pipeline/config.yaml"
        )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            print(f"🔧 Configuración cargada desde: {config_path}")
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Error al leer {config_path}: {e}") from e