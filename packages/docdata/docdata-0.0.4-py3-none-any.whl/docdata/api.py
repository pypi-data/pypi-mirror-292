"""Utilities for documentation."""

import textwrap
from functools import partial
from typing import Any, Callable, Optional, TypeVar, Union, cast, overload

import yaml

__all__ = [
    "get_docdata",
    "parse_docdata",
]

X = TypeVar("X")

DOCDATA_DUNDER = "__docdata__"


def get_docdata(obj: X) -> Any:
    """Get the docdata if it is available."""
    return getattr(obj, DOCDATA_DUNDER, None)


# docstr-coverage:inherited
@overload
def parse_docdata(
    obj: None,
    *,
    delimiter: str,
    formatter: Optional[Callable[[Any], str]] = None,
) -> Callable[[X], X]: ...


# docstr-coverage:inherited
@overload
def parse_docdata(
    obj: X,
    *,
    delimiter: str,
    formatter: Optional[Callable[[Any], str]] = None,
) -> X: ...


def parse_docdata(
    obj: Optional[X] = None,
    *,
    delimiter: str = "---",
    formatter: Optional[Callable[[Any], str]] = None,
) -> Union[X, Callable[[X], X]]:
    """Parse the structured data from the end of the docstr and store it in ``__docdata__``.

    The data after the delimiter should be in the YAML form.
    It is parsed with :func:`yaml.safe_load` then stored in the ``__docdata__`` field of the
    object.

    :param obj: Any object that can has a ``__doc__`` field.
    :param delimiter: The delimiter between the actual docstring and structured YAML.
    :param formatter: A function that takes the parsed docdata and turns it into more documentation
    :return: The same object with a modified docstr.

    :raises AttributeError: if the object has no ``__doc__`` field.
    """
    if obj is None:
        return cast(
            Callable[[X], X],
            partial(
                parse_docdata,
                delimiter=delimiter,
                formatter=formatter,
            ),
        )

    try:
        docstr = obj.__doc__
    except AttributeError:
        raise AttributeError(f"no __doc__ available in {obj}") from None
    if docstr is None:  # no docstr to modify
        return obj

    lines = docstr.splitlines()
    try:
        index = min(i for i, line in enumerate(lines) if line.strip() == delimiter)
    except ValueError:
        return obj

    # The docstr is all the lines before the line with the delimiter. No
    # modification to the text wrapping is necessary.
    obj.__doc__ = "\n".join(_strip_trailing_lines(lines[:index]))

    # The YAML structured data is on all lines following the line with the delimiter.
    # The text must be dedented before YAML parsing.
    yaml_str = textwrap.dedent("\n".join(lines[index + 1 :]))
    yaml_data = yaml.safe_load(yaml_str)
    setattr(obj, DOCDATA_DUNDER, yaml_data)

    # Automagically write more docs based on the yaml data
    if formatter is not None:
        obj.__doc__ += formatter(yaml_data)

    return obj


def _strip_trailing_lines(lines: list[str]) -> list[str]:
    """Strip trailing lines."""
    found = False
    rv = []
    for line in reversed(lines):
        if found:
            rv.append(line)
        elif not line:
            continue
        else:
            found = True
            rv.append(line)
    return list(reversed(rv))
