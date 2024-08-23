# TODO : Import the hello function from the cli.py file
import click
from .cli import hello, start, stop

@click.group()
def cli():
    pass

cli.add_command(hello)
cli.add_command(start)
cli.add_command(stop)



if __name__ == '__main__':
    cli()