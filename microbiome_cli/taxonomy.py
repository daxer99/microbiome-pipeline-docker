# microbiome_cli/taxonomy.py
import subprocess
import os


def run_taxonomy(sample_dir, config):
    """
    Ejecuta MetaPhlAn para clasificación taxonómica.
    """
    db = config["paths"]["metaphlan_db"]
    nproc = config["tools"]["threads"]  # Usa threads desde config

    # Entrada: salida de QC (R1 paired fastq)
    input_pattern = os.path.join(sample_dir, "kneaddata_output", "*_R1_kneaddata_paired*.fastq")
    output_dir = os.path.join(sample_dir, "taxonomy")
    os.makedirs(output_dir, exist_ok=True)
    profile_path = os.path.join(output_dir, "profile.txt")

    cmd = (
        f"metaphlan "
        f"{input_pattern} "
        f"--input_type fastq "
        f"--db {db} "
        f"--nproc {nproc} "           # ← ¡Cambiado de --threads a --nproc!
        f"--output {profile_path}"
    )

    print(f"🧬 Taxonomía: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

    # Generar gráfico opcional
    plot_path = os.path.join(output_dir, "profile_plot.png")
    plot_cmd = (
        f"metaphlan "
        f"{profile_path} "
        f"--plot_type bar --width 8 --height 6 --dpi 300 "
        f"--out_file {plot_path}"
    )
    subprocess.run(plot_cmd, shell=True, check=False)