# microbiome_cli/cli.py
"""
CLI modular para microbiome-pipeline
"""
import argparse
from .config_manager import load_config, create_default_config, update_config
from .downloader import DOWNLOADERS
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways


def run_all(samples_dir, config):
    from pathlib import Path
    samples_dir = Path(samples_dir)
    if not samples_dir.exists() or not samples_dir.is_dir():
        print(f"❌ Directorio inválido: {samples_dir}")
        return
    samples = [d for d in samples_dir.iterdir() if d.is_dir()]
    for sample in samples:
        print(f"\n{'='*60}\n📦 PROCESANDO: {sample.name}\n{'='*60}")
        try:
            run_qc(str(sample), config)
            run_taxonomy(str(sample), config)
            run_pathways(str(sample), config)
            print(f"✅ COMPLETADO: {sample.name}")
        except Exception as e:
            print(f"❌ ERROR: {e}")


def main():
    parser = argparse.ArgumentParser(description="microbiome-pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcomandos disponibles")

    # --- Subcomando: config ---
    config_parser = subparsers.add_parser("config", help="Gestiona el archivo config.yaml")
    config_sub = config_parser.add_subparsers(dest="action")
    config_set = config_sub.add_parser("set", help="Establece un valor")
    config_set.add_argument("key", help="Clave (ej: kneaddata_db)")
    config_set.add_argument("value", help="Valor (ruta)")
    config_create = config_sub.add_parser("create", help="Crea config.yaml por defecto")
    config_create.add_argument("--file", default="config.yaml", help="Nombre del archivo")

    # --- Subcomando: download ---
    download_parser = subparsers.add_parser("download", help="Descarga bases de datos")
    download_parser.add_argument(
        "database",
        choices=list(DOWNLOADERS.keys()),
        help="Base de datos a descargar"
    )
    download_parser.add_argument("dir", help="Directorio donde guardar")

    # --- Subcomandos: QC, Taxonomía, Vías ---
    qc_p = subparsers.add_parser("qc", help="Control de calidad")
    qc_p.add_argument("sample", help="Muestra")
    tax_p = subparsers.add_parser("taxonomy", help="Taxonomía")
    tax_p.add_argument("sample", help="Muestra")
    path_p = subparsers.add_parser("pathways", help="Vías metabólicas")
    path_p.add_argument("sample", help="Muestra")
    run_all_p = subparsers.add_parser("run-all", help="Pipeline completo")
    run_all_p.add_argument("data_dir", help="Carpeta con muestras")

    # Parsear argumentos
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Cargar config si es necesario
    config = None
    if args.command in ["qc", "taxonomy", "pathways", "run-all"]:
        config = load_config()

    # Ejecutar comando
    if args.command == "config":
        if args.action == "create":
            create_default_config(args.file)
            print(f"✅ config.yaml creado: {args.file}")
        elif args.action == "set":
            update_config(args.key, args.value)
        else:
            config_parser.print_help()

    elif args.command == "download":
        downloader = DOWNLOADERS[args.database]
        downloader(args.dir)

    elif args.command == "qc":
        run_qc(args.sample, config)

    elif args.command == "taxonomy":
        run_taxonomy(args.sample, config)

    elif args.command == "pathways":
        run_pathways(args.sample, config)

    elif args.command == "run-all":
        run_all(args.data_dir, config)


if __name__ == "__main__":
    main()