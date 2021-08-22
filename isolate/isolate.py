import logging
import os
import subprocess

from contextlib import contextmanager
from pathlib import Path
from typing import (
    List,
    Optional
)

from .options import IsolateOptions
from .utils import remove_directory_contents

logger = logging.getLogger(__name__)


class IsolateException(Exception):
    """General exception type for the package"""
    pass


class IsolateInitException(Exception):
    """Exception type thrown during the initialisation of an isolate workspace"""
    pass


class IsolateSandbox:
    """Class representing an isolate sandbox"""

    def __init__(self, options: IsolateOptions, workdir: str, box_id: str) -> None:
        """Constructor for IsolateSandbox

        Args:
            options (IsolateOptions): The options used to initialise the sandbox
            workdir (str): The working directory for the sandbox
            box_id (str): The unique ID associated with this sandbox
        """
        self.options = options
        self.box_id = box_id
        self.workdir = workdir
        self.boxdir = os.path.join(workdir, 'box')
        self.tmpdir = os.path.join(workdir, 'tmp')

    def add_file(self, source: str, destination: Optional[str] = None) -> None:
        """Copies a file from the host to the sandbox

        Args:
            source (str): A path to a file on the host system
            destination (str, optional): A destination path relative to the sandbox working directory. 
                                         Defaults to '<working directory>/box/<file name>' if not provided.

        Raises:
            IsolateException: If the destination path is not within the working directory
            IsolateException: If the source file path does not exist
        """
        # If destination is not specified, just copy the file to boxdir
        if destination is None:
            destination = os.path.join(self.boxdir, os.path.basename(source))

        # If the destination path is an absolute path, ensure that it is within boxdir
        if os.path.isabs(destination) and not destination.startswith(self.boxdir):
            raise IsolateException(
                f"Absolute destination path provided: '{destination}' \
                    is not within the sandbox box directory: {self.boxdir}")

        if not os.path.exists(source):
            raise IsolateException(
                f"Source file path provided: '{source}' does not exist")

        # If the destination path is a relative path, make it an absolute path wrt. to boxdir
        if not os.path.isabs(destination):
            destination = os.path.join(self.boxdir, destination)

        # Create any necessary directories at the destination
        if not os.path.exists(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination), mode=0o700)

        # Touch and own the destination file
        Path(destination).touch()
        os.chown(destination, uid=os.getuid(), gid=os.getgid())

        # Copy from source to destination
        with open(destination, 'w') as dest_fd, \
                open(source, 'r') as source_fd:
            for line in source_fd:
                dest_fd.write(line)

    # TODO: Wrap the results of this function in an IsolateResult class,
    #   providing an interface for the output metadata
    def run(self, run_args: List[str]) -> subprocess.CompletedProcess:
        """Runs a program in the sandbox

        Args:
            run_args (List[str]): A list of program arguments; the program to execute is the first item in `args`.

        Returns:
            subprocess.CompletedProcess: The result of executing `isolate --run`
        """
        args = ['isolate', '--run']
        args.extend(self.options.as_args())
        args.extend(['--'])
        args.extend(run_args)
        process: subprocess.CompletedProcess = subprocess.run(
            args,
            capture_output=True
        )
        logger.debug(process)
        return process

    def cleanup(self) -> None:
        """Cleans up the isolate sandbox

        Raises:
            IsolateException: If the clean-up step fails for any reason
        """
        # Remove all files from the box before cleaning up (see: https://github.com/ioi/isolate/issues/77)
        remove_directory_contents(self.boxdir)

        logging.info(f"Closing isolate sandbox: {self}")
        process: subprocess.CompletedProcess = subprocess.run(
            ['isolate', '--cleanup', '--box-id', self.box_id],
            capture_output=True
        )
        logger.debug(process)
        if process.returncode != 0:
            raise IsolateException(
                f"({process.returncode}) {process.stdout.decode() + process.stderr.decode()}")

    def __str__(self):
        return f"IsolateSandbox(workdir='{self.workdir}', box_id='{self.box_id}')"


@contextmanager
def isolate(options: IsolateOptions = IsolateOptions(), cleanup=True):
    """A context-managed function to create an isolate sandbox 

    Args:
        options (IsolateOptions, optional): Options for initialising the isolate sandbox, arguments will be later 
                                            re-used for running programs in the sandbox.
        cleanup (bool, optional): If false, will retain the sandbox for later inspection. Defaults to True.

    Raises:
        IsolateInitException: If the sandbox failed to initialise

    Yields:
        IsolateSandbox: The isolate sandbox
    """
    args: List[str] = ['isolate', '--init']
    args.extend(options.as_args())

    sandbox: Optional[IsolateSandbox] = None

    try:
        process: subprocess.CompletedProcess = subprocess.run(
            args, capture_output=True)
        logger.debug(process)
        if process.returncode != 0:
            raise IsolateInitException(
                f"[{process.returncode}] {process.stdout.decode() + process.stderr.decode()}")

        workdir = process.stdout.decode().strip()
        sandbox = IsolateSandbox(options, workdir, str(options.box_id))
        logging.info(f"Created isolate sandbox: {sandbox}")
        yield sandbox

    except Exception as e:
        raise IsolateInitException(str(e))

    finally:
        if sandbox is not None and cleanup:
            sandbox.cleanup()
