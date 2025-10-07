# microbiome_cli/cli.py
"""
CLI modular para microbiome-pipeline
El config.yaml debe existir en la raíz del repositorio.
No se crea ni modifica desde la CLI.
"""
import argparse
from .config_manager import load_config
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways


def run_all(samples_dir, config):
    """Ejecuta todo el pipeline para todas las muestras"""
    from pathlib import Path
    samples_dir = Path(samples_dir)
    if not samples_dir.exists() or not samples_dir.is_dir():
        print(f"❌ Directorio inválido: {samples_dir}")
        return

    samples = [d for d in samples_dir.iterdir() if d.is_dir()]
    if not samples:
        print(f"⚠️ No se encontraron muestras en: {samples_dir}")
        return

    print(f"🚀 Iniciando pipeline para {len(samples)} muestras...")
    for sample in samples:
        print(f"\n{'='*60}\n📦 PROCESANDO: {sample.name}\n{'='*60}")
        try:
            run_qc(str(sample), config)
            run_taxonomy(str(sample), config)
            run_pathways(str(sample), config)
            print(f"✅ COMPLETADO: {sample.name}")
        except Exception as e:
            print(f"❌ ERROR en {sample.name}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="microbiome-pipeline CLI\nEl config.yaml debe existir en la raíz del repositorio."
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # --- Comandos del pipeline ---
    qc_p = subparsers.add_parser("qc", help="Control de calidad con KneadData")
    qc_p.add_argument("sample", help="Carpeta de la muestra")

    tax_p = subparsers.add_parser("taxonomy", help="Taxonomía con MetaPhlAn")
    tax_p.add_argument("sample", help="Carpeta de la muestra")

    path_p = subparsers.add_parser("pathways", help="Vías metabólicas con HUMAnN")
    path_p.add_argument("sample", help="Carpeta de la muestra")

    run_all_p = subparsers.add_parser("run-all", help="Ejecutar todo el pipeline")
    run_all_p.add_argument("data_dir", help="Carpeta con todas las muestras")

    # Parsear argumentos
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Todos los comandos necesitan el config
    config = load_config("config.yaml")

    # Ejecutar comando
    if args.command == "qc":
        run_qc(args.sample, config)
    elif args.command == "taxonomy":
        run_taxonomy(args.sample, config)
    elif args.command == "pathways":
        run_pathways(args.sample, config)
    elif args.command == "run-all":
        run_all(args.data_dir, config)


if __name__ == "__main__":
    main()