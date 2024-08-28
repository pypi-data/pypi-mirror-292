import argparse
import time
from functools import wraps
from pathlib import Path
from typing import Callable, List

from benedict import benedict

from qemu.machine import QEMUMachine

from .functions import parse_args, split_args
from .logger import LOG
from .storage import DRIVE_TYPES, Drive

# To be moved into input.py
SPEC_CHAR_KEYS = {
    "\r": ["ret"],
    "\n": ["ret"],
    " ": ["spc"],
    "=": ["equal"],
    "+": ["shift", "equal"],
    "-": ["minus"],
    "_": ["shift", "minus"],
    ";": ["semicolon"],
    ":": ["shift", "semicolon"],
    "&": ["shift", "7"],
    "/": ["slash"],
    ".": ["dot"],
    ">": ["shift", "dot"],
    "<": ["shift", "comma"],
    "#": ["shift", "3"],
}


class MaqetError(Exception):
    """
    General exception
    """


class MachineError(Exception):
    """
    Machine generic error
    """


class Machine(QEMUMachine):
    def __init__(self, *args, **kwargs):
        """
        TODO: make docstring

        Machine objects should be created with **kwargs
        """
        self._config = benedict(kwargs)
        if 'storage_path' in self._config:
            self._config.storage_path = Path(self._config.storage_path)
        if 'binary' not in self._config:
            raise MachineError("Binary not stated in config")

        self._config.typing_delay = kwargs.get('typing_delay', 0.1)

        binary = self._config['binary']

        qemumachine_args = dict()
        for key in ['args', 'wrapper', 'name', 'base_temp_dir',
                    'monitor_address', 'drain_console', 'console_log',
                    'log_dir', 'qmp_timer']:
            if key in self._config:
                qemumachine_args[key] = self._config[key]

        super().__init__(binary=binary, **qemumachine_args)

        self.storage = dict()
        if 'storage' in self._config:
            for name, drive in self._config.storage.items():
                self.add_drive(name=name, **drive)

    def launch(self):
        LOG.info(f'VM launch with command: {self.command}')
        super().launch()

    def add_drive(self, name, **kwargs) -> None:
        if 'path' not in kwargs:
            if 'storage_path' in self._config:
                # Adding default storage path from config
                kwargs['path'] = self._config.storage_path / name
            else:
                raise MachineError(
                    'Cannot add drive: stated neither path nor storage_path')
        self.storage[name] = Drive(**kwargs)

    # def add_argument(self, argument: str) -> None:
    #     """
    #     Add user argument to VM config
    #     """
    #     self._config['user_arguments'].append(argument)

    def add_args(self, *args: str) -> None:
        """
        Adds to the list of extra arguments to be given to the QEMU binary
        """
        super().add_args(*split_args(args))

    @property
    def command(self) -> str:
        """
        get full command string that will be executed at start
        """
        return self._binary + ' ' + ' '.join(self._base_args)

    @property
    def _const_args(self) -> List[str]:
        if 'arguments' not in self._config:
            return []
        return parse_args(self._config.arguments)

    @property
    def _var_args(self) -> List[str]:
        # TODO:more reliable method. Maybe add-fd?

        args = []
        for id, drive in self.storage.items():
            args += drive()

        return [
            a_splitted
            for a in args
            for a_splitted in a.split()
        ]

    @property
    def user_args(self):
        return [
            a_splitted
            for a in self._config.user_arguments
            for a_splitted in a.split()
        ]

    @ property
    def _base_args(self):
        args = self._var_args + self._const_args + self.user_args

        if self._qmp_set:
            if self._sock_pair:
                moncdev = f"socket,id=mon,fd={self._sock_pair[0].fileno()}"
            elif isinstance(self._monitor_address, tuple):
                moncdev = "socket,id=mon,host={},port={}".format(
                    *self._monitor_address
                )
            else:
                moncdev = f"socket,id=mon,path={self._monitor_address}"
            args.extend(['-chardev', moncdev, '-mon',
                         'chardev=mon,mode=control'])

        if self._machine is not None:
            args.extend(['-machine', self._machine])
        for _ in range(self._console_index):
            args.extend(['-serial', 'null'])
        if self._console_set:
            assert self._cons_sock_pair is not None
            fd = self._cons_sock_pair[0].fileno()
            chardev = f"socket,id=console,fd={fd}"
            args.extend(['-chardev', chardev])
            if self._console_device_type is None:
                args.extend(['-serial', 'chardev:console'])
            else:
                device = '%s,chardev=console' % self._console_device_type
                args.extend(['-device', device])
        return args

    def send_keys(self, keys: list[str] = []) -> dict:
        LOG.debug(f"QMP: keys to input: {keys}")
        command = "input-send-event"

        arguments = benedict({"events": []})
        arguments.events = []

        for k in keys:
            arguments.events.append(benedict(
                {
                    "type": "key",
                    "data": {"down": True, "key":
                             {"type": "qcode", "data": k}},
                }
            ))

        r = self.qmp(cmd=command, args_dict=arguments)
        LOG.debug(f"QMP: {keys}")

        for e in arguments.events:
            e.data.down = False

        r = self.qmp(cmd=command, args_dict=arguments)
        LOG.debug(f"QMP: {keys}")
        return r

    def send_input(self, string: str = "",):
        """
        Send input string to VM by emulating key press events
        """
        chars = list(string)

        for c in chars:
            keys = []
            if c in SPEC_CHAR_KEYS.keys():  # Enter
                keys = SPEC_CHAR_KEYS[c]
            elif c.isnumeric():  # Numbers
                keys.append(c)
            elif c.isalpha():  # Letters
                if c.isupper():
                    keys.append('shift')
                keys.append(c.lower())

            LOG.debug(f"Sending keys: {keys}")
            self.send_keys(keys=keys)
            time.sleep(self._config.typing_delay)

    def qmp_command(self, command_name: str = None, verbose=False,
                    *args, **kwargs) -> dict:
        """
        Execute custom or pre-cooked qmp command from config.qmp_commands
        """
        # TODO: add kwargs usage for templating cooked commands
        if command_name is None:
            command = kwargs
        else:
            if 'qmp_commands' not in self._config:
                raise MachineError('qmp_commands not stated in config')
            if command_name not in self._config.qmp_commands:
                raise MachineError('qmp command not stated qmp_commands')
            command = self._config.qmp_commands[command_name]

        if 'execute' not in command:
            raise MachineError(
                'qmp command: execute key and value not found')

        if 'arguments' in command:
            r = self.qmp(cmd=command.execute, args_dict=command.arguments)
        else:
            r = self.qmp(cmd=command.execute)

        if verbose:
            LOG.debug(f"QMP: {command}\nRETURN: {r}")
        return r

    def shutdown(self, *args, **kwargs):
        """
        Perform shutdown if machine is running
        """
        if self.is_running():
            super().shutdown(*args, **kwargs)


class Maqet:
    """
    TODO
    """

    def __init__(self, *args, **kwargs) -> None:
        self.Machine = Machine  # For comfortable stage building
        self._config = benedict(kwargs)

        self._validate_config()

        self._stages = dict()
        self.storage: dict[str, Drive] = dict()

    def __call__(self, *args, **kwargs) -> None:
        # Start pipeline

        LOG.info(f"Stages to run: {args}")

        for stage in args:
            if stage in self._stages:
                LOG.info(f"Executing stage {stage}")
                with self.Machine(**self._config.deepcopy()) as vm:
                    self._stages[stage](vm)
            else:
                LOG.warning(f"Stage {stage} not found. Skipping")

    def _validate_config(self):
        default_config_fields = {
            'binary': 'qemu-system-x86_64',
            'arguments': [],
            'user_arguments': [],
            'storage': []
        }

        for k, v in default_config_fields.items():
            if k not in self._config:
                self._config[k] = v

    @property
    def command(self) -> str:
        """
        get full command string that will be executed at start
        """
        with self.Machine(**self._config) as vm:
            return vm.command

    @property
    def DRIVE_TYPES(self) -> list:
        """
        Get available drive types
        """
        return list(DRIVE_TYPES)

    @property
    def config(self) -> dict:
        return self._config

    @config.setter
    def set_config(self, new_config: dict):
        self._config = benedict(new_config)
        self._validate_config()

    def merge_config(self, new_config: dict):
        self._config.merge(new_config)
        self._validate_config()

    def add_argument(self, argument: str) -> None:
        """
        Add user argument to config.
        It will be added to Machine arguments in every stage
        """
        self._config['user_arguments'].append(argument)

    def stage(self, stage_func: Callable, *args, **kwargs) -> Callable:
        """
        Include function as stage into Maqet pipeline. Does not modify function
        """
        self._stages[stage_func.__name__] = lambda vm: stage_func(vm)

        @ wraps
        def wrapper(*args, **kwargs):
            raise MaqetError(
                "Do not call stage functions by themselves, "
                f"call {self.__class__}(<stage function name>)"
                f"or {self.__class__}.cli() "
                "and enter stages as positional args"
            )
        return wrapper

    def cli(self, *args, **kwargs) -> None:
        """
        Run Maqet in Command Line Interface mode
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "stage",
            nargs="*",
            help="stages to run. If not stated - "
            "start VM with given config and wait for shutdown",
        )
        parser.add_argument(
            "-c", "--config-file",
            help="Set yaml file as a config",
            required=False,
            default=None,
            type=Path,
        )
        parser.add_argument(
            "-a", "--argument",
            help="State additional argument for qemu binary",
            action="append",
            default=[],
            # nargs="*",
        )
        parser.add_argument(
            "-s", "--storage-path",
            help="Set default path for drives",
            required=False,
            type=Path,
            default=None
        )
        parser.add_argument(
            "-v", "--verbose",
            action='count',
            help="increase verbose level",
            default=0
        )
        parser.add_argument(
            "--command",
            action='store_true',
            help="Output command with config and exit",
            default=False
        )

        cli_args = parser.parse_args()
        LOG.setLevel(50 - cli_args.verbose *
                     10 if cli_args.verbose < 5 else 10)

        LOG.info(cli_args)

        if cli_args.storage_path is not None:
            self._config.storage_path = cli_args.storage_path
        if cli_args.config_file is not None:
            self.merge_config(
                benedict.from_yaml(cli_args.config_file.resolve())
            )
        if len(cli_args.argument) > 0:
            for a in cli_args.argument:
                self.add_argument(a)
        if cli_args.command:
            print(self.command)
            exit(0)

        self(
            *cli_args.stage,
        )
