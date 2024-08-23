import json
import os
from pathlib import Path

import typer
from platformdirs import user_config_dir
from rich import print
from typing_extensions import Annotated

from wu_toolkit.__version__ import __title__, __version__
from wu_toolkit.app_config import config_, config_dir
from wu_toolkit.script.vesta_op import vesta_
from wu_toolkit.script.neb_aseview_ import visualize_neb_structures

wtk = typer.Typer(add_completion=False)
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


def main():
    wtk()


@wtk.callback(
    invoke_without_command=True,
    no_args_is_help=True,
    epilog=f"""+--------------------------------------------------------------------------------------------------------+\n
|                                           Wu-ToolKit                                                   |\n
|                                          Version: {__version__}                                                  |\n
|                                        Some scripts for personal use                                   |\n
+--------------------------------------------------------------------------------------------------------+""",
    context_settings=CONTEXT_SETTINGS,
)
def main_command():
    pass

@wtk.command(
    context_settings=CONTEXT_SETTINGS,
    help="Add, modify, delete, or show variables in the configuration file",
)
def config(
    action: Annotated[str, typer.Option("--action", "-a", help="Operation type: a (add), m (modify), d (delete), s (show)")] = None,
    var_name: Annotated[str, typer.Option("--name", "-n",help="Variable name")] = None,
    var_value: Annotated[str, typer.Option("--value", "-v",help="Variable value")] = None,
):
    config_(action, var_name, var_value)

# 自定义命令
@wtk.command(context_settings=CONTEXT_SETTINGS, help="Open files with Vesta")
def vesta(file_path: Annotated[str, typer.Argument(help="Input file path")]):
    vesta_(file_path)

@wtk.command(context_settings=CONTEXT_SETTINGS, help="Visualize NEB structures")
def neb(
    start: Annotated[int, typer.Argument(help="Start folder number")],
    end: Annotated[int, typer.Argument(help="End folder number")],
    filename: Annotated[str, typer.Argument(help="Structure file name")],
    base_dir: Annotated[str, typer.Argument(help="Base directory")] = ".",
):
    visualize_neb_structures(start, end, filename, base_dir)