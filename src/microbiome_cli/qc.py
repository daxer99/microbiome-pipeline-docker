# microbiome_cli/qc.py
from .utils import find_fastq_pairs
import os
import subprocess


def run_qc(sample_dir, config):
    db = config["paths"]["kneaddata_db"]
    threads = config["tools"]["threads"]

    input1, input2 = find_fastq_pairs(sample_dir)

    print(f"✅ Archivos FASTQ encontrados:")
    print(f"   R1: {input1}")
    print(f"   R2: {input2}")

    output_dir = os.path.join(sample_dir, "kneaddata_output")
    os.makedirs(output_dir, exist_ok=True)

    TRIMMOMATIC_DIR = "/opt/trimmomatic"

    # ✅ Usar --trimmomatic-options=-valor para evitar parsing erróneo
    cmd = [
        "kneaddata",
        "--input1", input1,
        "--input2", input2,
        "-db", db,
        "-t", str(threads),
        "-o", output_dir,
        "--trimmomatic", TRIMMOMATIC_DIR,
        "--trimmomatic-options=-Xmx12g",
        "--run-fastqc-start",
        "--run-fastqc-end",
        "--bypass-trf"
    ]

    print(f"🔍 QC: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")