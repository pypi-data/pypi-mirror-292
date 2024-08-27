"""Module to hold cli functions."""
import click
from .destroyer import destroy_code
from .generator import generate_code


@click.group()
def cli():
    pass

@click.command()
@click.argument("name", required = True)
def new(name):
    generate_code(['app', name.lower()])

@click.command()
@click.argument("args", required = True, nargs = -1)
def generate(args):
    if args[0].lower() not in ['model','view','controller','scaffold']:
        click.echo('Valid Generation types are model, view, controller, scaffold')
        return
    if not args[1].isalnum():
        click.echo('Name can contain only alphabets and numbers')
        return
    generate_code([s.lower() for s in args])

@click.command()
@click.argument("type", required = True, nargs = 1)
@click.argument("name", required = True, nargs = 1)
def destroy(type,name):
    if type.lower() not in ['model','view','controller','scaffold']:
        click.echo('Valid Destroy types are model, view, controller, scaffold')
        return
    destroy_code(type,name.lower())

cli.add_command(new)
cli.add_command(generate)
cli.add_command(destroy)

if __name__ == "__main__":
    cli()
