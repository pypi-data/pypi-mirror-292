import click
from barbud import identifyUPC

@click.group(help='CLIT Toll for working with UPCs')
def cli():
    pass

@cli.command(help='Identify UPC Type')
@click.argument('upcstring')
def identify(upcstring):

    print(identifyUPC(upcstring))

def main():
    cli()

if __name__ == '__main__':
    cli()