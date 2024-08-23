from .cat import hello, start, stop

import click

@click.group()
def cli():
    pass

cli.add_command(hello)
cli.add_command(start)
cli.add_command(stop)

if __name__ == '__main__':
    cli()