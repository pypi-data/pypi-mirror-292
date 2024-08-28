import logging
import subprocess
from pathlib import Path
from typing import List

from benedict import benedict

from .logger import LOG


def shell_command(command: str, verbose: bool = True) -> benedict:
    """
    Run shell command and return dictionary of stdout, stderr, returncode
    Return is benedict object, members can be accessed as fields
    """
    command = " ".join(command.split())

    proc = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    out = proc.communicate()

    output = benedict({
        "stdout": out[0].decode('ascii').strip("\n"),
        "stderr": out[1].decode('ascii').strip("\n"),
        "rc": proc.returncode
    })

    message = f"command `{command}` returned {output}"

    if verbose:
        level = logging.DEBUG
        if output.stderr != '':
            level = logging.WARNING
        if output.rc != 0:
            level = logging.ERROR

        LOG.log(level, message)
    return output


def mount_disk_to_host(path: Path) -> Path:
    return Path(shell_command(f"""
        udiskie-mount {str(path)} | grep mounted |\
        grep -o 'on .*$' | sed 's/on //'
    """).stdout)


def split_args(args: List):
    """
    Split args by spaces, used to send them into qemu methods
    """
    return [
        a_splitted
        for a in args
        for a_splitted in a.split()
    ]


def parse_options(arg, stack=[], key_only=False):
    if not isinstance(arg, (list, dict)):
        if len(stack) > 0:
            if key_only:
                return '.'.join(stack) + f'.{arg}'
            else:
                return '.'.join(stack) + f'={arg}'
        else:
            return arg

    options = []
    if isinstance(arg, list):
        for v in arg:
            if isinstance(arg, (list, dict)):
                options.append(parse_options(v, stack, key_only=True))
            else:
                options.append('.'.join(stack) + f'.{v}')

    elif isinstance(arg, dict):
        for k, v in arg.items():
            if isinstance(arg, (list, dict)):
                options.append(parse_options(v, stack+[k], key_only=False))
            else:
                option = '.'.join(stack) + f'={v}'
                options.append(option)
    return ','.join(options)


def parse_args(args: list) -> List[str]:
    final_args = []

    for arg in args:
        if type(arg) is str:
            argument = f'-{arg}'
        else:
            al = list(arg.items())
            if len(al) == 1:
                argument = f"-{al[0][0]} {parse_options(al[0][1])}"
            else:
                subarg = arg.copy()
                del subarg[al[0][0]]
                argument = f"-{al[0][0]} {al[0][1]},{parse_options(subarg)}"
        final_args.append(argument)

    return split_args(final_args)
