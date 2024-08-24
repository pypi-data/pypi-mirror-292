import re
from collections.abc import Iterator
from re import Pattern
from typing import NamedTuple

from prelawsql import Rule, StatuteSerialCategory

from .components import make_regex_readable


class NamedPattern(NamedTuple):
    name: str
    regex_base: str
    rule: Rule
    matches: list[str] | None = None
    excludes: list[str] | None = None
    options: list[Rule] | None = None

    @property
    def regex(self) -> str:
        return make_regex_readable(rf"(?P<{self.group_name}>{self.regex_base})")

    @property
    def pattern(self) -> Pattern:
        return re.compile(self.regex, re.X)

    @property
    def group_name(self) -> str:
        return self.rule.slug


class SerialPattern(NamedTuple):
    """The word _serial_ is employed because the documents representing rules are numbered consecutively.

    Each serial pattern refers to a statute category, e.g. `RA`, `CA`, etc. matched with an identifier, e.g. 386.

    Field | Description | Example
    --:|:--|:--
    `cat` | [`Statute Category`][statute-category-model] | StatuteSerialCategory.RepublicAct
    `regex_bases` | How do we pattern the category name? | ["r.a. no.", "Rep. Act. No."]
    `regex_serials` | What digits are allowed | ["386", "11114"]
    `matches` | Usable in parametized tests to determine whether the pattern declared matches the samples | ["Republic Act No. 7160", "R.A. 386 and 7160" ]
    `excludes` | Usable in parametized tests to determine that the full pattern will not match | ["Republic Act No. 7160:", "RA 9337-"]
    """  # noqa: E501

    cat: StatuteSerialCategory
    regex_bases: list[str]
    regex_serials: list[str]
    matches: list[str] | None = None
    excludes: list[str] | None = None

    @property
    def lines(self) -> Iterator[str]:
        """Each regex string produced matches the serial rule. Note the line break
        needs to be retained so that when printing `@regex`, the result is organized.
        """
        for base in self.regex_bases:
            for idx in self.regex_serials:
                yield rf"""({base}\s*{idx})
                """

    @property
    def group_name(self) -> str:
        return rf"serial_{self.cat.value}"

    @property
    def regex(self) -> str:
        return rf"(?P<{self.group_name}>{r'|'.join(self.lines)})"

    @property
    def pattern(self) -> Pattern:
        return re.compile(self.regex, re.X)

    @property
    def digits_in_match(self) -> Pattern:
        return re.compile(r"|".join(self.regex_serials))
