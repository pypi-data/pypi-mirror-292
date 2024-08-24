import sys
import os
from typing import Any, Optional
from urllib.parse import urlparse

import click
from loguru import logger

from rich.console import Console

from anc.conf.remote import remote_storage_prefix

console = Console(highlight=False)


def click_group(*args, **kwargs):
    class ClickAliasedGroup(click.Group):
        def get_command(self, ctx, cmd_name):
            rv = click.Group.get_command(self, ctx, cmd_name)
            if rv is not None:
                return rv

            def is_abbrev(x, y):
                # first char must match
                if x[0] != y[0]:
                    return False
                it = iter(y)
                return all(any(c == ch for c in it) for ch in x)

            matches = [x for x in self.list_commands(ctx) if is_abbrev(cmd_name, x)]

            if not matches:
                return None
            elif len(matches) == 1:
                return click.Group.get_command(self, ctx, matches[0])
            ctx.fail(f"'{cmd_name}' is ambiguous: {', '.join(sorted(matches))}")

        def resolve_command(self, ctx, args):
            # always return the full command name
            _, cmd, args = super().resolve_command(ctx, args)
            return cmd.name, cmd, args

    return click.group(*args, cls=ClickAliasedGroup, **kwargs)

def is_valid_source_path(path: str) -> bool:
    """Check if the source path is valid."""
    if not os.path.exists(path):
        print(f"Your source {path} is invalid, path not exists")
        return False
    if not os.access(path, os.R_OK):
        print(f"Your source {path} is invalid, path not access")
        return False
    if not path.startswith(remote_storage_prefix):
        print(f"Your source {path} is invalid, path is not prefix of {remote_storage_prefix} ")
        return False
    return True

def convert_to_absolute_path(path: str) -> str:
    """Convert a relative path to an absolute path."""
    return os.path.abspath(path)

def get_file_or_folder_name(path: str) -> str:
    """Get the file name with extension or folder name from the given path."""
    if os.path.isdir(path):
        return os.path.basename(path)  # Return folder name
    elif os.path.isfile(path):
        return os.path.basename(path)  # Return file name with extension
    else:
        raise ValueError(f"Invalid path {path}")