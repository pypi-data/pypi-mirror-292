import datetime

from bs4 import Tag
from dateutil.parser import parse
from markdownify import markdownify
from prelawsql import StatuteTitle, StatuteTitleCategory, url_to_soup

from .components import list_sections


def extract_link_from_tag(tag: Tag) -> str:
    return tag("a")[0]["href"].replace("showdocs", "showdocsfriendly")


def extract_serial_title_from_tag(tag: Tag) -> str:
    return tag("strong")[0].text.strip().title()


def extract_official_title_from_tag(tag: Tag) -> str:
    return tag("small")[0].text.strip().title()


def extract_date_from_tag(tag: Tag) -> datetime.date:
    dt = tag("a")[0].find_all(string=True, recursive=False)[-1].strip()
    return parse(dt).date()


def extract_statute_titles(tag: Tag) -> list[StatuteTitle]:
    return [
        StatuteTitle(
            category=StatuteTitleCategory.Serial,
            text=extract_serial_title_from_tag(tag),
        ),
        StatuteTitle(
            category=StatuteTitleCategory.Official,
            text=extract_official_title_from_tag(tag),
        ),
    ]


def clean_units(units: list[dict]) -> list[dict]:
    for unit in units:
        unit.pop("order")
        raw = unit.pop("content")
        unit["content"] = markdownify(html=raw)
    return units


def remove_extraneous_text(units: list[dict]) -> list[dict]:
    last_unit = units[-1]["content"]
    marker = "Approved,\n"
    if marker in last_unit:
        idx = last_unit.index("Approved,\n")
        units[-1]["content"] = units[-1]["content"][:idx]
        print("Removing extra area")
    return units


def extract_units_from_tag(tag: Tag) -> list[dict]:
    link = extract_link_from_tag(tag)
    soup = url_to_soup(link)
    if not soup:
        raise Exception(f"Missing soup from {tag=}")
    units = list_sections(raw=str(soup))
    units = clean_units(units)
    units = remove_extraneous_text(units)
    return units
