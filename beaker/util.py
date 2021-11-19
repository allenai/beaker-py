import subprocess
from typing import Generator, NamedTuple


class CmdOutput(NamedTuple):
    stdout: str
    stderr: str


def run_cmd(cmd: str) -> CmdOutput:
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True)
    return CmdOutput(stdout=result.stdout.decode(), stderr=result.stderr.decode())


def stream_cmd(cmd: str) -> Generator[str, None, None]:
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    assert process.stdout is not None
    for line in iter(process.stdout.readline, b""):
        yield line.decode().rstrip()
