# microbiome_cli/config_manager.py
import yaml
from pathlib import Path

def load_config(config_file="config.yaml"):
    config_path = Path("/home/microbiome/microbiome-pipeline") / config_file
    if not config_path.exists():
        raise FileNotFoundError(f"No se encuentra {config_path}. Asegúrate de montarlo.")
    print(f"🔧 Config cargada desde: {config_path}")
    return yaml.safe_load(config_path.read_text(encoding='utf-8'))