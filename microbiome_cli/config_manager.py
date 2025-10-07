# microbiome_cli/config_manager.py
import yaml
from pathlib import Path


def find_repo_root():
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists() or (current / ".git").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("No se encontró la raíz del repositorio")


def load_config(config_file="config.yaml"):
    """
    Carga el config.yaml desde la raíz del repositorio.
    Si no existe, lanza una excepción (que será manejada por el CLI).
    """
    try:
        repo_root = find_repo_root()
    except FileNotFoundError as e:
        raise RuntimeError(f"❌ Error: {e}") from e

    config_path = repo_root / config_file

    if not config_path.exists():
        raise FileNotFoundError(
            f"❌ No se encuentra el archivo de configuración: {config_path}\n"
            "Por favor, crea un 'config.yaml' en la raíz del repositorio.\n"
            "Puedes usar el ejemplo del README."
        )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            print(f"🔧 Configuración cargada desde: {config_path}")
            return yaml.safe_load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Error al leer {config_path}: {e}") from e