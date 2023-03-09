# Subtask

A simple wrapper around `subprocess.Popen` to reduce the painfulness of running
multiple processes concurrently.

```py
task = Subtask(['python', 'hello.py'])
task.wait()
assert task.read_stdout().strip() == "Hello, world!"
```

## What is Subtask for?

Subtask makes it easy to keep track of many concurrent subprocesses. It makes
it much easier to capture outputs and give inputs to these processes.

## What is Subtask not for?

Subtask is designed for simplicity. It should not be used if you want high
performance, or to chain outputs for many files together.
