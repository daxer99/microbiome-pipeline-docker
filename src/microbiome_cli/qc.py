# microbiome_cli/qc.py
from .utils import run_cmd
import os
import subprocess
import glob


def run_qc(sample_dir, config):
    db = config["paths"]["kneaddata_db"]
    threads = config["tools"]["threads"]

    # Buscar archivos automáticamente
    r1_files = sorted(glob.glob(os.path.join(sample_dir, "*_R1*.fastq")))
    r2_files = sorted(glob.glob(os.path.join(sample_dir, "*_R2*.fastq")))

    if not r1_files or not r2_files:
        raise FileNotFoundError(
            f"No se encontraron archivos *_R1*.fastq o *_R2*.fastq en {sample_dir}"
        )

    input1 = r1_files[0]
    input2 = r2_files[0]

    print(f"✅ Archivos FASTQ encontrados:")
    print(f"   R1: {input1}")
    print(f"   R2: {input2}")

    output_dir = os.path.join(sample_dir, "kneaddata_output")
    os.makedirs(output_dir, exist_ok=True)

    TRIMMOMATIC_DIR = "/opt/trimmomatic"

    # ✅ Usar lista de argumentos para evitar problemas de parsing
    cmd = [
        "kneaddata",
        "--input1", input1,
        "--input2", input2,
        "-db", db,
        "-t", str(threads),
        "-o", output_dir,
        "--trimmomatic", TRIMMOMATIC_DIR,
        "--trimmomatic-options", "-Xmx12g",  # ← Separado: clave para que funcione
        "--run-fastqc-start",
        "--run-fastqc-end",
        "--bypass-trf"
    ]

    print(f"🔍 QC: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")