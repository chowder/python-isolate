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
    pass


class IsolateInitException(Exception):
    pass


class IsolateSandbox:
    def __init__(self, options: IsolateOptions, workdir: str, box_id: str) -> None:
        self.options = options
        self.box_id = box_id
        self.workdir = workdir
        self.boxdir = os.path.join(workdir, 'box')
        self.tmpdir = os.path.join(workdir, 'tmp')

    def add_file(self, source: str, destination: Optional[str] = None) -> None:
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
                f"Source file path provided: '{source} does not exist")

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
