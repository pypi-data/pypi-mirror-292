# _Formatter Utility_

[![test](https://github.com/korawica/fmtutil/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/korawica/fmtutil/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/korawica/fmtutil/branch/main/graph/badge.svg?token=J2MN63IFT0)](https://codecov.io/gh/korawica/fmtutil)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fmtutil?logo=pypi)](https://pypi.org/project/fmtutil/)
[![size](https://img.shields.io/github/languages/code-size/korawica/fmtutil)](https://github.com/korawica/fmtutil)

**Table of Contents**:

* [Installation](#installation)
* [Formatter Objects](#formatter-objects)
  * [Datetime](#datetime)
  * [Version](#version)
  * [Serial](#serial)
  * [Naming](#naming)
  * [Storage](#storage)
  * [Constant](#constant)
* [FormatterGroup Object](#formattergroup-object)
* [Example](#example)

This **Formatter** package was created for `parse` and `format` any string values
that match a format pattern string with Python regular expression.
This package be the co-pylot project for stating to my **Python Software Developer**
way.

:dart: First objective of this project is include necessary formatter objects for
any data components package which mean we can `parse` any complicate names on
data source and ingest the right names to in-house or data target.

## Installation

```shell
pip install -U fmtutil
```

**Dependency supported**:

| Python Version  | Installation                        |
|-----------------|-------------------------------------|
| `== 3.8`        | `pip install "fmtutil>=0.4,<0.5.0"` |
| `>=3.9,<3.13`   | `pip install -U fmtutil`            |

For example, we want to get filename with the format like, `filename_20220101.csv`,
on the file system storage, and we want to incremental ingest the latest file with
date **2022-03-25** date. So we will implement `Datetime` object and parse
that filename to it,

```python
assert (
    Datetime.parse('filename_20220101.csv', 'filename_%Y%m%d.csv').value
    == datetime.datetime(2022, 1, 1, 0)
)
```

The above example is :yawning_face: **NOT SURPRISE!!!** for us because Python
already provide the build-in `datetime` to parse by `datetime.strptime` and
format by `{dt}.strftime`. This package will be the special thing when we group
more than one format-able objects together as `Naming`, `Version`, and `Datetime`.

**For complex filename format like**:

```text
{filename:%s}_{datetime:%Y_%m_%d}.{version:%m.%n.%c}.csv
```

From above filename format string, the `datetime` package does not enough for
this scenario right? but you can handle by your hard-code object or create the
better package than this project.

> [!NOTE]
> Any formatter object was implemented the `self.valid` method for help us validate
> format string value like the above the example scenario,
> ```python
> this_date = Datetime.parse('20220101', '%Y%m%d')
> assert this_date.valid('any_files_20220101.csv', 'any_files_%Y%m%d.csv')
> ```

## Formatter Objects

* [Datetime](#datetime)
* [Version](#version)
* [Serial](#serial)
* [Naming](#naming)
* [Storage](#storage)
* [Constant](#constant)

The main purpose is **Formatter Objects** for `parse` and `format` with string
value, such as `Datetime`, `Version`, and `Serial` formatter objects. These objects
were used for parse any filename with put the format string value.

The formatter able to enhancement any format value from sting value, like in
`Datetime`, for `%B` value that was designed for month shortname (`Jan`,
`Feb`, etc.) that does not support in build-in `datetime` package.

> [!IMPORTANT]
> The main usage of this formatter object is `parse` and `format` method.

### Datetime

```python
from fmtutil import Datetime

datetime = Datetime.parse(value='Datetime_20220101_000101', fmt='Datetime_%Y%m%d_%H%M%S')
datetime.format('New_datetime_%Y%b-%-d_%H:%M:%S')
```

```text
>>> 'New_datetime_2022Jan-1_00:01:01'
```

### Version

```python
from fmtutil import Version

version = Version.parse(value='Version_2_0_1', fmt='Version_%m_%n_%c')
version.format('New_version_%m%n%c')
```

```text
>>> 'New_version_201'
```

### Serial

```python
from fmtutil import Serial

serial = Serial.parse(value='Serial_62130', fmt='Serial_%n')
serial.format('Convert to binary: %b')
```

```text
>>> 'Convert to binary: 1111001010110010'
```

### Naming

```python
from fmtutil import Naming

naming = Naming.parse(value='de is data engineer', fmt='%a is %n')
naming.format('Camel case is %c')
```

```text
>>> 'Camel case is dataEngineer'
```

### Storage

```python
from fmtutil import Storage

storage = Storage.parse(value='This file have 250MB size', fmt='This file have %M size')
storage.format('The byte size is: %b')
```

```text
>>> 'The byte size is: 2097152000'
```

### Constant

```python
from fmtutil import Constant, make_const
from fmtutil.exceptions import FormatterError

const = make_const({'%n': 'normal', '%s': 'special'})
try:
    parse_const: Constant = const.parse(value='Constant_normal', fmt='Constant_%n')
    parse_const.format('The value of %%s is %s')
except FormatterError:
    pass
```

```text
>>> 'The value of %s is special'
```

All formatter object can convert itself to constant formatter object for frozen
parsing value to constant by `.to_const()`.

> [!NOTE]
> This package already implement the environment constant object,
> `fmtutil.EnvConst`. \
> [Read more about the Formatter objects API](/docs/API.md#formatter-objects)

## FormatterGroup Object

The **FormatterGroup** object, `FormatterGroup`, which is the grouping of needed
mapping formatter objects and its alias formatter object ref name together. You
can define a name of formatter that you want, such as `name` for `Naming`, or
`timestamp` for `Datetime`.

**Parse**:

```python
from fmtutil import make_group, Naming, Datetime, FormatterGroupType

group_obj: FormatterGroupType = make_group({'name': Naming, 'datetime': Datetime})
group_obj.parse('data_engineer_in_20220101_de', fmt='{name:%s}_in_{timestamp:%Y%m%d}_{name:%a}')
```

```text
>>> {
>>>     'name': Naming.parse('data engineer', '%n'),
>>>     'timestamp': Datetime.parse('2022-01-01 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')
>>> }
```

**Format**:

```python
from fmtutil import FormatterGroup
from datetime import datetime

group_01: FormatterGroup = group_obj({'name': 'data engineer', 'datetime': datetime(2022, 1, 1)})
group_01.format('{name:%c}_{timestamp:%Y_%m_%d}')
```

```text
>>> dataEngineer_2022_01_01
```

## Example

If you have multi-format filenames on the data source directory, and you want to
dynamic getting max datetime on these filenames to your app, you can use a
formatter group.

```python
from fmtutil import (
  make_group, Naming, Datetime, FormatterGroup, FormatterGroupType, FormatterArgumentError,
)

name: Naming = Naming.parse('Google Map', fmt='%t')

fmt_group: FormatterGroupType = make_group({
    "naming": name.to_const(),
    "timestamp": Datetime,
})

rs: list[FormatterGroup] = []
for file in (
    'googleMap_20230101.json',
    'googleMap_20230103.json',
    'googleMap_20230103_bk.json',
    'googleMap_with_usage_20230105.json',
    'googleDrive_with_usage_20230105.json',
):
    try:
        rs.append(
            fmt_group.parse(file, fmt=r'{naming:c}_{timestamp:%Y%m%d}\.json')
        )
    except FormatterArgumentError:
        continue

repr(max(rs).groups['timestamp'])
```

```text
>>> <Datetime.parse('2023-01-03 00:00:00.000000', '%Y-%m-%d %H:%M:%S.%f')>
```

> [!TIP]
> The above **Example** will convert the `name`, **Naming** instance, to **Constant**
> instance before passing to the **Formatter Group** because it does not want
> to dynamic parsing this format when find any matching filenames at destination
> path.

## License

This project was licensed under the terms of the [MIT license](LICENSE).
