# microbiome_cli/pathways.py
from .utils import run_cmd
import os


def run_pathways(sample_dir, config):
    """
    Ejecuta HUMAnN3 para análisis funcional.
    Usa variables de entorno para evitar errores de escritura en config.
    """
    sample_name = os.path.basename(os.path.normpath(sample_dir))
    print(f"🧪 Vías metabólicas: {sample_name}")

    clean_dir = os.path.join(sample_dir, "kneaddata_output")
    if not os.path.exists(clean_dir):
        raise FileNotFoundError(f"Directorio kneaddata_output no encontrado: {clean_dir}")

    # Listar archivos limpios
    files = [
        f for f in os.listdir(clean_dir)
        if os.path.isfile(os.path.join(clean_dir, f)) and f.endswith('.fastq')
    ]
    files.sort()

    if len(files) < 2:
        raise FileNotFoundError(f"Se esperaban al menos 2 archivos limpios, encontrados: {files}")

    r1_file = next((f for f in files if "_paired_1.fastq" in f), None)
    r2_file = next((f for f in files if "_paired_2.fastq" in f), None)

    if not r1_file or not r2_file:
        raise FileNotFoundError(f"No se encontraron archivos _paired_1.fastq o _paired_2.fastq en: {files}")

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    print(f"🧫 Pathways: encontrados R1 y R2:")
    print(f"   R1: {r1}")
    print(f"   R2: {r2}")

    # Verificar perfil taxonómico
    mpa_profile = os.path.join(sample_dir, f"{sample_name}_profile_mpa.txt")
    if not os.path.exists(mpa_profile):
        raise FileNotFoundError(f"Falta perfil taxonómico: {mpa_profile}. Ejecuta 'taxonomy' primero.")

    # Salidas
    merged = os.path.join(sample_dir, f"{sample_name}_merged.fastq")
    humann_out = os.path.join(sample_dir, f"{sample_name}_humann3_results")

    # Configurar bases de datos con variables de entorno
    nucleotide_db = config['paths']['humann_nucleotide_db']
    protein_db = config['paths']['humann_protein_db']

    print("🔧 Configurando bases de datos vía variables de entorno...")
    os.environ["HUMANN_nucleotide_database"] = nucleotide_db
    os.environ["HUMANN_protein_database"] = protein_db
    print(f"✅ Bases de datos configuradas:\n   Nucleótidos: {nucleotide_db}\n   Proteínas: {protein_db}")

    # Combinar R1 y R2
    run_cmd(f"cat {r1} {r2} > {merged}")

    # Ejecutar HUMAnN3
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

    # --- POST-PROCESAMIENTO ---
    if not os.path.exists(humann_out):
        raise FileNotFoundError(f"Directorio de resultados no encontrado: {humann_out}")

    os.chdir(humann_out)
    print(f"📁 Trabajando en: {humann_out}")

    genefam_tsv = f"{sample_name}_merged_genefamilies.tsv"
    genefam_path = os.path.join(humann_out, genefam_tsv)

    # Renombrar si humann no usó prefijo
    if os.path.exists("merged_genefamilies.tsv") and not os.path.exists(genefam_tsv):
        run_cmd(f"mv merged_genefamilies.tsv {genefam_tsv}")
        run_cmd(f"mv merged_pathabundance.tsv {sample_name}_merged_pathabundance.tsv")
        if os.path.exists("merged_pathabundance_relab.tsv"):
            run_cmd(f"mv merged_pathabundance_relab.tsv {sample_name}_merged_pathabundance_relab.tsv")

    # Renormalizar a abundancia relativa
    print("🔁 Renormalizando a abundancia relativa...")
    run_cmd(
        f"humann_renorm_table "
        f"--input {genefam_tsv} --units relab --output {sample_name}_merged_genefamilies_relab.tsv"
    )
    pathabun = f"{sample_name}_merged_pathabundance.tsv"
    if os.path.exists(pathabun):
        run_cmd(
            f"humann_renorm_table "
            f"--input {pathabun} --units relab --output {sample_name}_merged_pathabundance_relab.tsv"
        )

    # Extraer no estratificado
    print("✂️ Extrayendo genefamilias no estratificadas...")
    stra_tmp_dir = "stra_tmp"
    run_cmd(
        f"humann_split_stratified_table "
        f"--input {sample_name}_merged_genefamilies_relab.tsv --output {stra_tmp_dir}"
    )
    unstrat_file = f"{sample_name}_merged_genefamilies_relab_unstratified.tsv"
    src = f"{stra_tmp_dir}/{sample_name}_merged_genefamilies_relab_unstratified.tsv"
    if os.path.exists(src):
        run_cmd(f"mv {src} {unstrat_file}")
    run_cmd("rm -rf stra_tmp")

    # Función auxiliar para regroup
    def process_regroup(input_tsv, db_path, output_suffix):
        out_tsv = f"{sample_name}_merged_genefamilies_relab_{output_suffix}.tsv"
        stra_dir = f"stra_{output_suffix}"
        unstrat_file = f"{sample_name}_merged_genefamilies_relab_{output_suffix}_unstratified.tsv"
        src = f"{stra_dir}/{out_tsv.replace('.tsv', '_unstratified.tsv')}"

        run_cmd(
            f"humann_regroup_table "
            f"-i {input_tsv} -c {db_path} -o {out_tsv}"
        )
        run_cmd(
            f"humann_split_stratified_table "
            f"--input {out_tsv} --output {stra_dir}"
        )
        if os.path.exists(src):
            run_cmd(f"mv {src} {unstrat_file}")
        run_cmd(f"rm -rf {stra_dir}")

    # Procesar cada base de datos
    try:
        print("🔄 Procesando GO...")
        process_regroup(genefam_tsv, config['paths']['humann_go_db'], "go")
        print("🔄 Procesando KO...")
        process_regroup(genefam_tsv, config['paths']['humann_ko_db'], "ko")
        print("🔄 Procesando EC...")
        process_regroup(genefam_tsv, config['paths']['humann_ec_db'], "ec")
        print("🔄 Procesando PFAM...")
        process_regroup(genefam_tsv, config['paths']['humann_pfam_db'], "pfam")
        print("🔄 Procesando EGGNOG...")
        process_regroup(genefam_tsv, config['paths']['humann_eggnog_db'], "eggnog")
        print(f"✅ Post-procesamiento HUMAnN3 completado en: {humann_out}")
    except Exception as e:
        print(f"❌ Error en post-procesamiento: {e}")
        raise

    os.chdir(sample_dir)