# Data Utility Packages: _Core_

[![test](https://github.com/korawica/ddeutil/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/ddeutil/actions/workflows/tests.yml)
[![python support version](https://img.shields.io/pypi/pyversions/ddeutil)](https://pypi.org/project/ddeutil/)
[![size](https://img.shields.io/github/languages/code-size/korawica/ddeutil)](https://github.com/korawica/ddeutil)

**Table of Contents**:

- [Installation](#installation)
- [Features](#features)
  - [Base Utility Functions](#base-utility-functions)
  - [Utility Functions](#utility-functions)

The **Core Utility** package implements the utility functions and objects
that was created on sub-package namespace, `ddeutil`, design for independent
installation. I make this package able to extend with any sub-extension with
this namespace. This namespace able to scale out the coding with folder
structure design. You can add any extension features and import by
`import ddeutil.{extension}`.

> [!NOTE]
> This package provide the Base Utility functions and objects for any sub-namespace
> package that use for data function or application.

## Installation

```shell
pip install -U ddeutil
```

## Features

This Core package will implement all of reusable functions and objects that does
not re-create again because it is basic code but has a lot of coding.

```text
core
  - base
    - cache
    - checker
    - convert
    - hash
    - merge
    - sorting
    - splitter
  - decorator
  - dtutils
  - randomly
```

### OnlyOne

```python
from ddeutil.core import onlyone

assert 'a' == onlyone(['a', 'b'], ['a', 'b', 'c'])
assert 'c' == onlyone(('a', 'b'), ['c', 'e', 'f'])
assert onlyone(['a', 'b'], ['c', 'e', 'f'], default=False) is None
```

### Instance Check

```python
from ddeutil.core import isinstance_check
from typing import Union, Optional

assert isinstance_check("s", str)
assert isinstance_check(["s"], list[str])
assert isinstance_check(("s", "t"), tuple[str, ...])
assert not isinstance_check(("s", "t"), tuple[str])
assert isinstance_check({"s": 1, "d": "r"}, dict[str, Union[int, str]])
assert isinstance_check("s", Optional[str])
assert isinstance_check(1, Optional[Union[str, int]])
assert not isinstance_check("s", list[str])
```

## License

This project was licensed under the terms of the [MIT license](LICENSE).
