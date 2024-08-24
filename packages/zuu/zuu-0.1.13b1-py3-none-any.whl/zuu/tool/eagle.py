
import click

from zuu.app.eagle import new_library

@click.command()
@click.argument('path')
def newlib(path):
    click.echo(f"creating eagle library at {path}")
    new_library(path)

def run():
    """
    eagle file explorer utilities
    """

    newlib()


