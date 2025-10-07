# microbiome_cli/cli.py
"""
CLI modular para microbiome-pipeline
El config.yaml debe existir en la raíz del repositorio.
Editado manualmente por el usuario.
"""
import argparse
from .config_manager import load_config
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways


def run_all(samples_dir):
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

    # Cargar config UNA VEZ, antes de procesar muestras
    try:
        config = load_config()
    except Exception as e:
        print(e)
        return

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
        epilog="El config.yaml debe existir en la raíz del repositorio.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    qc_p = subparsers.add_parser("qc", help="Control de calidad con KneadData")
    qc_p.add_argument("sample", help="Carpeta de la muestra")

    tax_p = subparsers.add_parser("taxonomy", help="Taxonomía con MetaPhlAn")
    tax_p.add_argument("sample", help="Muestra")

    path_p = subparsers.add_parser("pathways", help="Vías metabólicas con HUMAnN")
    path_p.add_argument("sample", help="Muestra")

    run_all_p = subparsers.add_parser("run-all", help="Ejecutar todo el pipeline")
    run_all_p.add_argument("data_dir", help="Carpeta con todas las muestras")

    # Parsear argumentos ANTES de cargar el config
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Ejecutar comando SOLO si necesita el config
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