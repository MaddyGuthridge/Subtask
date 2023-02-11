# Subtask

A simple wrapper around `subprocess.Popen` to reduce the painfulness of doing
running multiple processes concurrently.

```py
task = Subtask(['python', 'hello.py'])
task.wait()
assert task.read_stdout().strip() == "Hello, world!"
```
