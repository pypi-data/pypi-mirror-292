
from abc import ABCMeta, abstractmethod
from pathlib import Path

from benedict import benedict

from .functions import parse_args
from .functions import shell_command as cmd
from .logger import LOG

MESSAGE = r"""
 _                _      __  __           _   _         _   _                 _     _ 
| |    ___   ___ | | __ |  \/  | __ _    | \ | | ___   | | | | __ _ _ __   __| |___| |
| |   / _ \ / _ \| |/ / | |\/| |/ _` |   |  \| |/ _ \  | |_| |/ _` | '_ \ / _` / __| |
| |__| (_) | (_) |   <  | |  | | (_| |_  | |\  | (_) | |  _  | (_| | | | | (_| \__ \_|
|_____\___/ \___/|_|\_\ |_|  |_|\__,_( ) |_| \_|\___/  |_| |_|\__,_|_| |_|\__,_|___(_)
                                     |/
"""


class DriveError(Exception):
    """
    Exception called when error in Drive happens
    """


class IDrive(metaclass=ABCMeta):
    """
    Interface for drive classes
    """

    @abstractmethod
    def __init__(self, path: Path, *args, **kwargs):
        """INTERFACE METHOD"""

    @abstractmethod
    def __call__(self) -> str:
        """INTERFACE METHOD"""


class FileDrive(IDrive):
    """
    Superclass of drives using files like raw or QCOW2
    """

    def size(self) -> int:
        r = cmd(
            f"qemu-img info {self._path} | grep 'virtual size' | "
            "grep -o '(.*)' | grep -o '[0-9]*'")
        return int(r.stdout)

    def __call__(self) -> str:
        argument = benedict({'drive': {'file': self._path}})
        if 'options' in self._config:
            argument.drive.merge(self._config.options)

        return parse_args([argument])

    def _fix_suffix(self, path: Path | str) -> Path:
        path = Path(path).resolve()
        if path.suffix == '':
            path = path.parent / (path.name + '.' + self._config.type)
        return path


class RawDrive(FileDrive):
    """
    Drive in RAW format, no COW snapshots
    """

    def __init__(self, path: Path,
                 *args, **kwargs):
        self._path = self._fix_suffix(path)
        self._config = benedict(kwargs)

        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            LOG.info(f'Creating RawDrive on path {self._path}')
            cmd(f"qemu-img create -f raw {self._path} {kwargs['size']}")
        else:
            LOG.info(f'Collecting RawDrive on path {self._path}')

    def clean(self) -> None:
        LOG.info(f'Recreating {self._config.type} drive on path {self._path}')
        size = self.size()
        cmd(f"rm -f {self._path}")
        cmd(f"qemu-img create -f {self._config.type} {self._path} {size}")


class QCOW2Drive(FileDrive):
    """
    Drive in QCOW2 format
    """

    def __init__(self,
                 path: Path,
                 *args, **kwargs):
        self._path = path
        self._config = benedict(kwargs)

        self._path = self._fix_suffix(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

        self.__create()

    def __create(self):
        if not self._path.exists():
            if 'backing' in self._config:
                self._config.backing = Path(self._config.backing).resolve()
                LOG.info(f'Creating QCOW2Drive at {self._path} '
                         f'using backing image at {self._config.backing}')
                r = cmd(f"qemu-img create -f qcow2 {self._path} "
                        f"-b {self._config.backing} -F qcow2")
            else:
                LOG.info(f'Creating QCOW2Drive on path {self._path}')
                r = cmd("qemu-img create -f qcow2 "
                        f"{self._path} {self._config.size}")
            if r.rc > 0:
                raise DriveError(f"Error on creating QCOW2Drive:\n{r}")
        else:
            LOG.info(f'Collecting QCOW2Drive on path {self._path}')

    def clean(self) -> None:
        LOG.info(f'Recreating {self._config.type} drive on path {self._path}')
        cmd(f"rm -f {self._path}")
        self.__create()

    def snapshot(self, name: str, overwrite=False) -> None:
        """
        create or revert to internal image snapshot
        If overwrite stated - existing snapshot deleted and created
        If not stated - existing snapshot loaded
        """
        if name in self.snapshots:
            if overwrite:
                LOG.info(f'Recreating snapshot {
                         name} QCOW2Drive on path {self._path}')
                cmd(f"qemu-img snapshot {self._path} -d {name}")
                cmd(f"qemu-img snapshot {self._path} -c {name}")
            else:
                LOG.info(f'Reverting QCOW2Drive on path {
                         self._path} to snapshot {name}')
                cmd(f"qemu-img snapshot {self._path} -a {name}")
        else:
            LOG.info(f'Creating snapshot {
                     name} QCOW2Drive on path {self._path}')
            cmd(f"qemu-img snapshot {self._path} -c {name}")

    @property
    def snapshots(self):
        return cmd("qemu-img snapshot {path} -l | awk 'NR>2 {{print $2}}'"
                   .format(path=self._path)).stdout.split('\n')

    @property
    def backing_chain(self) -> list[Path]:
        """
        Backing chain as list of paths
        """
        paths = cmd(f"qemu-img info --backing-chain {self._path} "
                    "| grep image | awk '{{print $2}}'").stdout.split('\n')
        paths.reverse()
        paths = [str(Path(x)) for x in paths]
        return paths


DRIVE_TYPES = {
    'raw': RawDrive,
    'qcow2': QCOW2Drive,
}


def Drive(*args, **kwargs):
    """
    Drive factory. Returns IDrive object according to arguments
    Also checks that size is stated in case if drive doesn't exist
    """
    LOG.debug(f'Drive factory: creating with arguments {kwargs}')

    kwargs['path'] = Path(kwargs['path'])

    if (not kwargs['path'].exists()
            and 'size' not in kwargs
            and 'backing' not in kwargs):
        raise DriveError(
            f"Drive on {kwargs['path']} doesn't exists "
            "and size or backing not stated"
        )

    if 'type' not in kwargs:
        raise DriveError("Drive type not stated")

    t = kwargs['type'].lower()
    if t in DRIVE_TYPES:
        return DRIVE_TYPES[t](*args, **kwargs)
    else:
        raise DriveError("Invalid/unsupported drive type")
