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

console_formatter = logging.Formatter("%(message)s")
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


def init_config(edgerc_file, section):
    if not edgerc_file:
        if not os.getenv("AKAMAI_EDGERC"):
            edgerc_file = os.path.join(os.path.expanduser("~"), ".edgerc")
        else:
            edgerc_file = os.getenv("AKAMAI_EDGERC")

    if not os.access(edgerc_file, os.R_OK):
        logger.error(f"ERROR: Unable to read edgerc file {edgerc_file}")
        exit(1)

    if not section:
        if not os.getenv("AKAMAI_EDGERC_SECTION"):
            section = "network-lists"
        else:
            section = os.getenv("AKAMAI_EDGERC_SECTION")

    try:
        edgerc = EdgeRc(edgerc_file)
        base_url = edgerc.get(section, "host")
        session = requests.Session()
        session.auth = EdgeGridAuth.from_edgerc(edgerc, section)
    except configparser.NoSectionError:
        logger.error(f"ERROR: edgerc section {section} not found")
        exit(1)
    except Exception:
        logger.error(
            f"ERROR: Unknown error occurred trying to read edgerc file ({edgerc_file})"
        )
        exit(1)
    return base_url, session


class Config:
    def __init__(self):
        pass


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-e",
    "--edgerc",
    metavar="",
    default=os.path.join(os.path.expanduser("~"), ".edgerc"),
    help="Location of the credentials file [$AKAMAI_EDGERC]",
    required=False,
)
@click.option(
    "-s",
    "--section",
    metavar="",
    help="Section of the credentials file [$AKAMAI_EDGERC_SECTION]",
    required=False,
)
@click.option("-a", "--account-key", metavar="", help="Account Key", required=False)
@click.version_option(version=importlib.metadata.version("akamai_network_lists"))
@pass_config
def cli(config, edgerc, section, account_key):
    f"""
    Akamai CLI for Network Lists {importlib.metadata.version("akamai_network_lists")}
    """
    config.edgerc = edgerc
    config.section = section
    config.account_key = account_key


@cli.command()
@click.pass_context
def help(ctx):
    """
    Show help information
    """
    print(ctx.parent.get_help())


@cli.command(short_help="List Network Lists")
@pass_config
def list(config):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    lists = network_lists.list_network_lists(session)

    for list in lists["networkLists"]:
        print(f"{list['uniqueId']} - {list['name']}")
        print(f"  Type: {list['type']}")
        print(f"  Description: {list['description']}")
        print(f"  Elements: {list['elements']}")
        print(f"  Sync Point: {list['syncPoint']}")
        print(f"  Contract ID: {list['contractId']}")
        print(f"  Group ID: {list['groupId']}")
        print(f"  Element Count: {list['elementCount']}")


@cli.command(short_help="Create Network List")
@click.option(
    "-n", "--name", metavar="", help="Name of the network list", required=True
)
@click.option(
    "-t", "--type", metavar="", help="Type of network list (IP or GEO)", required=True
)
@click.option("-e", "--elements", metavar="", help="List of elements", required=True)
@click.option(
    "-d",
    "--description",
    metavar="",
    help="Description of the network list",
    required=False,
)
@click.option("-c", "--contract-id", metavar="", help="Contract ID", required=False)
@click.option("-g", "--group-id", metavar="", help="Group ID", required=False)
@pass_config
def create(config, name, type, elements, description, contract_id, group_id):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    elements = elements.split(",")
    response = network_lists.create_network_list(
        session, name, type, elements, description, contract_id, group_id
    )

    print(response)


@cli.command(short_help="Retrieve Network List")
@click.argument("network_list_id")
@pass_config
def retrieve(config, network_list_id):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.get_network_list(session, network_list_id)

    print(response)


@cli.command(short_help="Delete Network List")
@click.argument("network_list_id")
@pass_config
def delete(config, network_list_id):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.delete_network_list(session, network_list_id)

    print(response)


@cli.command(short_help="Update Network List")
@click.argument("network_list_id")
@click.option(
    "-t", "--type", metavar="", help="Type of network list (IP or GEO)", required=True
)
@click.option("-e", "--elements", metavar="", help="List of elements", required=True)
@click.option("-s", "--sync-point", metavar="", help="Sync Point", required=True)
@click.option(
    "-d",
    "--description",
    metavar="",
    help="Description of the network list",
    required=False,
)
@click.option("-x", "--extended", is_flag=True, help="Extended output", required=False)
@click.option(
    "-i", "--include-elements", is_flag=True, help="Include elements", required=False
)
@pass_config
def update(
    config,
    network_list_id,
    type,
    elements,
    sync_point,
    description,
    extended,
    include_elements,
):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    elements = elements.split(",")
    response = network_lists.update_network_list(
        session,
        network_list_id,
        type,
        elements,
        sync_point,
        description,
        extended,
        include_elements,
    )

    print(response)


@cli.command(short_help="Append Elements to Network List")
@click.argument("network_list_id")
@click.option("-e", "--elements", metavar="", help="List of elements", required=True)
@pass_config
def append(config, network_list_id, elements):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    elements = elements.split(",")
    response = network_lists.append_elements_to_network_list(
        session, network_list_id, elements
    )

    print(response)


@cli.command(short_help="Update Network List details")
@click.argument("network_list_id")
@click.option(
    "-n", "--name", metavar="", help="Name of the network list", required=True
)
@click.option(
    "-d",
    "--description",
    metavar="",
    help="Description of the network list",
    required=False,
)
@pass_config
def update_details(config, network_list_id, name, description):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.update_network_list_details(
        session, network_list_id, name, description
    )

    print(response)


@cli.command(short_help="Remove Network List Element")
@click.argument("network_list_id")
@click.option("-e", "--element", metavar="", help="Element to remove", required=True)
@pass_config
def remove_element(config, network_list_id, element):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.remove_network_list_element(
        session, network_list_id, element
    )

    print(response)


@cli.command(short_help="Add Network List Element")
@click.argument("network_list_id")
@click.option("-e", "--element", metavar="", help="Element to add", required=True)
@pass_config
def add_element(config, network_list_id, element):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.add_network_list_element(session, network_list_id, element)

    print(response)


@cli.command(short_help="Activate Network List")
@click.argument("network_list_id")
@click.option(
    "-e",
    "--environment",
    metavar="",
    help="Environment to activate the network list",
    required=True,
)
@click.option(
    "-c", "--comments", metavar="", help="Comments for the activation", required=False
)
@click.option(
    "-n",
    "--notification-recipients",
    metavar="",
    help="Notification recipients",
    required=False,
)
@click.option(
    "-s", "--siebel-ticket-id", metavar="", help="Siebel Ticket ID", required=False
)
@pass_config
def activate(
    config,
    network_list_id,
    environment,
    comments,
    notification_recipients,
    siebel_ticket_id,
):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.activate_network_list(
        session,
        network_list_id,
        environment,
        comments,
        notification_recipients,
        siebel_ticket_id,
    )

    print(response)


@cli.command(short_help="Get Activation Status")
@click.argument("network_list_id")
@click.option(
    "-e",
    "--environment",
    metavar="",
    help="Environment to activate the network list",
    required=True,
)
@pass_config
def activation_status(config, network_list_id, environment):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.get_activation_status(
        session, network_list_id, environment
    )

    print(response)


@cli.command(short_help="Get Activation Snapshot")
@click.argument("network_list_id")
@click.option("-s", "--sync-point", metavar="", help="Sync Point", required=True)
@click.option("-x", "--extended", is_flag=True, help="Extended output", required=False)
@pass_config
def activation_snapshot(config, network_list_id, sync_point, extended):
    base_url, session = init_config(config.edgerc, config.section)
    network_lists = NetworkLists(base_url)
    response = network_lists.get_activation_snapshot(
        session, network_list_id, sync_point, extended
    )

    print(response)


def main():
    try:
        cli_status = cli(prog_name="akamai_network_lists", obj={})
        exit(cli_status)
    except Exception as e:
        logger.error(e)
        exit(1)


if __name__ == "__main__":
    main()
