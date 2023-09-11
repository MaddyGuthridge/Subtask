"""
Basic tests for subtask
"""
import pytest
from subtask import Subtask


def test_args():
    args = ['tests/programs/print_args.py', 'hello', 'world']
    task = Subtask(['python'] + args)
    task.wait()
    assert task.read_stdout().strip() == str(args)


def test_env():
    task = Subtask(
        ['python', 'tests/programs/check_env.py', 'MY_ENV_VAR'],
        env={
            "MY_ENV_VAR": "Hello world!",
        }
    )
    task.wait()
    assert task.read_stdout().strip() == "Hello world!"


def test_input():
    task = Subtask(
        ['cat'],
        input="Hello world!",
    )
    task.wait()
    assert task.read_stdout().strip() == "Hello world!"


def test_invalid_exe():
    with pytest.raises(FileNotFoundError):
        Subtask(["not_a_real_program"])
