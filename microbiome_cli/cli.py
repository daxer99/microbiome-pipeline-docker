# microbiome_cli/cli.py
import os
import click
from .qc import run_qc
from .taxonomy import run_taxonomy
from .pathways import run_pathways
from .config_manager import load_config


@click.group()
def cli():
    pass


@cli.command()
@click.argument("samples_dir")
@click.option("--config", default="config.yaml", help="Ruta al archivo de configuración")
def run_all(samples_dir, config):
    """Procesa todas las muestras en samples_dir."""
    config_data = load_config(config)
    samples_dir = os.path.abspath(samples_dir)

    # Descubrir subdirectorios con muestras
    samples = [
        os.path.join(samples_dir, d) for d in os.listdir(samples_dir)
        if os.path.isdir(os.path.join(samples_dir, d)) and not d.startswith('.')
    ]
    samples.sort()

    if not samples:
        raise click.ClickException(f"No se encontraron muestras en {samples_dir}")

    click.echo(f"🚀 Iniciando pipeline para {len(samples)} muestras...")

    for sample_path in samples:
        sample_name = os.path.basename(sample_path)
        click.echo(f"\n{'='*60}\n📦 PROCESANDO: {sample_name}\n{'='*60}")

        try:
            run_qc(sample_path, config_data)
            run_taxonomy(sample_path, config_data)
            run_pathways(sample_path, config_data)
            click.echo(f"✅ Muestra {sample_name} procesada exitosamente.")
        except Exception as e:
            click.echo(f"❌ ERROR en {sample_name}: {str(e)}")