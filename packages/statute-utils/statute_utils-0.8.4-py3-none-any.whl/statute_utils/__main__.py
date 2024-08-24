from pathlib import Path

import click
from prelawsql import CODE_DIR, DB_FILE, STAT_DIR, TREE_GLOB


@click.group()
def cli():
    """Extensible wrapper of commands."""
    pass


@cli.command()
@click.option("--db-name", type=str, default=DB_FILE)
@click.option("--folder", type=Path, default=STAT_DIR)
@click.option("--pattern", type=str, default=TREE_GLOB)
def source_statutes(db_name: str, folder: str, pattern: str):
    """Create statute tables and populate with *.yml files from `--folder`."""
    from .tree_statute import Statute

    Statute.source(db_name=db_name, folder=folder, pattern=pattern)


@cli.command()
@click.option("--db-name", type=str, default=DB_FILE)
@click.option("--folder", type=Path, default=CODE_DIR)
@click.option("--pattern", type=str, default=TREE_GLOB)
def source_codifications(db_name: str, folder: str, pattern: str):
    """Create codification tables and populate with *.yml files from `--folder`."""
    from .tree_codification import Codification

    Codification.source(db_name=db_name, folder=folder, pattern=pattern)


if __name__ == "__main__":
    cli()  # search @cli.command
