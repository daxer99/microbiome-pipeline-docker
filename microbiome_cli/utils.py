# microbiome_cli/utils.py
import os
import glob


def find_fastq_pairs(sample_dir):
    """
    Encuentra pares de archivos FASTQ en sample_dir usando patrones comunes.
    Retorna (r1_path, r2_path) o lanza FileNotFoundError.
    """
    patterns = [
        ("*_R1*.fastq", "*_R2*.fastq"),
        ("*R1*.fastq", "*R2*.fastq"),
        ("*_1*.fastq", "*_2*.fastq"),
        ("*1.fq", "*2.fq"),
        ("*.1.fq", "*.2.fq")
    ]

    for r1_pattern, r2_pattern in patterns:
        r1_files = sorted(glob.glob(os.path.join(sample_dir, r1_pattern)))
        r2_files = sorted(glob.glob(os.path.join(sample_dir, r2_pattern)))

        if r1_files and r2_files:
            return r1_files[0], r2_files[0]

    raise FileNotFoundError(
        f"No se encontraron pares de archivos FASTQ en {sample_dir} "
        "con patrones *_R1*, *_R2*, *1/*2, etc."
    )