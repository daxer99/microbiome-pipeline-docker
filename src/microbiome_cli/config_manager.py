# microbiome_cli/config_manager.py
import yaml
from pathlib import Path

def load_config(config_file="config.yaml"):
    """
    Carga el config.yaml desde una ubicación fija dentro del contenedor.
    """
    config_path = Path("/home/microbiome/microbiome-pipeline") / config_file
    if not config_path.exists():
        raise FileNotFoundError(
            f"❌ No se encuentra el archivo de configuración: {config_path}\n"
            "Asegúrate de montarlo correctamente.\n"
            "Ejemplo:\n"
            "  -v $(pwd)/config.yaml:/home/microbiome/microbiome-pipeline/config.yaml"
        )
    print(f"🔧 Config cargada desde: {config_path}")
    return yaml.safe_load(config_path.read_text(encoding='utf-8'))