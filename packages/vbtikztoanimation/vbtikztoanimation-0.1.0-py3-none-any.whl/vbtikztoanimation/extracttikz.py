import click
import re
import os
import subprocess


@click.command()
@click.option(
    '--inputfile',
    '-i',
    type=click.Path(exists=True),
    default='main.tex',
    show_default=True,
    help='The tex file to extract the tikz code from'
)
@click.option(
    '--outputdir',
    '-o',
    type=click.Path(),
    default='tikz',
    show_default=True,
    help='The output directory to write the tikz code to'
)
def extracttikz(inputfile, outputdir):
    if inputfile is None:
        click.echo('No input file provided')
        return

    with open(inputfile, 'r') as f:
        tex_content = f.read()

    tikz_content = re.findall(
        r'\\begin{tikzpicture}(.*?)\\end{tikzpicture}', tex_content, re.DOTALL)

    for i, tikz in enumerate(tikz_content, 1):
        tikz_dir = os.path.join(outputdir, f'tikz_{i}')
        os.makedirs(tikz_dir, exist_ok=True)
        with open(os.path.join(tikz_dir, 'tikz.tex'), 'w') as f:
            f.write("\\begin{tikzpicture}")
            for line in tikz.split('\n'):
                if line.strip():
                    f.write(f"\t{line.strip()}\n")
            f.write("\\end{tikzpicture}")
        click.echo(f"Generated tikz file for tikz_{i} in {tikz_dir}")

        # Show the generated tikz file using bat
        try:
            subprocess.run(['bat', os.path.join(
                tikz_dir, 'tikz.tex')], check=True)
        except subprocess.CalledProcessError:
            click.echo(
                f"Error: Unable to display file using bat. Make sure bat is installed.")
        except FileNotFoundError:
            click.echo(
                f"Error: bat command not found. Please install bat to use this feature.")
