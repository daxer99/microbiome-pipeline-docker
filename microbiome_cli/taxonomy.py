# microbiome_cli/taxonomy.py
from .utils import run_cmd
import os


def run_taxonomy(sample_dir, config):
    """
    Ejecuta MetaPhlAn para clasificación taxonómica usando R1 y R2 emparejados.
    Incluye --mapout requerido por MetaPhlAn 4.x cuando se usan múltiples archivos.
    """
    # Obtener nombre de la muestra desde el directorio
    sample_name = os.path.basename(os.path.normpath(sample_dir))
    print(f"🧬 Taxonomía: {sample_name}")

    clean_dir = os.path.join(sample_dir, "kneaddata_output")
    if not os.path.exists(clean_dir):
        raise FileNotFoundError(f"Directorio kneaddata_output no encontrado: {clean_dir}")

    # Listar archivos limpios
    files = [
        f for f in os.listdir(clean_dir)
        if os.path.isfile(os.path.join(clean_dir, f)) and not f.endswith('.log')
    ]
    files.sort()

    if len(files) < 2:
        raise FileNotFoundError(f"Se esperaban al menos 2 archivos limpios, encontrados: {files}")

    # Buscar archivos emparejados generados por kneaddata
    r1_file = next((f for f in files if "_paired_1.fastq" in f), None)
    r2_file = next((f for f in files if "_paired_2.fastq" in f), None)

    if not r1_file or not r2_file:
        raise FileNotFoundError(f"No se encontraron archivos _paired_1.fastq o _paired_2.fastq en: {files}")

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    print(f"✅ Archivos limpios encontrados:")
    print(f"   R1: {r1}")
    print(f"   R2: {r2}")

    # Salidas con prefijo de muestra
    output_file = os.path.join(sample_dir, f"{sample_name}_profile_mpa.txt")
    temp_mapout = os.path.join(sample_dir, f"{sample_name}_profile_mpa.bz2")  # Necesario para MetaPhlAn

    cmd = (
        f"metaphlan "
        f"{r1},{r2} "
        f"--input_type fastq "
        f"--db_dir {config['paths']['metaphlan_db']} "
        f"--nproc {config['tools']['threads']} "
        f"-x mpa_vJun23_CHOCOPhlAnSGB_202307 "
        #f"--t rel_ab_w_read_stats "
        f"--offline "
        f"--mapout {temp_mapout} "
        f"-o {output_file}"
    )

    print(f"🧬 Ejecutando MetaPhlAn...")
    run_cmd(cmd)

    # Opcional: eliminar el mapout si no lo necesitas
    run_cmd(f"rm -f {temp_mapout}")
    print(f"✅ Taxonomía completada: {output_file}")

    # --- Separar por niveles taxonómicos con prefijo ---
    try:
        profile_path = output_file

        run_cmd(
            f"grep -E 'p__|clade' {profile_path} | egrep -v 'c__|o__|f__|g__|s__' | "
            f"sed 's/^.*p__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_phylum.txt')}"
        )
        run_cmd(
            f"grep -E 'c__|clade' {profile_path} | egrep -v 'o__|f__|g__|s__' | "
            f"sed 's/^.*c__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_class.txt')}"
        )
        run_cmd(
            f"grep -E 'o__|clade' {profile_path} | egrep -v 'f__|g__|s__' | "
            f"sed 's/^.*o__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_order.txt')}"
        )
        run_cmd(
            f"grep -E 'f__|clade' {profile_path} | egrep -v 'g__|s__' | "
            f"sed 's/^.*f__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_family.txt')}"
        )
        run_cmd(
            f"grep -E 'g__|clade' {profile_path} | egrep -v 's__' | "
            f"sed 's/^.*g__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_genus.txt')}"
        )
        run_cmd(
            f"grep -E 's__|clade' {profile_path} | "
            f"sed 's/^.*s__//g' | cut -f1,2-5000 > {os.path.join(sample_dir, f'{sample_name}_profile_species.txt')}"
        )
        print(f"✅ Perfiles taxonómicos con prefijo guardados en {sample_dir}")

    except Exception as e:
        print(f"❌ Error al procesar niveles taxonómicos: {e}")
        raise