"""
A simple wrapper around `subprocess.Popen` to reduce the painfulness of running
multiple processes concurrently.

Author: Maddy Guthridge
"""
__all__ = ['Subtask']
from .__subtask import Subtask
