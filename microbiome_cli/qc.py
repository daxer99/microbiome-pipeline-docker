# microbiome_cli/qc.py
import subprocess
import os


def run_qc(sample_dir, config):
    db = config["paths"]["kneaddata_db"]
    threads = config["tools"]["threads"]

    # Asegurarse de que las rutas de entrada existen
    input1 = os.path.join(sample_dir, "R1.fastq")
    input2 = os.path.join(sample_dir, "R2.fastq")

    if not os.path.exists(input1) or not os.path.exists(input2):
        raise FileNotFoundError(f"No se encontraron los archivos FASTQ en {sample_dir}")

    output_dir = os.path.join(sample_dir, "kneaddata_output")
    os.makedirs(output_dir, exist_ok=True)

    # Ruta fija a trimmomatic.jar
    TRIMMOMATIC_JAR = "/opt/trimmomatic/trimmomatic.jar"
    if not os.path.exists(TRIMMOMATIC_JAR):
        raise FileNotFoundError(f"No se encuentra trimmomatic.jar: {TRIMMOMATIC_JAR}")

    cmd = (
        f"kneaddata "
        f"--input {input1} --input {input2} "
        f"-db {db} "
        f"-t {threads} "
        f"-o {output_dir} "
        f"--trimmomatic {TRIMMOMATIC_JAR} "
        f"--run-fastqc-start --run-fastqc-end"
    )

    print(f"🔍 QC: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")