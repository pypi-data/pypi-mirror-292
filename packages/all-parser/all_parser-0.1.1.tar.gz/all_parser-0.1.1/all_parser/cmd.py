import click
import logging
import tempfile
import os
import sys
import traceback
from all_parser import allparse
from all_parser.constants import supported_extensions
from all_parser.all_parser_exceptions import *

global verbose
logging.basicConfig(filename=os.path.join(tempfile.gettempdir(),
                                            'all_parser.log'),
                                            level=logging.INFO,
                                            format='%(asctime)s - %(name)s'
                                            ' - %(levelname)s - %(message)s')
LOG = logging.getLogger(__name__)

def exception_handler(exception_type, exception, traceback):
    '''
    Custom exception handler to log the exception and print the message.
    '''
    LOG.error(f"ERROR: {exception_type.__name__} - {exception}")
    click.echo(f"ERROR: {exception_type.__name__} - {exception}")
    if verbose:
        traceback.print_tb(traceback)
    sys.exit(1)

def output_checks(output, force):
    if os.path.exists(output) and not force:
        raise FileExistsError(output)
    if '.' + output.split('.')[1] not in supported_extensions:
        print(allparse.supported_extensions)
        raise UnsupportedExtensionError(output)

sys.excepthook = exception_handler

@click.command()
@click.option('-f', '--file', required=True,
              help=f'Path to the file to parse.'
                   f'Supported file types are {supported_extensions}. '
                   f'If no extension is specified, the parser will try to '
                   f'parse the file with all supported types.')
@click.option('-e', '--ext', default=None,
              help='File type of the provided input,'
                   'this overrides the file type from extension.')
@click.option('-o', '--output', default=None,
              help='Output path to store the parsed file. '
                   'Prints the file in stdout by default.'
                   'Automatically assumes output file type '
                   'based on the extension.')
@click.option('-s', '--silent', is_flag=True, help='Silent mode.')
@click.option('-f', '--force', is_flag=True, help='Force parsing. This will'
                                                  ' overwrite the output '
                                                  'file, if exists. And will '
                                                  'also force parsing.')
@click.option('-v','--verbose', is_flag=True, default=False, help='Verbose mode.')
def parse(file, ext, output, silent, force, verbose):
    # Start parsing
    LOG.info(f"Parsing file {file}")

    allparser = allparse.AllParse(file, ext, verbose)

    if output:
        output_checks(output, force)
        allparser.write_output(output)
        LOG.info(f"Output file {output} created.")
        if not silent:
            click.echo(f"Output file {output} created.")
    else:
        allparser.print_parsed()

if __name__ == '__main__':
    parse()

