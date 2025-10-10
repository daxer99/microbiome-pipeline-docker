# microbiome_cli/qc.py
from .utils import run_cmd, find_fastq_pairs
import os


def run_qc(sample_dir, config):
    db = config["paths"]["kneaddata_db"]
    threads = config["tools"]["threads"]

    # Usar la función centralizada
    input1, input2 = find_fastq_pairs(sample_dir)

    print(f"✅ Archivos FASTQ encontrados:")
    print(f"   R1: {input1}")
    print(f"   R2: {input2}")

    output_dir = os.path.join(sample_dir, "kneaddata_output")
    os.makedirs(output_dir, exist_ok=True)

    TRIMMOMATIC_DIR = "/opt/trimmomatic"
    if not os.path.exists(TRIMMOMATIC_DIR):
        raise FileNotFoundError(f"No se encuentra Trimmomatic: {TRIMMOMATIC_DIR}")

    cmd = (
        f"kneaddata "
        f"--input1 {input1} --input2 {input2} "
        f"-db {db} "
        f"-t {threads} "
        f"-o {output_dir} "
        f"--trimmomatic {TRIMMOMATIC_DIR} "
        f"--run-fastqc-start --run-fastqc-end "
        f"--bypass-trf"
    )

    print(f"🔍 QC: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")