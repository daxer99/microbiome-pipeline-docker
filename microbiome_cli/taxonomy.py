# microbiome_cli/taxonomy.py
from .utils import run_cmd
import os
import glob


def run_taxonomy(sample_dir, config):
    clean_dir = os.path.join(sample_dir, "kneaddata_output")
    if not os.path.exists(clean_dir):
        raise FileNotFoundError(f"Directorio kneaddata_output no encontrado: {clean_dir}")

    # Buscar archivos limpios emparejados
    r1_file = next((f for f in os.listdir(clean_dir) if "_paired_1.fastq" in f), None)
    r2_file = next((f for f in os.listdir(clean_dir) if "_paired_2.fastq" in f), None)

    if not r1_file or not r2_file:
        raise FileNotFoundError(f"No se encontraron archivos _paired_1/_paired_2 en {clean_dir}")

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    sample_name = os.path.basename(os.path.normpath(sample_dir))
    mpa_profile = os.path.join(sample_dir, f"{sample_name}_profile_mpa.txt")

    cmd = (
        f"metaphlan "
        f"{r1},{r2} "
        f"--input_type fastq "
        f"--db_dir {config['paths']['metaphlan_db']} "
        f"--nproc {config['tools']['threads']} "
        f"-x mpa_vJun23_CHOCOPhlAnSGB_202307 "
        f"--offline "
        f"--mapout /tmp/{sample_name}_temp.bz2 "
        f"-o {mpa_profile}"
    )

    print(f"🧬 Ejecutando MetaPhlAn...")
    run_cmd(cmd)
    run_cmd(f"rm -f /tmp/{sample_name}_temp.bz2")
    print(f"✅ Taxonomía completada: {mpa_profile}")

    # --- Post-procesamiento (igual que antes) ---
    try:
        profile_path = mpa_profile

        run_cmd(
            f"grep -E 'p__|clade' {profile_path} | egrep -v 'c__|o__|f__|g__|s__' | "
            f"sed 's/^.*p__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_phylum.txt')}"
        )
        run_cmd(
            f"grep -E 'c__|clade' {profile_path} | egrep -v 'o__|f__|g__|s__' | "
            f"sed 's/^.*c__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_class.txt')}"
        )
        # ... (el resto igual)
    except Exception as e:
        print(f"❌ Error al procesar niveles taxonómicos: {e}")
        raise