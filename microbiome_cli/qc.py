# microbiome_cli/qc.py
import subprocess
import os


def run_qc(sample_dir, config):
    db = config["paths"]["kneaddata_db"]
    threads = config["tools"]["threads"]

    input1 = os.path.join(sample_dir, "R1.fastq")
    input2 = os.path.join(sample_dir, "R2.fastq")

    if not os.path.exists(input1) or not os.path.exists(input2):
        raise FileNotFoundError(f"No se encontraron los archivos FASTQ en {sample_dir}")

    output_dir = os.path.join(sample_dir, "kneaddata_output")
    os.makedirs(output_dir, exist_ok=True)

    # Ruta al directorio de Trimmomatic (no al .jar)
    TRIMMOMATIC_DIR = "/opt/trimmomatic"
    if not os.path.exists(TRIMMOMATIC_DIR):
        raise FileNotFoundError(f"No se encuentra el directorio de Trimmomatic: {TRIMMOMATIC_DIR}")

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