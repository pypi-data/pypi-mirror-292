# allow-extra-kwargs

A plugin for mypy that allows extra kwargs in function calls.

## Description

`allow-extra-kwargs` is a Python package that provides a decorator and a mypy plugin to allow functions to accept extra
keyword arguments in a type-safe way.

## Installation

You can install `allow-extra-kwargs` using pip:

```bash
pip install allow-extra-kwargs
```

## Usage

### Decorator Usage

To use the `allow_extra_kwargs` decorator in your code:

```python
from allow_extra_kwargs import allow_extra_kwargs


@allow_extra_kwargs
def my_function(a: int) -> int:
    return a


# Now you can call the function with extra kwargs
result = my_function(1, extra_arg="value")
```

## Mypy Plugin

To enable the mypy plugin, add the following to your pyproject.toml:

```
[tool.mypy]
plugins = ["allow_extra_kwargs.mypy"]
```
