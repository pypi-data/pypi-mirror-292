import click
from .config import config
from .core import (
    copy_all_images,
    clean_image_bank,
    split_image_bank,
    clean_dataset,
    copy_all_labels,
)


@click.group()
def cli():
    """A tool for managing image datasets for computer vision models."""
    pass


@click.command()
def rebuild_image_bank():
    """Rebuild the entire image bank by cleaning and copying all images and labels."""
    clean_image_bank()
    copy_all_images()
    copy_all_labels()
    click.echo("Image bank rebuilt successfully.")


@click.command()
def clean_image_bank_cmd():
    """Clean the image bank by removing all images and labels."""
    clean_image_bank()
    click.echo("Image bank cleaned successfully.")


@click.command()
def split_image_bank_cmd():
    """Split the image bank into training, validation, and test datasets."""
    split_image_bank()
    click.echo("Image bank split into datasets successfully.")


@click.command()
def clean_dataset_cmd():
    """Clean the dataset directory."""
    clean_dataset()
    click.echo("Dataset cleaned successfully.")


# Add the commands to the CLI group
cli.add_command(rebuild_image_bank)
cli.add_command(clean_image_bank_cmd, name="clean_image_bank")
cli.add_command(split_image_bank_cmd, name="split_image_bank")
cli.add_command(clean_dataset_cmd, name="clean_dataset")

if __name__ == "__main__":
    cli()
