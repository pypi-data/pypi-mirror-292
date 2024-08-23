import os
import click
import importlib
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from zuu.stdpkg.importlib import import_from_pkg_path
from zuu.tool import pkg_path, pkgs

incase_args = sys.argv[2:]
cmd_list = {}
for name in list(pkgs):

    try:
        # Import the module
        pkg = import_from_pkg_path(name, os.path.dirname(os.path.dirname(pkg_path)))
        name = name.rsplit(".", 1)[1]
        if not pkg:
            raise
        # Check if the module has a 'run' attribute
        if not hasattr(pkg, "run"):
            raise
    except:  # noqa
        continue

    # Add the command to the CLI
    cmd_list[name] = pkg


class CMD(click.Command):
    def format_help(self, ctx, formatter):
        # Modify help format if necessary
        ctx.invoke(run, name=incase_args[0], args=incase_args[1:])


@click.group()
def cli():
    """A CLI tool to list and run dynamic tools."""
    pass


@cli.command("list")
def _list():
    """List all available tools."""
    for name, pkg in cmd_list.items():
        try:
            click.echo(f"{name}\t\t- {pkg.run.__doc__.strip()}")
        except AttributeError:
            click.echo(f"{name}\t\t- (No description provided)")


@cli.command("run", cls=CMD)
@click.argument(
    "name", type=click.STRING, shell_complete=lambda _, __, **kwargs: list(pkgs.keys())
)
@click.argument("args", type=str, required=False)
def _run(name, args):
    """Run a specified tool by name."""
    if name not in cmd_list:
        click.echo(f"Package {name} not found")
        return

    # Get the package and call its 'run' function
    pkg = cmd_list[name]

    # Set sys.argv for the package run function
    if args:
        sys.argv = [name] + args.split()
    else:
        sys.argv = [name]
    # Execute the package's run function
    pkg.run()


def run():
    cli()


if __name__ == "__main__":

    cli()
