# microbiome_cli/pathways.py
import subprocess
import os


def run_pathways(sample_dir, config):
    """
    Ejecuta HUMAnN3 para análisis funcional usando humann_config.
    """
    sample_name = os.path.basename(os.path.normpath(sample_dir))
    print(f"🧪 Vías metabólicas: {sample_name}")

    clean_dir = os.path.join(sample_dir, "kneaddata_output")
    if not os.path.exists(clean_dir):
        raise FileNotFoundError(f"Directorio kneaddata_output no encontrado: {clean_dir}")

    files = [
        f for f in os.listdir(clean_dir)
        if os.path.isfile(os.path.join(clean_dir, f)) and not f.endswith('.log')
    ]
    files.sort()

    if len(files) < 2:
        raise FileNotFoundError(f"Se esperaban 2 archivos limpios, encontrados: {files}")

    r1_file = next((f for f in files if "_paired_1.fastq" in f), None)
    r2_file = next((f for f in files if "_paired_2.fastq" in f), None)

    if not r1_file or not r2_file:
        raise FileNotFoundError(f"No se encontraron archivos R1/R2 limpios: {files}")

    r1 = os.path.join(clean_dir, r1_file)
    r2 = os.path.join(clean_dir, r2_file)

    mpa_profile = os.path.join(sample_dir, f"{sample_name}_profile_mpa.txt")
    if not os.path.exists(mpa_profile):
        raise FileNotFoundError(f"Falta perfil taxonómico: {mpa_profile}")

    merged = os.path.join(sample_dir, f"{sample_name}_merged.fastq")
    humann_out = os.path.join(sample_dir, f"{sample_name}_humann3_results")

    # --- Configurar bases de datos con humann_config ---
    print("🔧 Configurando rutas de bases de datos para HUMAnN3...")

    nucleotide_db = config['paths']['humann_nucleotide_db']
    protein_db = config['paths']['humann_protein_db']

    # ✅ Usar humann_config para actualizar las rutas
    run_cmd(f"humann_config --update database_folders nucleotide {nucleotide_db}")
    run_cmd(f"humann_config --update database_folders protein {protein_db}")

    print(f"✅ Bases de datos configuradas:")
    print(f"   Nucleótidos: {nucleotide_db}")
    print(f"   Proteínas: {protein_db}")

    # --- Ejecutar HUMAnN3 ---
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

    # --- POST-PROCESAMIENTO HUMAnN3 ---
    results_dir = humann_out
    if not os.path.exists(results_dir):
        raise FileNotFoundError(f"Directorio de resultados no encontrado: {results_dir}")

    os.chdir(results_dir)
    print(f"📁 Trabajando en: {results_dir}")

    genefam_tsv = f"{sample_name}_merged_genefamilies.tsv"
    genefam_path = os.path.join(results_dir, genefam_tsv)
    if not os.path.exists(genefam_path):
        raise FileNotFoundError(f"No se encontró el archivo de genefamilias: {genefam_path}")

    # Renormalizar a abundancia relativa
    print("🔁 Renormalizando a abundancia relativa...")
    run_cmd(
        f"humann_renorm_table "
        f"--input {genefam_tsv} --units relab --output {sample_name}_merged_genefamilies_relab.tsv"
    )
    run_cmd(
        f"humann_renorm_table "
        f"--input {sample_name}_merged_pathabundance.tsv --units relab --output {sample_name}_merged_pathabundance_relab.tsv"
    )

    # Extraer no estratificado de genefamilias
    print("✂️ Extrayendo genefamilias no estratificadas...")
    stra_tmp_dir = "stra_tmp"
    run_cmd(
        f"humann_split_stratified_table "
        f"--input {sample_name}_merged_genefamilies_relab.tsv --output {stra_tmp_dir}"
    )
    run_cmd(f"mv {stra_tmp_dir}/{sample_name}_merged_genefamilies_relab_unstratified.tsv .")
    run_cmd("rm -r stra_tmp")

    # Función auxiliar para procesar cada base de datos
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
        if not os.path.exists(src):
            raise FileNotFoundError(f"No se generó el archivo unstratified: {src}")
        run_cmd(f"mv {src} {unstrat_file}")
        run_cmd(f"rm -r {stra_dir}")

    # Procesar cada base de datos
    try:
        print("🔄 Procesando GO...")
        process_regroup(f"{sample_name}_merged_genefamilies_relab.tsv", config['paths']['humann_go_db'], "go")
        print("🔄 Procesando KO...")
        process_regroup(f"{sample_name}_merged_genefamilies_relab.tsv", config['paths']['humann_ko_db'], "ko")
        print("🔄 Procesando EC...")
        process_regroup(f"{sample_name}_merged_genefamilies_relab.tsv", config['paths']['humann_ec_db'], "ec")
        print("🔄 Procesando PFAM...")
        process_regroup(f"{sample_name}_merged_genefamilies_relab.tsv", config['paths']['humann_pfam_db'], "pfam")
        print("🔄 Procesando EGGNOG...")
        process_regroup(f"{sample_name}_merged_genefamilies_relab.tsv", config['paths']['humann_eggnog_db'], "eggnog")
        print(f"✅ Post-procesamiento HUMAnN3 completado en: {results_dir}")
    except Exception as e:
        print(f"❌ Error en post-procesamiento: {e}")
        raise

    os.chdir(sample_dir)


def run_cmd(cmd):
    """Ejecuta un comando shell y muestra salida en tiempo real"""
    print(f"🔧 Ejecutando: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")
    return result