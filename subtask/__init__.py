"""
A simple wrapper around `subprocess.Popen` to reduce the painfulness of running
multiple processes concurrently.

Author: Miguel Guthridge
"""
__all__ = ['Subtask']
from .__subtask import Subtask
