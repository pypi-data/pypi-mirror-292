import json

import click
from tabulate import tabulate

from .api import ApiClient
from .version import __version__


@click.group(invoke_without_command=True)
@click.option("-e", "--endpoint", default=None, help="Specify the API endpoint")
@click.pass_context
def cli(ctx, endpoint):
    ctx.ensure_object(dict)
    ctx.obj["ENDPOINT"] = endpoint

    if ctx.invoked_subcommand is None:
        click.echo(f"protium CLI version {__version__}")
        click.echo("Use one of the following commands:")
        click.echo("  list    - List all projects")
        click.echo("  create  - Create a project from a JSON file")
        click.echo("  version - Display the version number")
        click.echo("\nUse 'ptm <command> --help' for more information on a command.")


@click.command()
@click.pass_context
def list(ctx):
    """List all projects"""
    endpoint = ctx.obj["ENDPOINT"]
    api_client = ApiClient(api_url=endpoint) if endpoint else ApiClient()
    df = api_client.list()
    if df is not None:
        # Convert DataFrame to list of lists and get columns
        table = tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False)  # type: ignore
        click.echo(table)
    else:
        click.echo("Failed to retrieve the list.")


@click.command()
@click.option("-f", "--file", type=click.Path(exists=True), help="JSON file to upload")
@click.pass_context
def create(ctx, file):
    """Create a project from a JSON file"""
    endpoint = ctx.obj["ENDPOINT"]
    api_client = ApiClient(api_url=endpoint) if endpoint else ApiClient()
    if file:
        try:
            with open(file, "r") as f:
                data = json.load(f)
            response = api_client.create(data)
            click.echo(json.dumps(response, indent=2))
        except json.JSONDecodeError:
            click.echo("Invalid JSON file.")
        except Exception as e:
            click.echo(f"Error: {e}")
    else:
        click.echo("No file provided. Use the -f option to specify a JSON file.")


@click.command()
def version():
    """Display the version number"""
    click.echo(f"protium version {__version__}")


cli.add_command(list)
cli.add_command(create)
cli.add_command(version)

if __name__ == "__main__":
    cli()
