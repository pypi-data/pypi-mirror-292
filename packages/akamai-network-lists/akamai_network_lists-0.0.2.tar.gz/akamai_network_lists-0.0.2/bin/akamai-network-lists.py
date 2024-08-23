"""
Some of the initial code for this project was borrowed from the Akamai cli-cloudlets project
https://github.com/akamai/cli-cloudlets/blob/56825e078b6014ce2f3b8af86fdcebf21d9e08d7/bin/akamai-cloudlets.py

"""
import click
import configparser
import importlib.metadata
import logging
import os
import requests
import sys
from akamai.edgegrid import EdgeGridAuth
from akamai.edgegrid import EdgeRc
from akamai_network_lists.network_lists_api_wrapper import NetworkLists


logger = logging.getLogger()

# file_handler = logging.FileHandler('akamai_network_lists.log')
# file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(file_formatter)
# logger.addHandler(file_handler)

console_formatter = logging.Formatter('%(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


def init_config(edgerc_file, section):
    if not edgerc_file:
        if not os.getenv('AKAMAI_EDGERC'):
            edgerc_file = os.path.join(os.path.expanduser('~'), '.edgerc')
        else:
            edgerc_file = os.getenv('AKAMAI_EDGERC')

    if not os.access(edgerc_file, os.R_OK):
        logger.error(f'ERROR: Unable to read edgerc file {edgerc_file}')
        exit(1)

    if not section:
        if not os.getenv('AKAMAI_EDGERC_SECTION'):
            section = 'network-lists'
        else:
            section = os.getenv('AKAMAI_EDGERC_SECTION')

    try:
        edgerc = EdgeRc(edgerc_file)
        base_url = edgerc.get(section, 'host')
        session = requests.Session()
        session.auth = EdgeGridAuth.from_edgerc(edgerc, section)
    except configparser.NoSectionError:
        logger.error(f'ERROR: edgerc section {section} not found')
        exit(1)
    except Exception:
        logger.error(f'ERROR: Unknown error occurred trying to read edgerc file ({edgerc_file})')
        exit(1)
    return base_url, session


class Config:
    def __init__(self):
        pass


pass_config = click.make_pass_decorator(Config, ensure=True)



@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('-e', '--edgerc', metavar='', default=os.path.join(os.path.expanduser('~'), '.edgerc'), help='Location of the credentials file [$AKAMAI_EDGERC]', required=False)
@click.option('-s', '--section', metavar='', help='Section of the credentials file [$AKAMAI_EDGERC_SECTION]', required=False)
@click.option('-a', '--account-key', metavar='', help='Account Key', required=False)
@click.version_option(version=importlib.metadata.version("akamai_network_lists"))
@pass_config
def cli(config, edgerc, section, account_key):
    f'''
    Akamai CLI for Network Lists {importlib.metadata.version("akamai_network_lists")}
    '''
    config.edgerc = edgerc
    config.section = section
    config.account_key = account_key


@cli.command()
@click.pass_context
def help(ctx):
    '''
    Show help information
    '''
    print(ctx.parent.get_help())

@cli.command()
@pass_config
def list(ctx):
    print("this is a test command.")


def main():
    try:
        cli_status = cli(prog_name="akamai_network_lists", obj={})
    except Exception as e:
        logger.error(e)
        exit(1)

if __name__ == "__main__":
    main()
