# microbiome_cli/pathways.py
from .utils import run_cmd, find_fastq_pairs
import os


def run_pathways(sample_dir, config):
    sample_name = os.path.basename(os.path.normpath(sample_dir))

    # Encontrar archivos limpios generados por kneaddata
    clean_dir = os.path.join(sample_dir, "kneaddata_output")
    r1_file = next((f for f in os.listdir(clean_dir) if "_paired_1.fastq" in f), None)
    r2_file = next((f for f in os.listdir(clean_dir) if "_paired_2.fastq" in f), None)

    if not r1_file or not r2_file:
        raise FileNotFoundError(f"No se encontraron archivos _paired_1/_paired_2 en {clean_dir}")

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    mpa_profile = os.path.join(sample_dir, f"{sample_name}_profile_mpa.txt")
    if not os.path.exists(mpa_profile):
        raise FileNotFoundError(f"Falta perfil taxonómico: {mpa_profile}")

    merged = os.path.join(sample_dir, f"{sample_name}_merged.fastq")
    humann_out = os.path.join(sample_dir, f"{sample_name}_humann3_results")

    # Configurar bases de datos vía variables de entorno
    nucleotide_db = config['paths']['humann_nucleotide_db']
    protein_db = config['paths']['humann_protein_db']

    os.environ["HUMANN_nucleotide_database"] = nucleotide_db
    os.environ["HUMANN_protein_database"] = protein_db

    run_cmd(f"cat {r1} {r2} > {merged}")

    cmd = (
        f"humann "
        f"--input {merged} "
        f"--output {humann_out} "
        f"--threads {config['tools']['threads']} "
        f"--taxonomic-profile {mpa_profile} "
        f"--remove-temp-output "
        f"--remove-column-description-output "
        f"--bypass-nucleotide-search"
    )

    print(f"🧫 Ejecutando HUMAnN3...")
    run_cmd(cmd)
    print(f"✅ Análisis funcional completado: {humann_out}")

    # --- Post-procesamiento (igual que antes) ---
    # (mantén el regroup, renormalización, etc.)