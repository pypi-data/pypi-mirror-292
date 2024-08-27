import click
import os
import subprocess
import re
from .choice_option import ChoiceOption


@click.command()
@click.option(
    '--inputfile',
    '-i',
    type=click.Path(exists=True),
    default='tikz.tex',
    show_default=True,
    help='The tex file to extract the tikz code from'
)
@click.option(
    '--outputdir',
    '-o',
    type=click.Path(),
    default='frames',
    show_default=True,
    help='The output directory to write the tikz code to'
)
@click.option(
    '--framerate',
    '-f',
    type=int,
    default=30,
    show_default=True,
    help='The framerate of the animation'
)
@click.option(
    '--package',
    '-p',
    type=str,
    default='v-equation',
    show_default=True,
    help='The packages to include in the document'
)
@click.option(
    '--dimension',
    '-d',
    type=click.Tuple([float, float]),
    default=(6, 3.375),
    show_default=True,
    help='The dimension of the animation'
)
@click.option(
    '--vertical',
    '-v',
    is_flag=True,
    help='Whether to generate a vertical animation'
)
@click.option(
    '--color',
    '-c',
    type=str,
    default='black',
    show_default=True,
    help='The color of the animation'
)
@click.option(
    '--easing_function',
    '-e',
    cls=ChoiceOption,
    type=click.Choice(['smoothstep', 'powstep', 'backstep',
                      'sinestep', 'expstep', 'circstep', 'elasticstep']),
    default='sinestep',
    prompt=True,
    show_default=True,
    help='The easing function to use'
)
def genframes(inputfile, outputdir, framerate, package, dimension, vertical, color, easing_function):
    if inputfile is None:
        click.echo('No input file provided')
        return

    with open(inputfile, 'r') as f:
        tex_content = f.read()

    if re.search(r'\\def\\c@f{\d+}', tex_content) and re.search(r'\\def\\fps{\d+}', tex_content):
        with open(os.path.join(os.path.dirname(inputfile), 'main.tex'), 'w') as f:
            f.write("\\documentclass{article}\n")
            f.write(f"\\usepackage{{{package}}}\n")
            if vertical:
                f.write(
                    f"\\geometry{{paperwidth={dimension[1]} in, paperheight={dimension[0]} in}}\n\n")
            else:
                f.write(
                    f"\\geometry{{paperwidth={dimension[0]} in, paperheight={dimension[1]} in}}\n\n")
            f.write("\\begin{document}\n")
            f.write(f'\\color{{{color}}}\n')
            f.write(r'\tikz\fill (0, 0) circle(5pt);')
            f.write(r'\pagebreak')

            for frame in range(1, framerate + 1):
                f.write("\\vspace*{\\fill}\n")
                f.write("\\begin{center}\n")
                frame_content = re.sub(
                    r'\\def\\fps{\d+}',
                    f'\\\\def\\\\fps{{{framerate}}}',
                    tex_content)
                frame_content = re.sub(
                    r'\\def\\t{sinestep(0, \\fps, \\c@f)}',
                    f'\\\\def\\\\t{{{easing_function}(0, \\\\fps, \\\\c@f)}}',
                    frame_content)
                f.write(
                    re.sub(r'\\def\\c@f{\d+}', f'\\\\def\\\\c@f{{{frame}}}', frame_content))
                f.write("\\end{center}\n\n")
                f.write("\\vspace*{\\fill}\n\n")
                f.write(r'\pagebreak')

            f.write("\\end{document}\n")

    try:
        subprocess.run(['pdflatex', 'main.tex'], check=True)
    except subprocess.CalledProcessError:
        click.echo(
            "Error: Failed to run pdflatex. Please ensure it's installed and accessible.")
    except FileNotFoundError:
        click.echo(
            "Error: pdflatex command not found. Please install pdflatex to generate frames.")
