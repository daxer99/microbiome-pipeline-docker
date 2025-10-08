# microbiome_cli/qc.py
import subprocess
import os
import kneaddata


def run_qc(sample_dir, config):
    db = config["paths"]["kneaddata_db"]
    threads = config["tools"]["threads"]

    # Entradas
    input1 = os.path.join(sample_dir, "R1.fastq")
    input2 = os.path.join(sample_dir, "R2.fastq")

    if not os.path.exists(input1) or not os.path.exists(input2):
        raise FileNotFoundError(f"No se encontraron los archivos FASTQ en {sample_dir}")

    output_dir = os.path.join(sample_dir, "kneaddata_output")
    os.makedirs(output_dir, exist_ok=True)

    # Obtener la ruta al trimmomatic.jar incluido en kneaddata
    try:
        KNEDDATA_PATH = os.path.dirname(kneaddata.__file__)
        TRIMMOMATIC_JAR_DIR = os.path.join(KNEDDATA_PATH, "trimmomatic")
        if not os.path.exists(TRIMMOMATIC_JAR_DIR):
            raise FileNotFoundError(f"No se encuentra el directorio de Trimmomatic: {TRIMMOMATIC_JAR_DIR}")
    except Exception as e:
        raise RuntimeError(f"Error al encontrar Trimmomatic: {e}")

    cmd = (
        f"kneaddata "
        f"--input {input1} --input {input2} "
        f"-db {db} "
        f"-t {threads} "
        f"-o {output_dir} "
        f"--trimmomatic {TRIMMOMATIC_JAR_DIR} "
        f"--run-fastqc-start --run-fastqc-end"
    )

    print(f"🔍 QC: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")