from typing import (
    List,
    Tuple,
    Optional,
    NamedTuple,
)


class IsolateOptions(NamedTuple):
    meta: Optional[str] = None
    mem: Optional[int] = None
    time: Optional[int] = None
    wall_time: Optional[int] = None
    extra_time: Optional[int] = None
    box_id: Optional[int] = None
    stack: Optional[int] = None
    fsize: Optional[int] = None
    quota: Optional[Tuple[int, int]] = None
    stdin: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    stderr_to_stdout: Optional[bool] = None
    chdir: Optional[str] = None
    processes: Optional[int] = None
    share_net: Optional[bool] = None
    inherit_fds: Optional[bool] = None
    verbose: Optional[bool] = None
    silent: Optional[bool] = None

    def as_args(self) -> List[str]:
        args = []
        if self.meta is not None:
            args.extend(['--meta', self.meta])
        if self.mem is not None:
            args.extend(['--mem', self.mem])
        if self.time is not None:
            args.extend(['--time', self.time])
        if self.wall_time is not None:
            args.extend(['--wall-time', self.time])
        if self.extra_time is not None:
            args.extend(['--extra-time', self.extra_time])
        if self.box_id is not None:
            args.extend(['--box-id', self.box_id])
        if self.stack is not None:
            args.extend(['--stack', self.stack])
        if self.fsize is not None:
            args.extend(['--fsize', self.fsize])
        if self.quota is not None:
            args.extend(['--quota', self.quota])
        if self.stdin is not None:
            args.extend(['--stdin', self.stdin])
        if self.stdout is not None:
            args.extend(['--stdout', self.stdout])
        if self.stderr is not None:
            args.extend(['--stderr', self.stderr])
        if self.stderr_to_stdout is not None:
            args.extend(['--stderr-to-stdout'])
        if self.chdir is not None:
            args.extend(['--chdir', self.chdir])
        if self.processes is not None:
            args.extend(['--processes', self.processes])
        if self.share_net is not None:
            args.extend(['--share-net'])
        if self.inherit_fds is not None:
            args.extend(['--inherit-fds'])
        if self.verbose is not None:
            args.extend(['--verbose'])
        if self.silent is not None:
            args.extend(['--silent'])
        return [str(arg) for arg in args]
