# Task Score Calculator

The Task Score Calculator is a Python package that helps you prioritize your tasks by calculating a score based on the task's importance and effort.

## Goal

The goal of this package is to provide a simple and effective way to prioritize tasks. By assigning a score to each task based on its importance and effort, you can easily decide which tasks to tackle first.

## Installation

You can install the Task Score Calculator via pip:

```bash
pip install taskscordepm
```

## Usage

The Task Score Calculator can be used in a Python program by importing the package and creating a `Task` object:

```python
from taskscordepm.task_score import calculate_task_score

task_score = calculate_task_score(importance=3, effort=2)
```

The `Task` object has a `score` attribute that can be used to prioritize tasks:

```python
print(task.score)
```

## Contributing

Contributions to the Task Score Calculator are welcome! If you have any ideas for improvements or new features, please open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
