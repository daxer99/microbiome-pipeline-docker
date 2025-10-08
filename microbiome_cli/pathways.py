# microbiome_cli/pathways.py
import subprocess
import os
def run_pathways(sample_dir, config):
    """
    Ejecuta HUMAnN3 y su post-procesamiento completo.
    """
    nucleotide_db = config["paths"]["humann_nucleotide_db"]
    protein_db = config["paths"]["humann_protein_db"]
    threads = config["tools"]["threads"]

    input_dir = os.path.join(sample_dir, "kneaddata_output")
    output_dir = os.path.join(sample_dir, "pathways")
    os.makedirs(output_dir, exist_ok=True)

    # Buscar archivos emparejados limpios
    r1_files = [f for f in os.listdir(input_dir) if "_R1_" in f and "paired" in f]
    if not r1_files:
        raise FileNotFoundError(f"No se encontraron archivos emparejados en {input_dir}")

    base_name = r1_files[0].replace("_R1_", "").replace("_kneaddata_paired.fastq", "")
    input_r1 = os.path.join(input_dir, f"{base_name}_R1_kneaddata_paired.fastq")
    input_r2 = os.path.join(input_dir, f"{base_name}_R2_kneaddata_paired.fastq")

    sample_name = base_name  # Usa el nombre base como identificador

    # --- PASO 1: Ejecutar humann ---
    cmd = (
        f"humann "
        f"--input {input_r1},{input_r2} "
        f"--output {output_dir} "
        f"--nucleotide-database {nucleotide_db} "
        f"--protein-database {protein_db} "
        f"--threads {threads} "
        f"--verbose"
    )
    print(f"🧪 Vías metabólicas: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")

    # --- POST-PROCESAMIENTO HUMAnN3 ---
    results_dir = output_dir
    if not os.path.exists(results_dir):
        raise FileNotFoundError(f"Directorio de resultados no encontrado: {results_dir}")

    os.chdir(results_dir)
    print(f"📁 Trabajando en: {results_dir}")

    genefam_tsv = f"{sample_name}_merged_genefamilies.tsv"
    genefam_path = os.path.join(results_dir, genefam_tsv)

    # Renombrar si humann no usó prefijo
    if os.path.exists("merged_genefamilies.tsv") and not os.path.exists(genefam_tsv):
        os.rename("merged_genefamilies.tsv", genefam_tsv)
        os.rename("merged_pathabundance.tsv", f"{sample_name}_merged_pathabundance.tsv")
        if os.path.exists("merged_pathabundance_relab.tsv"):
            os.rename("merged_pathabundance_relab.tsv", f"{sample_name}_merged_pathabundance_relab.tsv")

    # --- RENORMALIZAR ---
    print("🔁 Renormalizando a abundancia relativa...")
    run_cmd(
        f"humann_renorm_table "
        f"--input {genefam_tsv} --units relab --output {sample_name}_merged_genefamilies_relab.tsv"
    )
    run_cmd(
        f"humann_renorm_table "
        f"--input {sample_name}_merged_pathabundance.tsv --units relab --output {sample_name}_merged_pathabundance_relab.tsv"
    )

    # --- EXTRAER NO ESTRATIFICADO ---
    print("✂️ Extrayendo genefamilias no estratificadas...")
    stra_tmp_dir = "stra_tmp"
    os.makedirs(stra_tmp_dir, exist_ok=True)
    run_cmd(
        f"humann_split_stratified_table "
        f"--input {sample_name}_merged_genefamilies_relab.tsv --output {stra_tmp_dir}"
    )
    src_file = os.path.join(stra_tmp_dir, f"{sample_name}_merged_genefamilies_relab_unstratified.tsv")
    if os.path.exists(src_file):
        os.rename(src_file, f"{sample_name}_merged_genefamilies_relab_unstratified.tsv")
    else:
        print(f"⚠️ No se generó archivo unstratified: {src_file}")
    cleanup_dir(stra_tmp_dir)

    # --- FUNCIONES AUXILIARES ---
    def process_regroup(input_tsv, db_path, output_suffix):
        out_tsv = f"{sample_name}_merged_genefamilies_relab_{output_suffix}.tsv"
        stra_dir = f"stra_{output_suffix}"
        unstrat_file = f"{sample_name}_merged_genefamilies_relab_{output_suffix}_unstratified.tsv"

        run_cmd(
            f"humann_regroup_table "
            f"-i {input_tsv} -c {db_path} -o {out_tsv}"
        )

        os.makedirs(stra_dir, exist_ok=True)
        run_cmd(
            f"humann_split_stratified_table "
            f"--input {out_tsv} --output {stra_dir}"
        )

        src = os.path.join(stra_dir, f"{sample_name}_merged_genefamilies_relab_{output_suffix}_unstratified.tsv")
        if os.path.exists(src):
            os.rename(src, unstrat_file)
        else:
            raise FileNotFoundError(f"No se generó el archivo unstratified: {src}")

        cleanup_dir(stra_dir)

    # --- PROCESAR CADA BASE DE DATOS ---
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
    """Ejecuta un comando shell."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, check=True)
    return result


def cleanup_dir(path):
    """Elimina un directorio si existe."""
    import shutil
    if os.path.exists(path):
        shutil.rmtree(path)