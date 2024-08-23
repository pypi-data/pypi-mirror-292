# ------------------------------------------------------------------------------
# Copyright (c) 2022 Korawich Anuttra. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root for
# license information.
# ------------------------------------------------------------------------------
"""
Note:
        This file is assert of formatter value that will passing for generate
    any formatter object. I will use it instead create sub-class form Formatter
    class for simple and scalable usage.

        It will use the Pydantic BaseModel class instead the origin object for
    fast validate the asset value and able to create a new formatter object with
    changing the asset field.

        I will start define the concept but it does not fit will my creation
    flow. It will be finish on the major version 2.0

Migration Note:

*   I will improve the scalable of the Formatter object that able to transform
    coding from Python to Rust.
*   Change the initialize process of Formatter object that using dynamic self
    attributes to fixing attribute with dynamic asset instead.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from functools import lru_cache, partial, total_ordering
from typing import Any, Callable, ClassVar, Optional, Union

from typing_extensions import Self, TypeAlias, TypeVar

from fmtutil.exceptions import (
    FormatterArgumentError,
    FormatterKeyError,
    FormatterValueError,
)
from fmtutil.formatter import (
    ConstantType,
    dict2const,
)
from fmtutil.utils import bytes2str, can_int, itself, remove_pad, scache

T = TypeVar("T")
DictStr: TypeAlias = dict[str, str]
String: TypeAlias = Union[str, bytes]
TupleInt: TypeAlias = tuple[int, ...]
TupleStr: TypeAlias = tuple[str, ...]


@dataclass
class BaseFormat:
    """Base Format Dataclass for the Asset mapping value with any format string
    matching."""

    alias: str
    fmt: Callable[[str], Callable[[], str]]


@dataclass
class CommonFormat(BaseFormat):
    regex: str
    parse: Callable[[str], str]
    level: Union[int, TupleInt] = field(default=(0,))


@dataclass
class CombineFormat(BaseFormat):
    cregex: str
    level: Union[int, TupleInt] = field(default=(0,))


Format = Union[CommonFormat, CombineFormat]


@dataclass
class ConfigFormat:
    default_fmt: str
    validator: Callable[[Any], Any] = field(default_factory=itself)


def asset_format(value: dict[str, Any]) -> Format:
    """Parsing any mapping value to Format dataclass."""
    if "regex" in value.keys() and "cregex" in value.keys():
        raise ValueError("Format does not support for getting all regex keys.")
    elif "regex" in value.keys():
        return CommonFormat(**value)
    elif "cregex" in value.keys():
        return CombineFormat(**value)
    raise ValueError("Format does not have any regex key, `regex` or `cregex`.")


@total_ordering
class Formatter(ABC):
    """The Asset Formatter object that will be the abstract parent class for any
    formatter sub-class object with the asset construction.

        Formatter object for inherit to any formatter subclass that define
    format and parse method. The base class will implement necessary
    properties and method for subclass that should implement or enhance such
    as `the cls.formatter()` method or the `cls.priorities` property.

    .. class attributes::
        * asset: dict[str, Format]
            A asset mapping with format string and Format object.
        * config: ConfigFormat
            A ConfigFormat object for this sub-class formatter.
        * level: int
            The maximum level of slot level of this instance.
    """

    asset: ClassVar[dict[str, Format]]
    config: ClassVar[ConfigFormat]
    level: ClassVar[int]

    def __init_subclass__(
        cls: type[Self],
        /,
        level: int = 1,
        asset: dict[str, Format] | None = None,
        config: ConfigFormat | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        cls.level: int = level  # type: ignore
        cls.asset: dict[str, Format] = asset or cls.asset  # type: ignore
        cls.config: ConfigFormat = config or cls.config  # type: ignore

        if cls.asset is None:
            raise NotImplementedError(
                "Should define the `asset` class variable for create a new "
                "formatter object"
            )
        elif all(isinstance(fmt, dict) for fmt in cls.asset.values()):
            raise FormatterValueError(
                "Please convert asset value to Format type with "
                "``asset_format`` func"
            )
        if cls.config is None:
            raise NotImplementedError(
                "Should define the `config` class variable for default values "
                "of a new formatter object"
            )

    @abstractmethod
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError(
            "Formatter should implement ``self.__init__`` for validate "
            "incoming parsing values"
        )

    def __hash__(self) -> int:
        """Return the hashed ``self.str`` attribute."""
        return hash(self.string)

    def __str__(self) -> str:
        """Return the ``self.str`` attribute that is the abstractmethod."""
        return self.string

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}"
            f".parse('{self.string}', "
            f"'{self.config.default_fmt}')>"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value  # type: ignore

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value.__lt__(other.value)  # type: ignore

    @property
    def string(self) -> str:
        """Return a string of ``self.value`` property that define with abstract
        property of this formatter object.

        :rtype: str
        """
        return str(self.value)

    @classmethod
    def from_value(cls, value: Any) -> Self:
        """Passer the value to this formatter that will pass this value to
        ``cls.formatter`` method and map with the base format string value
        before parse by ``cls.parse``."""

        fmt_filter = [
            (k, fmt.fmt(cls.prepare_value(value))())
            for k, fmt in cls.asset.items()
            if k in re.findall("(%[-+!*]?[A-Za-z])", cls.config.default_fmt)
        ]
        fmts, values = zip(*fmt_filter)
        return cls.parse(value="_".join(values), fmt="_".join(fmts))

    @classmethod
    def parse(
        cls,
        value: String,
        fmt: Optional[str] = None,
        *,
        strict: bool = False,
    ) -> Self:
        """Parse bytes or string value with its format to this formatter object.
        This method generates the value for itself data that can be formatted
        to another format string values.
        """
        _fmt: str = fmt or cls.config.default_fmt
        _value: str = bytes2str(value)

        if not _fmt:
            raise NotImplementedError(
                "This Formatter class does not set default format string "
                "value."
            )

        _fmt = cls.gen_format(_fmt)
        if _search := re.search(rf"^{_fmt}$", _value):
            return cls(
                **cls.__init_parsing__(
                    cls.__validate_format(_search.groupdict()),
                    set_strict_mode=strict,
                )
            )

        raise FormatterValueError(
            f"value {_value!r} does not match with format {_fmt!r}"
        )

    @classmethod
    def gen_format(
        cls,
        fmt: str,
        *,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        alias: bool = True,
    ) -> str:
        """Generate format string value that combine from any matching of
        format name with format regular expression value that able to search.
        """
        _cache: dict[str, int] = defaultdict(int)
        _prefix: str = prefix or ""
        _suffix: str = suffix or ""
        regexes = cls.regex()
        for fmt_match in re.finditer(r"(%?%[-+!*]?[A-Za-z])", fmt):
            fmt_str: str = fmt_match.group()
            if fmt_str.startswith("%%"):
                fmt = fmt.replace(fmt_str, fmt_str[1:], 1)
                continue
            if fmt_str not in regexes:
                raise FormatterArgumentError(
                    "fmt",
                    (
                        f"The format string, {fmt_str!r}, does not exists in "
                        f"``cls.regex``."
                    ),
                )
            regex: str = regexes[fmt_str]
            insided: bool = False
            for fmt_inside in re.finditer(
                r"\(\?P<(?P<alias>\w+)>(?P<fmt>(?:(?!\(\?P<\w+>).)*)\)",
                regex,
            ):
                _sr_re: str = fmt_inside.group("alias")
                regex = re.sub(
                    rf"\(\?P<{_sr_re}>",
                    (
                        (
                            f"(?P<{_prefix}{_sr_re}{scache(_cache[_sr_re])}"
                            f"{_suffix}>"
                        )
                        if alias
                        else "("
                    ),
                    regex,
                    count=1,
                )
                _cache[_sr_re] += 1
                insided = True
            if not insided:
                raise FormatterValueError(
                    "Regex format string does not set group name for "
                    "parsing value to its class."
                )
            fmt = fmt.replace(fmt_str, regex, 1)
        return fmt

    @classmethod
    @lru_cache(maxsize=None)
    def regex(cls) -> DictStr:
        """Return a dict of format string, and it's regular expression value
        that was generated from values of ``cls.asset``. This class-method
        was wrapped with ``lru_cache`` function for more frequency getting this
        ``cls.regex()`` value because the value does not change depend on the
        formatter class.
        """
        results: DictStr = {}
        pre_results: DictStr = {}
        for f, fmt in cls.asset.items():
            if isinstance(fmt, CommonFormat):
                fmt_regex: str = fmt.regex
                # TODO: Implement this for dynamic config
                # for conf in re.finditer(r'conf\.(?P<var>[A-Z_]+)', fmt_regex):
                #     var: str = conf.group('var')
                #     if conf_var := getattr(cls.config, var):
                #         fmt_regex = fmt_regex.replace(conf.group(0), conf_var)
                #     else:
                #         raise FormatterArgumentError(
                #             "config",
                #             "does not found {var} that set on config"
                #         )
                results[f] = f"(?P<{fmt.alias}>{fmt_regex})"
            elif isinstance(fmt, CombineFormat):
                pre_results[f] = fmt.cregex
            else:
                raise FormatterValueError(
                    "formatter does not contain `regex` or `cregex` "
                    "in dict value"
                )
        for f, cr in pre_results.items():
            cr = cr.replace("%%", "[ESCAPE]")
            for cm in re.finditer(r"(%[-+!*]?[A-Za-z])", cr):
                cs: str = cm.group()
                if cs in results:
                    cr = cr.replace(cs, results[cs], 1)
                else:
                    raise FormatterArgumentError(
                        "format",
                        (
                            f"format cregex string that contain {cs} regex "
                            f"does not found."
                        ),
                    )
            results[f] = cr.replace("[ESCAPE]", "%%")
        return results

    @staticmethod
    def __validate_format(formats: DictStr | None = None) -> DictStr:
        results: DictStr = {}
        _formats: DictStr = formats or {}
        for fmt in _formats:
            _fmt: str = fmt.split("__", maxsplit=1)[0]
            if _fmt not in results:
                results[_fmt] = _formats[fmt]
                continue
            if results[_fmt] != _formats[fmt]:
                raise FormatterValueError(
                    "Parsing with some duplicate format name that have "
                    "value do not all equal."
                )
        return results

    @classmethod
    def __init_parsing__(
        cls,
        parsing: DictStr,
        set_strict_mode: bool = False,
    ) -> dict[str, Any]:
        """Initialize after parsing value from ``cls.parse``."""
        # NOTE: This function was migrated from __init__ method.
        rs: dict[str, Any] = {}
        for value in cls.asset.values():
            if isinstance(value, CombineFormat):
                continue

            name: str = value.alias
            attr: str = name.split("_", maxsplit=1)[0]

            if getter := rs.get(attr):
                if not set_strict_mode:
                    continue

                # NOTE: Start strict mode
                elif name in parsing and getter != (
                    p := value.parse(parsing[name])
                ):
                    raise FormatterValueError(
                        f"Parsing duplicate values do not equal, {getter} and "
                        f"{p}, in ``self.{attr}`` with strict mode."
                    )
            elif name in parsing:
                rs[attr] = value.parse(parsing[name])
        return rs

    @property
    @abstractmethod
    def value(self) -> Any:  # pragma: no cover  # type: ignore
        raise NotImplementedError(
            "Please implement ``value`` property for sub-formatter object"
        )

    def values(self, value: Any | None = None) -> DictStr:
        """Return a dict of format string, and it's string value that was passed
        an input value to `cls.formatter` method.

        :rtype: DictStr
        :returns: A dict of format string, and it's string value that was passed
            an input value to `cls.formatter` method.

            Example:
                {
                    "%n": "normal-value",
                    "%N": "NORMAL-UPPER-VALUE",
                    ...
                }
        """
        return {
            f: fmt.fmt(value or self.value)() for f, fmt in self.asset.items()
        }

    def format(self, fmt: str) -> str:
        """Return a string value that was formatted and filled by an input
        format string pattern.

        :param fmt: A format string value for mapping with formatter.
        :type fmt: str

        :raises KeyError: if it has any format pattern does not found in
            `cls.formatter`.

        :rtype: str
        :returns: A string value that was formatted from format string pattern.
        """
        fmt = fmt.replace("%%", "[ESCAPE]")
        for _fmt_match in re.finditer(r"(%[-+!*]?[A-Za-z])", fmt):
            _fmt_str: str = _fmt_match.group(0)
            try:
                _value = self.asset[_fmt_str].fmt(self.value)
                fmt = fmt.replace(_fmt_str, _value())
            except KeyError as err:
                raise FormatterKeyError(
                    f"the format: {_fmt_str!r} does not support for "
                    f"{self.__class__.__name__!r}"
                ) from err
        return fmt.replace("[ESCAPE]", "%")

    def valid(self, value: str, fmt: str) -> bool:
        """Return a True value if the value from ``cls.parse`` of a string
        value, and a format string pattern is valid with ``self.value``.

        :param value: A string value that want to parse with a format string.
        :type value: str
        :param fmt: A format string pattern.
        :type fmt: str
        """
        return self.value.__eq__(  # type: ignore
            self.__class__.parse(value, fmt).value,
        )

    def to_const(self) -> ConstantType:
        """Convert this formatter instance to Constant object that have class
        name with ``f'{self.__class__.__name__}Const'`` with ``self.values()``.

        :rtype: ConstantType
        :returns: A Constant object that create from constant of ``self.values``
            and has class name with ``f'{self.__class__.__name__}Const'`` with
            ``self.values()``.
        """
        return dict2const(
            self.values(),
            name=f"{self.__class__.__name__}Const",
            base_fmt=self.config.default_fmt,
        )

    @staticmethod
    @abstractmethod
    def prepare_value(value: Any) -> Any:
        """Prepare value before passing to convert logic in the formatter
        method that define by property of this formatter object.

        :param value: A value that want to prepare before passing to formatter.
        :type value: Any

        :rtype: Any
        :returns: A prepared value with defined logic.
        """
        raise NotImplementedError(
            "Please implement ``prepare_value`` static method for this "
            "sub-formatter class."
        )

    def __add__(self, other: Any) -> Self:
        if not isinstance(other, self.__class__):
            try:
                return self.__class__.from_value(value=self.value + other)
            except FormatterValueError:
                return NotImplemented
        return self.__class__.from_value(value=self.value + other.value)

    def __sub__(self, other: Any) -> Self:
        if not isinstance(other, self.__class__):
            try:
                return self.__class__.from_value(value=(self.value - other))
            except FormatterValueError:
                return NotImplemented
        return self.__class__.from_value(value=(self.value - other.value))

    def __radd__(self, other: Any) -> Self:
        return self.__add__(other)

    def __rsub__(self, other: T) -> T:
        if not isinstance(other, type(self.value)):
            return NotImplemented
        return other - self.value  # type: ignore

    def __format__(self, fmt_spec: str) -> str:
        """Format a formatter object with any formatter setting value."""
        return self.format(fmt_spec)


SERIAL_MAX_PADDING: int = 3
SERIAL_MAX_BINARY: int = 8


def to_padding(value: str) -> str:
    return value.rjust(SERIAL_MAX_PADDING, "0") if value else ""


def to_binary(value: str) -> str:
    return f"{int(value):0{str(SERIAL_MAX_BINARY)}b}" if value else ""


SERIAL_ASSET: dict[str, Format] = {
    "%n": asset_format(
        {
            "alias": "number",
            "regex": r"[0-9]*",
            "fmt": lambda x: partial(itself, str(x)),
            "parse": lambda x: x,
            "level": 1,
        }
    ),
    "%p": asset_format(
        {
            "alias": "number_pad",
            "regex": rf"[0-9]{{{SERIAL_MAX_PADDING}}}",
            "fmt": lambda x: partial(to_padding, str(x)),
            "parse": lambda x: remove_pad(x),
            "level": 1,
        }
    ),
    "%b": asset_format(
        {
            "alias": "number_binary",
            # TODO: Change this value:
            #   ... "regex": rf"[0-1]{conf.SERIAL_MAX_BINARY}",
            "regex": rf"[0-1]{{{SERIAL_MAX_BINARY}}}",
            "fmt": lambda x: partial(to_binary, str(x)),
            "parse": lambda x: str(int(x, 2)),
            "level": 1,
        }
    ),
    "%c": asset_format(
        {
            "alias": "number_comma",
            "regex": r"\d{1,3}(?:,\d{3})*",
            "fmt": lambda x: partial(itself, f"{x:,}"),
            "parse": lambda x: x.replace(",", ""),
            "level": 1,
        }
    ),
    "%u": asset_format(
        {
            "alias": "number_underscore",
            "regex": r"\d{1,3}(?:_\d{3})*",
            "fmt": lambda x: partial(itself, f"{x:_}"),
            "parse": lambda x: x.replace("_", ""),
            "level": 1,
        }
    ),
}


SERIAL_CONF = ConfigFormat(default_fmt="%n")


class Serial(Formatter, asset=SERIAL_ASSET, config=SERIAL_CONF):
    """Serial Formatter object that build from SERIAL_ASSET value."""

    def __init__(self, number: int | str | float | None = None) -> None:
        self.number: int = self.prepare_value(number)

    @property
    def string(self) -> str:
        return str(self.number)

    @property
    def value(self) -> int:
        return self.number

    @staticmethod
    def prepare_value(value: int | str | float | None) -> int:
        """Prepare value before passing to convert logic in the formatter
        method that define by property of this formatter object. Return 0 if an
        input value does not pass.

        :param value: A value that want to prepare before passing to this
            serial formatter.
        :type value: int | str | float | None

        :raises FormatterValueError: If an input value does not able cast to
            integer, or it's value less than 0.

        :rtype: int
        :returns: A prepared positive integer value.
        """
        if value is None:
            return 0
        if not can_int(value) or ((prepare := int(float(value))) < 0):
            raise FormatterValueError(
                f"Serial formatter does not support for, {value!r}."
            )
        return prepare


DATETIME_ASSET: dict[str, Format] = {
    "%n": asset_format(
        {
            "alias": "normal",
            "cregex": "%Y%m%d_%H%M%S",
            "fmt": lambda x: partial(x.strftime, "%Y%m%d_%H%M%S"),
        }
    ),
    "%Y": asset_format(
        {
            "alias": "year",
            "regex": r"\d{4}",
            "fmt": lambda x: partial(x.strftime, "%Y"),
            "parse": lambda x: x,
            "level": 10,
        }
    ),
    # "": asset_format(
    #     {
    #         "alias": "year_cut_pad",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: f"19{x}",
    #         "level": 10,
    #     }
    # ),
    # "": asset_format(
    #     {
    #         "alias": "year_cut",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: f"19{x}",
    #         "level": 10,
    #     }
    # ),
    # "": asset_format(
    #     {
    #         "alias": "month",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: x.rjust(2, "0"),
    #         "level": 9,
    #     }
    # ),
    "%m": asset_format(
        {
            "alias": "month_pad",
            "regex": "01|02|03|04|05|06|07|08|09|10|11|12",
            "fmt": lambda x: partial(x.strftime, "%m"),
            "parse": lambda x: x,
            "level": 9,
        }
    ),
    # "": asset_format(
    #     {
    #         "alias": "month_short",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: MONTHS[x],
    #         "level": 9,
    #     }
    # ),
    # "": asset_format(
    #     {
    #         "alias": "month_full",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: MONTHS[x[:3]],
    #         "level": 9,
    #     }
    # ),
    # "": asset_format(
    #     {
    #         "alias": "day",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: x.rjust(2, "0"),
    #         "level": 8,
    #     }
    # ),
    "%d": asset_format(
        {
            "alias": "day_pad",
            "regex": "[0-3][0-9]",
            "fmt": lambda x: partial(x.strftime, "%d"),
            "parse": lambda x: x,
            "level": 8,
        }
    ),
    # "": asset_format(
    #     {
    #         "alias": "day_year",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: x.rjust(2, "0"),
    #         "level": (8, 9),
    #     }
    # ),
    # "": asset_format(
    #     {
    #         "alias": "day_year_pad",
    #         "regex": r"",
    #         "fmt": "",
    #         "parse": lambda x: x.rjust(2, "0"),
    #         "level": (8, 9),
    #     }
    # ),
    "%H": asset_format(
        {
            "alias": "hour_pad",
            "regex": "[0-2][0-9]",
            "fmt": lambda x: partial(x.strftime, "%H"),
            "parse": lambda x: x,
            "level": 0,
        }
    ),
    "%M": asset_format(
        {
            "alias": "minute_pad",
            "regex": "[0-6][0-9]",
            "fmt": lambda x: partial(x.strftime, "%M"),
            "parse": lambda x: x,
            "level": 0,
        }
    ),
    "%S": asset_format(
        {
            "alias": "second_pad",
            "regex": "[0-6][0-9]",
            "fmt": lambda x: partial(x.strftime, "%S"),
            "parse": lambda x: x,
            "level": 0,
        }
    ),
}


DATETIME_CONF = ConfigFormat(default_fmt="%Y-%m-%d %H:%M:%S")


class Datetime(Formatter, asset=DATETIME_ASSET, config=DATETIME_CONF, level=10):
    """Datetime Formatter object."""

    def __init__(
        self,
        year: int | None = None,
        month: int | None = None,
        week: int | None = None,
        weeks: str | None = None,
        day: int | None = None,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        locale: str | None = None,
    ) -> None:
        self.year = int(year or 1990)
        self.month = int(month or 1)
        self.week = week
        self.weeks = weeks
        self.day = int(day or 1)
        self.hour: int = int(hour)
        self.minute: int = int(minute)
        self.second: int = int(second)
        self.microsecond: int = int(microsecond)
        self.locale = locale
        self.datetime: datetime = datetime(
            year=self.year,
            month=self.month,
            day=self.day,
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=self.microsecond,
        )

    @property
    def string(self) -> str:
        return str(self.datetime)

    @property
    def value(self) -> datetime:
        return self.datetime

    @staticmethod
    def prepare_value(value: str | datetime | date | None) -> datetime:
        """Prepare value before passing to convert logic in the formatter
        method that define by property of this formatter object. Return
        ``datetime.now()`` if an input value does not pass.

        :param value: A value that want to prepare before passing to this
            datetime formatter.
        :type value: str | datetime | date | None

        :raises FormatterValueError: If an input value does be
            ``datetime.datetime`` or ``datetime.date``.

        :rtype: datetime
        :returns: A prepared datetime value.
        """

        if value is None:
            return datetime.now()
        if not isinstance(
            value,
            (
                str,
                datetime,
                date,
            ),
        ):
            raise FormatterValueError(
                f"Datetime formatter does not support for value, {value!r}."
            )
        elif isinstance(value, str):
            return datetime.fromisoformat(value)
        return (
            value
            if isinstance(value, datetime)
            else datetime(value.year, value.month, value.day)
        )


__all__ = (
    "Formatter",
    "Serial",
    "SERIAL_ASSET",
    "SERIAL_CONF",
    "DATETIME_ASSET",
    "DATETIME_CONF",
    "Datetime",
)


def demo_number_formating() -> None:
    print(Serial.gen_format("This is a number `%n` but extra `%b`"))
    serial_instance = Serial.parse("Number: 20240101", fmt="Number: %n")
    assert 20240101 == serial_instance.value
    assert isinstance(serial_instance.value, int)

    print(serial_instance.format("%b"))
    assert "1001101001101011011100101" == serial_instance.format("%b")

    print(serial_instance.values())


def demo_datetime_formating() -> None:
    print(Datetime.gen_format("This is a datetime %Y%m and special %n"))
    dt_instance = Datetime.parse("date: 20240101", fmt="date: %Y%m%d")
    assert datetime(2024, 1, 1) == dt_instance.value
    assert isinstance(dt_instance.value, datetime)

    print(dt_instance.format("%n"))
    assert "2024" == dt_instance.format("%Y")


if __name__ == "__main__":
    demo_number_formating()
    print("-" * 140)
    demo_datetime_formating()
    # import inspect
    # func = lambda x, conf: x + conf
    # print(inspect.signature(func))
