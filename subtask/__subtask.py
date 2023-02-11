"""
A simple wrapper around `subprocess.Popen` to reduce the painfulness of doing
running multiple processes concurrently.

Author: Miguel Guthridge
"""
import os
import subprocess
import signal
import time
from pathlib import Path
from typing import Optional, Callable


def output_folder():
    """Create the ./output/ directory if needed"""
    try:
        os.mkdir('output', )
    except FileExistsError:
        pass


class Subtask:
    """
    Simple wrapper around `subprocess.Popen`
    """
    process: Optional[subprocess.Popen]
    """Access to the underlying Popen object"""
    stdout: Optional[Path]
    """Location of the file containing stdout"""
    stderr: Optional[Path]
    """Location of the file containing stderr"""

    def __init__(
        self,
        name: str,
        args: list[str],
        live_output: bool = False,
        env: Optional[dict[str, str]] = None,
        wait_for: Optional[Callable[[], bool]] = None,
    ):
        """
        Create a Subtask.

        ## Args
        * `name`: name of task (used for output files)
        * `args`: list of args for program to run (eg ['python', 'foo.py'])
        * `live_output`: whether to print the subtask's output live or not
        * `env`: dictionary of environment variables to add into the
          environment of the subprocess.
        * `wait_for`: a callback to determine whether the task has started. It
          will be continually called until it returns `True`. Useful for web
          servers which take a hot minute to start up.
        """
        if wait_for is None:
            wait_for = lambda: True  # noqa: E731
        self.process = None
        curr_env = os.environ.copy()
        if env is not None:
            curr_env.update(env)
        output_folder()
        if live_output:
            self.__stdout = None
            self.__stderr = None
            self.stdout = None
            self.stderr = None
        else:
            self.stdout = Path(f"output/{name}.stdout.txt")
            self.stderr = Path(f"output/{name}.stderr.txt")
            self.__stdout = open(self.stdout, 'w')
            self.__stderr = open(self.stderr, 'w')
        self.process = subprocess.Popen(
            args,
            stdout=self.__stdout,
            stderr=self.__stderr,
            env=curr_env
        )
        # Request until we get a success, but crash if we failed to start
        # in 10 seconds
        start_time = time.time()
        started = False
        while time.time() - start_time < 10:
            if wait_for():
                started = True
                break
        if not started:
            raise RuntimeError(f"{name} failed to start in time")

    def __del__(self):
        # Always kill the subprocess when this goes out of scope, so we don't
        # end up with an orphaned process
        self.kill()

    def close_files(self):
        if self.__stdout is not None:
            self.__stdout.close()
        if self.__stderr is not None:
            self.__stderr.close()

    def interrupt(self):
        """Interrupt the process (like pressing Ctrl+C)"""
        if self.process is not None:
            self.process.send_signal(signal.SIGINT)
        self.close_files()

    def kill(self):
        """Kill the process forcefully (useful if it's not responding)"""
        if self.process is not None:
            self.process.kill()
        self.close_files()

    def wait(self):
        """Wait for the process to finish executing and return its exit code"""
        if self.process is None:
            raise ValueError("Process not started")
        ret = self.process.wait()
        self.close_files()
        return ret

    def poll(self):
        """Poll the process, returning `None` if it's still running, or its
        exit code if it has finished.
        """
        if self.process is None:
            raise ValueError("Process not started")
        ret = self.process.poll()
        if ret is not None:
            self.close_files()
        return ret
