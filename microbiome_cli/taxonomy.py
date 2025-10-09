# microbiome_cli/taxonomy.py
import subprocess
import os
import glob


def run_taxonomy(sample_dir, config):
    """
    Ejecuta MetaPhlAn para clasificación taxonómica.
    """
    db = config["paths"]["metaphlan_db"]
    nproc = config["tools"]["threads"]

    # Buscar el archivo R1 emparejado limpio
    # El archivo generado por kneaddata se llama: R1_kneaddata_paired_1.fastq
    input_pattern = os.path.join(sample_dir, "kneaddata_output", "R1_kneaddata_paired_*.fastq")
    input_files = glob.glob(input_pattern)

    if not input_files:
        raise FileNotFoundError(f"No se encontró ningún archivo que coincida con: {input_pattern}")

    input_file = input_files[0]

    output_dir = os.path.join(sample_dir, "taxonomy")
    os.makedirs(output_dir, exist_ok=True)
    profile_path = os.path.join(output_dir, "profile.txt")

    cmd = (
        f"metaphlan "
        f"{input_file} "
        f"--input_type fastq "
        f"--db_dir {db} "
        f"--nproc {nproc} "
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