# src/microbiome_cli/utils.py
import subprocess
import os
import glob


def run_cmd(cmd):
    """Ejecuta un comando shell."""
    print(f"🔧 Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")


def find_fastq_pairs(sample_dir):
    """Encuentra pares R1/R2 en cualquier formato común."""
    patterns = [
        ("*_R1*.fastq", "*_R2*.fastq"),
        ("*R1*.fastq", "*R2*.fastq"),
        ("*_1*.fastq", "*_2*.fastq"),
        ("*1*.fastq", "*2*.fastq")
    ]
    for r1_pat, r2_pat in patterns:
        r1_files = sorted(glob.glob(os.path.join(sample_dir, r1_pat)))
        r2_files = sorted(glob.glob(os.path.join(sample_dir, r2_pat)))
        if r1_files and r2_files:
            return r1_files[0], r2_files[0]
    raise FileNotFoundError(f"No se encontraron pares FASTQ en {sample_dir}")