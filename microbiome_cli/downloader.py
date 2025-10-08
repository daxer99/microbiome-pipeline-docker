# microbiome_cli/downloader.py
"""
Script para descargar bases de datos necesarias para el pipeline.
"""
import sys
from pathlib import Path
import subprocess


def download_kneaddata(db_dir):
    """Descarga la base de datos de KneadData (hg37)"""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    print("⬇️ Descargando KneadData (hg37)...")
    cmd = f"kneaddata_database --download human_genome bowtie2 {db_dir}"
    run_cmd(cmd)
    print(f"✅ Base de datos guardada en: {db_dir}")


def download_metaphlan(db_dir):
    """Descarga la base de datos de MetaPhlAn"""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    print("⬇️ Descargando MetaPhlAn...")
    cmd = f"metaphlan --install --index mpa_vJun23_CHOCOPhlAnSGB_202307 --db_dir {db_dir}"
    run_cmd(cmd)
    print(f"✅ Base de datos guardada en: {db_dir}")


def download_chocophlan(db_dir):
    """Descarga ChocoPhlAn (nucleótidos)"""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    print("⬇️ Descargando ChocoPhlAn...")
    cmd = f"humann_databases --download chocophlan full {db_dir}"
    run_cmd(cmd)
    print(f"✅ Base de datos guardada en: {db_dir}")


def download_uniref(db_dir):
    """Descarga UniRef90 (proteínas)"""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    print("⬇️ Descargando UniRef90...")
    cmd = f"humann_databases --download uniref uniref90_diamond {db_dir}"
    run_cmd(cmd)
    print(f"✅ Base de datos guardada en: {db_dir}")


def download_utility_mapping(db_dir):
    """Descarga los mapas de utilidad (KO, GO, EC, etc.)"""
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    print("⬇️ Descargando Utility Mapping...")
    cmd = f"humann_databases --download utility_mapping full {db_dir}"
    run_cmd(cmd)
    print(f"✅ Base de datos guardada en: {db_dir}")


def run_cmd(cmd):
    """Ejecuta un comando y maneja errores."""
    print(f"🔧 Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Error al ejecutar: {cmd}")
        sys.exit(1)


# Mapeo de comandos
DOWNLOADERS = {
    "kneaddata": download_kneaddata,
    "metaphlan": download_metaphlan,
    "chocophlan": download_chocophlan,
    "uniref": download_uniref,
    "utility-mapping": download_utility_mapping,
}