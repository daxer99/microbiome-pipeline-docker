# microbiome_cli/downloader.py
import subprocess
import sys
from .config_manager import update_config


def run_cmd(cmd):
    """Ejecuta un comando y muestra salida"""
    print(f"🔧 Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error al ejecutar: {cmd}")
        sys.exit(1)


def download_kneaddata(db_dir):
    db_dir = str(db_dir)
    run_cmd(f"conda run -n microbiome-pipeline kneaddata_database --download human_genome bowtie2 {db_dir}")
    update_config("paths.kneaddata_db", db_dir)


def download_metaphlan(db_dir):
    db_dir = str(db_dir)
    run_cmd(
        f"conda run -n microbiome-pipeline metaphlan --install --index mpa_vJun23_CHOCOPhlAnSGB_202307 --db_dir {db_dir}")
    update_config("paths.metaphlan_db", db_dir)


def download_chocophlan(db_dir):
    db_dir = str(db_dir)
    run_cmd(f"conda run -n microbiome-pipeline humann_databases --download chocophlan full {db_dir}")
    update_config("paths.humann_nucleotide_db", db_dir)


def download_uniref(db_dir):
    db_dir = str(db_dir)
    run_cmd(f"conda run -n microbiome-pipeline humann_databases --download uniref uniref90_diamond {db_dir}")
    update_config("paths.humann_protein_db", db_dir)


def download_utility_mapping(db_dir):
    db_dir = str(db_dir)
    run_cmd(f"conda run -n microbiome-pipeline humann_databases --download utility_mapping full {db_dir}")

    # Actualizar rutas internas de utility_mapping
    base = Path(db_dir) / "utility_mapping"
    update_config("paths.humann_go_db", base / "map_go_uniref90.txt.gz")
    update_config("paths.humann_ko_db", base / "map_ko_uniref90.txt.gz")
    update_config("paths.humann_ec_db", base / "map_level4ec_uniref90.txt.gz")
    update_config("paths.humann_pfam_db", base / "map_pfam_uniref90.txt.gz")
    update_config("paths.humann_eggnog_db", base / "map_eggnog_uniref90.txt.gz")


# Mapeo de comandos
DOWNLOADERS = {
    "kneaddata": download_kneaddata,
    "metaphlan": download_metaphlan,
    "humann-chocophlan": download_chocophlan,
    "humann-uniref": download_uniref,
    "utility-mapping": download_utility_mapping,
}