import click

from anc.cli.util import click_group
from anc.api.connection import Connection
#from ac.conf.remote import remote_server, remote_storage_prefix
from pprint import pprint
from tabulate import tabulate
import os
import sys
import signal

from .util import is_valid_source_path, get_file_or_folder_name, convert_to_absolute_path
from anc.conf.remote import remote_server
from .dataset_operator import DatasetOperator

@click_group()
def ds():
    pass


@ds.command()
@click.option("--source_path", "-s", type=str, help="Source path ot the dataset", required=True)
@click.option("--version", "-v", type=str, help="Dataset version you want to register", required=True)
@click.option("--message", "-m", type=str, help="Note of the dataset")
@click.pass_context
def add(ctx, source_path, version, message):
    if not is_valid_source_path(source_path):
        sys.exit(1) 
    abs_path = convert_to_absolute_path(source_path)
    dataset_name = get_file_or_folder_name(abs_path)
    conn = Connection(url=remote_server)
    data = {
        "dataset_name": dataset_name,
        "version": version,
        "source_path": abs_path,
        "dest_path": "local",
        "message": message
    }
    try:
        response = conn.post("/add", json=data, stream=True)
        for chunk in response.iter_lines(decode_unicode=True):
            if chunk:
                print(chunk)
    except KeyboardInterrupt:
        print(f"The dataset add operation may occur backend, you can check it later by `anc ds list -n {dataset_name} -v {version}` ")
        sys.exit(0)
    except Exception as e:
        print(f"Error occurred: {e}")

@ds.command()
@click.option("--name", "-n", help="Name of the datasets in remote",)
def list(name):
    op = DatasetOperator()
    op.list_dataset(name)


@ds.command()
@click.option("--name", "-n", help="Name of the datasets in remote", required=True)
@click.option("--version", "-v", help="Version of the dataset")
@click.option("--dest", "-d", help="Destination path you want to creat the dataset")
@click.option("--cache_policy", "-c", help="If input is `no` which means no cache used, the dataset will be a completely copy")
@click.pass_context
def get(ctx, name, version, dest, cache_policy):
    op = DatasetOperator()
    op.download_dataset(name, version, dest, cache_policy)

def add_command(cli_group):
    cli_group.add_command(ds)
