import click
from .extracttikz import extracttikz
from .genframes import genframes
from .renderframes import renderframes
from .renderanimation import renderanimation
CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'], auto_envvar_prefix='VBTIKZTOANIMATION')


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


main.add_command(extracttikz)
main.add_command(genframes)
main.add_command(renderframes)
main.add_command(renderanimation)
