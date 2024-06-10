"""
A simple wrapper around `subprocess.Popen` to reduce the painfulness of running
multiple processes concurrently.

Author: Maddy Guthridge
"""
import os
import subprocess
import signal
import time
from typing import overload
from tempfile import TemporaryFile
from pathlib import Path
from typing import Optional, Callable


class Subtask:
    """
    Simple wrapper around `subprocess.Popen`
    """

    def __init__(
        self,
        args: list[str],
        live_output: bool = False,
        env: Optional[dict[str, str]] = None,
        wait_for: Optional[Callable[[], bool]] = None,
        input: Optional[str] = None,
    ) -> None:
        """
        Create a Subtask.

        ## Args
        * `args`: list of args for program to run (eg ['python', 'foo.py'])
        * `live_output`: whether to print the subtask's output live or not
        * `env`: dictionary of environment variables to add into the
          environment of the subprocess.
        * `wait_for`: a callback to determine whether the task has started. It
          will be continually called until it returns `True`. Useful for web
          servers which take a hot minute to start up.
        * `input`: an input string to be passed to the task
        """
        if wait_for is None:
            wait_for = lambda: True  # noqa: E731
        curr_env = os.environ.copy()
        if env is not None:
            curr_env.update(env)
        if live_output:
            self.stdout = None
            self.stderr = None
        else:
            self.stdout = TemporaryFile()
            self.stderr = TemporaryFile()
        if input is None:
            self.stdin = None
        else:
            self.stdin = TemporaryFile('w')
            self.stdin.write(input)
            self.stdin.seek(0)
        self.process = subprocess.Popen(
            args,
            stdin=self.stdin,
            stdout=self.stdout,
            stderr=self.stderr,
            env=curr_env
        )
        """Access to the underlying Popen object"""

        # Request until we get a success, but crash if we failed to start
        # in 10 seconds
        start_time = time.time()
        started = False
        while time.time() - start_time < 10:
            if wait_for():
                started = True
                break
        if not started:
            raise RuntimeError("Failed to start process in time")

    def __del__(self) -> None:
        # Always kill the subprocess when this goes out of scope, so we don't
        # end up with an orphaned process
        self.kill()

    def write_stdout(self, output: Path) -> None:
        """Write the task's stdout to a file"""
        if self.stdout is None:
            raise ValueError("Cannot write output to file if output was "
                             "written to terminal")
        self.stdout.seek(0)
        with open(output, 'w+b') as f:
            f.write(self.stdout.read())

    def write_stderr(self, output: Path) -> None:
        """Write the task's stderr to a file"""
        if self.stderr is None:
            raise ValueError("Cannot write output to file if output was "
                             "written to terminal")
        self.stderr.seek(0)
        with open(output, 'w+b') as f:
            f.write(self.stderr.read())

    def read_stdout(self) -> str:
        """read the task's stdout to a file"""
        if self.stdout is None:
            raise ValueError("Cannot read output if output was "
                             "written to terminal")
        self.stdout.seek(0)
        return self.stdout.read().decode()

    def read_stderr(self) -> str:
        """read the task's stderr to a file"""
        if self.stderr is None:
            raise ValueError("Cannot read output if output was "
                             "written to terminal")
        self.stderr.seek(0)
        return self.stderr.read().decode()

    def interrupt(self) -> None:
        """Interrupt the process (like pressing Ctrl+C)"""
        self.process.send_signal(signal.SIGINT)

    def kill(self) -> None:
        """Kill the process forcefully (useful if it's not responding)"""
        self.process.kill()

    @overload
    def wait(self, timeout: float) -> Optional[int]:
        ...

    @overload
    def wait(self) -> int:
        ...

    @overload
    def wait(self, timeout: None = None) -> int:
        ...

    def wait(self, timeout: Optional[float] = None) -> Optional[int]:
        """Wait for the process to finish executing and return its exit code"""
        try:
            ret = self.process.wait(timeout)
        except subprocess.TimeoutExpired:
            return None
        return ret

    def wait_for_zero(self, timeout: Optional[float] = None) -> None:
        """
        Wait for the process to finish executing, then assert that its exit
        code is zero.

        If the timeout is exceeded, an exception is raised.
        """
        status = self.wait(timeout)
        if status is None:
            raise TimeoutError('The process did not exit in time')
        elif status != 0:
            raise RuntimeError(f'The process exited with code {status}')

    def poll(self) -> Optional[int]:
        """Poll the process, returning `None` if it's still running, or its
        exit code if it has finished.
        """
        ret = self.process.poll()
        return ret
