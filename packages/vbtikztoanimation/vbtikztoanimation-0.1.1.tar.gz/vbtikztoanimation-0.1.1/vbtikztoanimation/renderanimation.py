import click
import subprocess


@click.command()
@click.option(
    '--inputfile',
    '-i',
    type=str,
    default='frame_',
    required=True,
    help='The input file'
)
@click.option(
    '--outputfile',
    '-o',
    type=str,
    default='animation.mov',
    required=True,
    help='The output file'
)
@click.option(
    '--framerate',
    '-f',
    type=int,
    default=30,
    show_default=True,
    help='The framerate of the animation'
)
def renderanimation(inputfile, outputfile, framerate):
    try:
        subprocess.run(['ffmpeg', '-framerate', str(framerate), '-i',
                       f'{inputfile}%d.png', '-c:v', 'prores_ks', '-pix_fmt', 'yuva420p', outputfile])
    except subprocess.CalledProcessError as e:
        click.echo(
            f"Error: Failed to run ffmpeg. Please ensure it's installed and accessible. Error: {e}")
    except FileNotFoundError:
        click.echo(
            "Error: ffmpeg command not found. Please install ffmpeg to generate frames.")
