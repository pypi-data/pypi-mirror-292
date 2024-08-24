import datetime
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Self

import yaml
from bs4 import Tag
from prelawsql import (
    BaseTreePath,
    Rule,
    StatuteTitle,
    StatuteTitleCategory,
    add_idx,
    check_table,
    check_view,
    run_sql_file,
)
from rich.progress import Progress
from sqlite_utils.db import Database, Table, View

from .components import walk
from .fetcher import (
    extract_date_from_tag,
    extract_serial_title_from_tag,
    extract_statute_titles,
    extract_units_from_tag,
)
from .tree import TreeBase, TreeContent


@dataclass(frozen=True)
class Statute(TreeBase):
    """Algorithmic rendering of rules.

    ## Files

    Requires specifically formatted statute Path.

    Files would need to be downloaded from the [repo](https://github.com/justmars/corpus-statutes)
    and passed through [from_file][statute_utils.tree.TreeBase.from_file] to generate the instance.

    ## Tables

    The instance generates [@metadata][statute_utils.tree_statute.Statute.metadata] and [@content][statute_utils.tree_statute.Statute.content]
    to populate tables:

    1. `statutes`,
    2. `statute_units`, and
    3. `statute_titles` - each statute consists of various statute titles.
    4. `statute_references` - each statute may be mentioned in a future statute unit.
    """  # noqa: E501

    titles: list[StatuteTitle]
    variant: int

    @property
    def path(self) -> str:
        """Intended path to source file using computed values."""
        return "/".join(
            [
                self.rule.cat.value,
                self.rule.num,
                self.date.isoformat(),
                f"{str(self.variant)}.yml",
            ]
        )

    @classmethod
    def set_id(cls, rule: Rule, date: datetime.date, variant: str):
        return "-".join([rule.cat.value, rule.num, date.isoformat(), variant])

    ###
    ### REFERENCE ROWS
    ###

    @classmethod
    def set_reference_table_name(cls) -> str:
        return "statute_references"

    @classmethod
    def create_reference_table(cls, db: Database) -> Table:
        """Each statute can be mentioned in a future statute unit.

        By this relationship, we establish the following fields:

        1. `statute_id`: a foreign key to the `statutes` table
        2. `affector_key_statute_unit_id`: foreign key to the `statute_units` table
        """
        tbl_name = cls.set_reference_table_name()
        affected_fk = cls.set_common_root_pk()  # affected statute_id
        affector_key = "affector_statute_unit_id"
        tbl = db[tbl_name].create(  # type: ignore
            columns={"id": str, affected_fk: str, affector_key: str},
            pk="id",  # populated by hashing
            foreign_keys=[
                (affected_fk, cls.set_root_table_name(), "id"),
                (affector_key, cls.set_unit_table_name(), "id"),
            ],
            not_null={affected_fk, affector_key},
            if_not_exists=True,
        )

        for idx in (
            {affected_fk},
            {affector_key},
            {affected_fk, affector_key},
        ):
            add_idx(db[tbl_name], idx)

        return check_table(tbl)

    @classmethod
    def create_reference_view(cls, db: Database) -> View:
        """An interim view to be used as basis for populating the reference table proper."""  # noqa: E501
        _view = "view_" + cls.set_reference_table_name()
        db[_view].drop(ignore=True)
        run_sql_file(
            conn=db.conn,
            file=Path(__file__).parent / "sql" / (_view + ".sql"),
            prefix_expr=f"create view {_view} as",
        )
        return check_view(db[_view])

    @classmethod
    def unpack_view_row(cls, row: dict) -> Iterator[dict[str, Any]]:
        """Unpacks each row from [create_reference_view()][statute_utils.tree_statute.Statute.create_reference_view]

        Each row will contain an `id` which represents a `statutes` table primary key.

        Args:
            row (dict): Each row from `/sql/view_statute_references.sql` will
                contain a `unit_ids` key which is comma-separated. These refer to
                `statute_units` primary keys.

        Yields:
            Iterator[dict[str, Any]]: Records for insertion into the prospective reference table.
        """  # noqa: E501
        col_name = cls.set_common_root_pk()
        for statute_unit_pk in row["unit_ids"].split(","):
            yield {
                col_name: row["id"],
                "affector_statute_unit_id": statute_unit_pk,
            }

    @classmethod
    def add_reference_rows(cls, db: Database):
        """Create an interim view, parse view for raw records that will serve as the
        basis for creating the reference table records. See in relation to
        [create_reference_table()][statute_utils.tree_statute.Statute.create_reference_table]."""  # noqa: E501"""
        cls.create_reference_table(db).insert_all(
            records=(
                result
                for row in cls.create_reference_view(db).rows
                for result in Statute.unpack_view_row(row)
            ),
            hash_id="id",  # type: ignore
        )

    @classmethod
    def create_future_statute_units_view(cls, db: Database):
        """A more detailed view of the created reference table."""  # noqa: E501
        _view = "view_future_statute_units"
        db[_view].drop(ignore=True)
        # requires update sqlite version
        run_sql_file(
            conn=db.conn,
            file=Path(__file__).parent / "sql" / (_view + ".sql"),
            prefix_expr=f"create view {_view} as",
        )

    @classmethod
    def create_cite_statute_in_codifications(cls, db: Database):
        """A statute can be part of a codification, the metadata of
        such inclusions is prepared in advance as a view."""  # noqa: E501
        _view = "cite_statute_in_codifications"
        db[_view].drop(ignore=True)
        run_sql_file(
            conn=db.conn,
            file=Path(__file__).parent / "sql" / (_view + ".sql"),
            prefix_expr=f"create view {_view} as",
        )

    @classmethod
    def create_cite_statute_in_statute_units(cls, db: Database):
        """A statute can be referenced in the future by another statute,
        specifically through a statute unit. Such reference is prepared in
        advance as a view."""  # noqa: E501
        _view = "cite_statute_in_statute_units"
        db[_view].drop(ignore=True)
        run_sql_file(
            conn=db.conn,
            file=Path(__file__).parent / "sql" / (_view + ".sql"),
            prefix_expr=f"create view {_view} as",
        )

    @classmethod
    def create_cite_statute_in_unique_statutes(cls, db: Database):
        """A statute can be referenced in the future by another statute.
        Such reference is prepared in advance as a view."""  # noqa: E501
        _view = "cite_statute_in_unique_statutes"
        db[_view].drop(ignore=True)
        run_sql_file(
            conn=db.conn,
            file=Path(__file__).parent / "sql" / (_view + ".sql"),
            prefix_expr=f"create view {_view} as",
        )

    ###
    ### LOCAL TO DB
    ###

    @property
    def metadata(self) -> dict[str, Any]:
        """Root-based metadata."""
        return self.base | {"variant": self.variant}

    @property
    def content(self) -> TreeContent:
        """Unit-based column data."""
        rows = StatuteTitle.make_title_rows(self.id, titles=self.titles)
        texts = [row["text"] for row in rows]
        return self.set_content(extra_data={"content": ", ".join(texts)})

    def to_row(self, db: Database):
        row = self.metadata | self.content._asdict()
        fts = row.pop("fts")  # need to remove first
        self.add_root(db, record=row)
        self.add_units(db, records=fts)
        StatuteTitle.add_title_rows(
            db, title_variants=StatuteTitle.make_title_rows(self.id, titles=self.titles)
        )

    @classmethod
    def from_file(cls, file: Path) -> Self:
        treepath = BaseTreePath.unpack(file)
        data = BaseTreePath.load(file)
        rule = Rule(cat=treepath.category, num=treepath.num)
        date = treepath.date
        id = cls.set_id(rule=rule, date=date, variant=treepath.slug)
        return cls(
            id=id,
            rule=rule,
            variant=int(treepath.slug),
            date=treepath.date,
            size=file.stat().st_size,
            units=walk(data["units"]),
            titles=list(
                StatuteTitle.generate(
                    official=data["title"],
                    serial=treepath.serial_title,
                    short=data.get("short"),
                    aliases=data.get("aliases"),
                    searchables=treepath.searchable_serial_titles,
                )
            ),
        )

    @classmethod
    def create_root_table(cls, db: Database) -> Table:
        tbl_name = cls.set_root_table_name()

        db[tbl_name].create(  # type: ignore
            columns={
                "id": str,
                "cat": str,
                "num": str,
                "date": datetime.date,
                "variant": int,
                "units": str,
                "html": str,
                "size": int,
            },
            pk="id",
            not_null={
                "cat",
                "num",
                "date",
                "units",
                "size",
                "html",
            },
            defaults={"variant": 1},
            if_not_exists=True,
        )

        for idx in (
            {"size"},
            {"date"},
            {"cat", "num"},
            {"cat", "num", "date"},
            {"cat", "num", "date", "variant"},
        ):
            add_idx(db[tbl_name], idx)

        return check_table(db[tbl_name])

    @classmethod
    def source(cls, db_name: str, folder: str, pattern: str):
        # initialize related db-tables before adding files from folder
        db = Database(filename_or_conn=db_name, use_counts_table=True)
        _, units_tbl = cls.create_base_tables(db)
        titles_table = StatuteTitle.create_titles_table(
            db,
            fk=cls.set_common_root_pk(),
            fk_tbl=cls.set_root_table_name(),
        )
        cls.from_folder_to_db(
            db=db,
            folder=folder,
            pattern=pattern,
        )
        with Progress() as progress:
            task = progress.add_task("post-statute-processing", total=3)
            while not progress.finished:
                progress.console.print("Enabling fts")
                units_tbl.enable_fts(["snippetable"], replace=True)
                titles_table.enable_fts(["text"], replace=True)
                db.index_foreign_keys()
                progress.update(task, advance=1)

                progress.console.print("Adding related views")
                cls.add_reference_rows(db)
                cls.create_future_statute_units_view(db)
                cls.create_cite_statute_in_codifications(db)
                cls.create_cite_statute_in_statute_units(db)
                cls.create_cite_statute_in_unique_statutes(db)
                progress.update(task, advance=1)

                db.vacuum()
                progress.update(task, advance=1)

    ###
    ### WEB TO LOCAL
    ###

    def ensure_path(self, basepath: Path):
        if not basepath.exists():
            raise Exception("Ensure statute base path exists first.")

        f = basepath.joinpath(self.path)
        f.parent.mkdir(parents=True, exist_ok=True)
        return f

    def to_file(self, basepath: Path) -> Path:
        """Orders different key, value pairs for `yaml.dump()` .
        Ensures each node in the tree is properly (rather than alphabetically) ordered.
        """
        f = self.ensure_path(basepath)
        data: dict = asdict(self)
        data["units"] = walk(data["units"])
        text = yaml.dump(data, width=60)  # see representer added in walk
        f.write_text(text)
        return f

    def to_file_from_web(self, basepath: Path) -> Path:
        """Like `to_file()` but limits data passed."""
        f = self.ensure_path(basepath)
        title = next(
            title.text
            for title in self.titles
            if title.category == StatuteTitleCategory.Official
        )
        data = {"title": title, "units": walk(self.units)}
        text = yaml.dump(data, width=60)  # see representer added in walk
        f.write_text(text)
        return f

    @classmethod
    def from_web(cls, tag: Tag) -> Self:
        """See in relation to `Listing.fetch_tags()` where a user
        can select a given tag (raw data from tist of statutes) to
        convert into the structured object. After creation, can
        use `self.to_file_from_web(basepath: Path)` to place the file in the `basepath`
        directory."""
        from .extractor import extract_rule

        text = extract_serial_title_from_tag(tag)
        rule = extract_rule(text)
        if not rule:
            raise Exception(f"Missing rule from {text=}")
        date = extract_date_from_tag(tag)
        variant = "1"  # mocked value
        id = cls.set_id(rule=rule, date=date, variant=variant)
        return cls(
            id=id,
            titles=extract_statute_titles(tag),
            rule=rule,
            variant=int(variant),
            date=date,
            units=extract_units_from_tag(tag),
            size=1,  # mocked value
        )
