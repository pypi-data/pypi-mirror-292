import os
import click
from pdf2image import convert_from_path


@click.command()
@click.option(
    '--inputfile',
    '-i',
    type=click.Path(exists=True),
    default='main.pdf',
    show_default=True,
    help='The input file to read the frames from'
)
@click.option(
    '--outputdir',
    '-o',
    type=click.Path(),
    default='frames',
    show_default=True,
    help='The output directory to write the frames to'
)
@click.option(
    '--dpi',
    '-d',
    type=int,
    default=320,
    show_default=True,
    help='The dpi of the frames'
)
def renderframes(inputfile, outputdir, dpi):
    os.makedirs(outputdir, exist_ok=True)
    images = convert_from_path(
        inputfile, dpi=dpi, transparent=True, use_pdftocairo=True, thread_count=16)
    for i, image in enumerate(images[1:], 1):
        image.save(os.path.join(outputdir, f'frame_{i}.png'), 'PNG')
