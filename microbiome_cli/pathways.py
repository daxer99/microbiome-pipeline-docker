# microbiome_cli/pathways.py
from .utils import run_cmd
import os


def run_pathways(sample_dir, config):
    """
    Ejecuta humann para análisis funcional.
    Usa los archivos emparejados limpios generados por kneaddata.
    """
    clean_dir = os.path.join(sample_dir, "kneaddata_output")
    if not os.path.exists(clean_dir):
        raise FileNotFoundError(f"Directorio kneaddata_output no encontrado: {clean_dir}")

    # Listar archivos limpios
    files = [
        f for f in os.listdir(clean_dir)
        if os.path.isfile(os.path.join(clean_dir, f)) and f.endswith('.fastq')
    ]
    files.sort()

    # Buscar archivos emparejados por patrón _paired_1 y _paired_2
    r1_file = next((f for f in files if "_paired_1.fastq" in f), None)
    r2_file = next((f for f in files if "_paired_2.fastq" in f), None)

    if not r1_file or not r2_file:
        raise FileNotFoundError(
            f"No se encontraron archivos emparejados (_paired_1.fastq, _paired_2.fastq) en {clean_dir}"
        )

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    print(f"🧫 Pathways: encontrados R1 y R2:")
    print(f"   R1: {r1}")
    print(f"   R2: {r2}")

    output_dir = os.path.join(sample_dir, "humann_output")
    os.makedirs(output_dir, exist_ok=True)

    cmd = (
        f"humann "
        f"--input {r1},{r2} "
        f"--output {output_dir} "
        f"--nprocs {config['tools']['threads']} "
        f"--taxonomic-profile {os.path.join(sample_dir, 'sample_1_profile_mpa.txt')} "
        f"--remove-column-description-output "
        f"--bypass-nucleotide-search"
    )

    print(f"🧫 Ejecutando HUMAnN...")
    run_cmd(cmd)
    print(f"✅ Análisis funcional completado: {output_dir}")