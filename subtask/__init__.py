"""
A simple wrapper around `subprocess.Popen` to reduce the painfulness of doing
running multiple processes concurrently.

Author: Miguel Guthridge
"""
__all__ = ['Subtask']
from .__subtask import Subtask