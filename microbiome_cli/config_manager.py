# microbiome_cli/config_manager.py
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "paths": {
        "kneaddata_db": "",
        "metaphlan_db": "",
        "humann_nucleotide_db": "",
        "humann_protein_db": "",
        "humann_go_db": "",
        "humann_ko_db": "",
        "humann_ec_db": "",
        "humann_pfam_db": "",
        "humann_eggnog_db": ""
    },
    "tools": {
        "threads": 8,
        "kneaddata_env": "microbiome-pipeline",
        "metaphlan_env": "microbiome-pipeline",
        "humann3_env": "microbiome-pipeline"
    },
    "samples_dir": ""
}

def load_config(config_file="config.yaml"):
    path = Path(config_file)
    if not path.exists():
        create_default_config(config_file)
        print(f"✅ Archivo {config_file} creado con valores por defecto.")
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def create_default_config(config_file="config.yaml"):
    with open(config_file, 'w') as f:
        yaml.dump(DEFAULT_CONFIG, f, indent=2, sort_keys=False)

def update_config(key, value, config_file="config.yaml"):
    config = load_config(config_file)
    keys = key.split('.')
    d = config
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = str(Path(value).resolve())
    with open(config_file, 'w') as f:
        yaml.dump(config, f, indent=2, sort_keys=False)
    print(f"✅ {key} actualizado a: {value}")