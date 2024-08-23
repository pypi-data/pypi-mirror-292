import click
from .cli import hello, start, stop, connect

@click.group()
def cli():
    pass

cli.add_command(hello)
cli.add_command(start)
cli.add_command(stop)
cli.add_command(connect)

if __name__ == '__main__':
    cli()
