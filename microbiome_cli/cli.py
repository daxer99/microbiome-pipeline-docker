# microbiome_cli/cli.py
"""
CLI modular para microbiome-pipeline
"""
import argparse
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways
from .config_manager import load_config


def run_all(samples_dir):
    from pathlib import Path
    samples_dir = Path(samples_dir)
    if not samples_dir.exists() or not samples_dir.is_dir():
        print(f"❌ Directorio inválido: {samples_dir}")
        return

    samples = [d for d in samples_dir.iterdir() if d.is_dir()]
    if not samples:
        print(f"⚠️ No se encontraron muestras en: {samples_dir}")
        return

    try:
        config = load_config()
    except Exception as e:
        print(e)
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
        description="microbiome-pipeline CLI",
        epilog="El config.yaml debe estar montado en /home/microbiome/microbiome-pipeline/config.yaml"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    qc_p = subparsers.add_parser("qc", help="Control de calidad")
    qc_p.add_argument("sample", help="Muestra")

    tax_p = subparsers.add_parser("taxonomy", help="Taxonomía")
    tax_p.add_argument("sample", help="Muestra")

    path_p = subparsers.add_parser("pathways", help="Vías metabólicas")
    path_p.add_argument("sample", help="Muestra")

    run_all_p = subparsers.add_parser("run-all", help="Pipeline completo")
    run_all_p.add_argument("data_dir", help="Carpeta con muestras")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "run-all":
        run_all(args.data_dir)
    elif args.command == "qc":
        try:
            config = load_config()
            run_qc(args.sample, config)
        except Exception as e:
            print(e)
    elif args.command == "taxonomy":
        try:
            config = load_config()
            run_taxonomy(args.sample, config)
        except Exception as e:
            print(e)
    elif args.command == "pathways":
        try:
            config = load_config()
            run_pathways(args.sample, config)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()