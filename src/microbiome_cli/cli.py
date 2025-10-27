# src/microbiome_cli/cli.py
"""
CLI modular para microbiome-pipeline
"""
import os
import click
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways
from .config_manager import load_config
from .downloader import DOWNLOADERS


@click.group()
def cli():
    """Pipeline de análisis microbioma."""
    pass


@cli.command()
@click.argument("samples_dir")
@click.option("--config", default="config.yaml", help="Ruta al archivo de configuración")
def run_all(samples_dir, config):
    """Procesa todas las muestras en samples_dir."""
    try:
        config_data = load_config(config)
    except Exception as e:
        click.echo(f"❌ Error al cargar config: {e}")
        return

    samples_dir = os.path.abspath(samples_dir)

    if not os.path.exists(samples_dir):
        click.echo(f"❌ Directorio no encontrado: {samples_dir}")
        return

    samples = [
        os.path.join(samples_dir, d) for d in os.listdir(samples_dir)
        if os.path.isdir(os.path.join(samples_dir, d)) and not d.startswith('.')
    ]
    samples.sort()

    if not samples:
        click.echo(f"❌ No se encontraron subdirectorios en: {samples_dir}")
        return

    click.echo(f"🔧 Config cargada desde: {config}")
    click.echo(f"🚀 Iniciando pipeline para {len(samples)} muestras...\n")

    for sample_path in samples:
        sample_name = os.path.basename(sample_path)
        click.echo(f"{'='*60}\n📦 PROCESANDO: {sample_name}\n{'='*60}")

        try:
            run_qc(sample_path, config_data)
            run_taxonomy(sample_path, config_data)
            run_pathways(sample_path, config_data)
            click.echo(f"✅ Muestra {sample_name} procesada exitosamente.\n")
        except Exception as e:
            click.echo(f"❌ ERROR en {sample_name}: {str(e)}\n")


@cli.command()
@click.argument("db_type", type=click.Choice(list(DOWNLOADERS.keys()) + ["all"]))
@click.argument("db_dir")
def download_db(db_type, db_dir):
    """Descarga bases de datos necesarias para el pipeline."""
    click.echo(f"📥 Descargando base de datos: {db_type}")
    click.echo(f"📁 Destino: {db_dir}")

    os.makedirs(db_dir, exist_ok=True)

    if db_type == "all":
        # Descargar todas
        for name, func in DOWNLOADERS.items():
            click.echo(f"\n🔄 Descargando {name}...")
            try:
                func(db_dir)
                click.echo(f"✅ {name} descargado.")
            except Exception as e:
                click.echo(f"❌ Error al descargar {name}: {e}")
    elif db_type in DOWNLOADERS:
        # Descargar una sola
        try:
            DOWNLOADERS[db_type](db_dir)
            click.echo(f"✅ {db_type} descargado en {db_dir}")
        except Exception as e:
            click.echo(f"❌ Error al descargar {db_type}: {e}")
            raise
    else:
        click.echo(f"❌ Tipo de base de datos desconocido: {db_type}")


def main():
    cli()


if __name__ == "__main__":
    main()