from datetime import datetime
from typing import TYPE_CHECKING, Any

import sqlalchemy.dialects.postgresql as postgresql
import sqlalchemy.types as sa_types
from sqlalchemy import Column, Select, and_, cast

from .model import Model
from .utils import is_sqla_type

if TYPE_CHECKING:
    from .api.interface import SQLAInterface
    from .db import QueryManager

__all__ = [
    "BaseFilter",
    "FilterEqual",
    "FilterNotEqual",
    "FilterStartsWith",
    "FilterNotStartsWith",
    "FilterEndsWith",
    "FilterNotEndsWith",
    "FilterContains",
    "FilterNotContains",
    "FilterGreater",
    "FilterSmaller",
    "FilterGreaterEqual",
    "FilterSmallerEqual",
    "FilterIn",
    "FilterRelationOneToOneOrManyToOneEqual",
    "FilterRelationOneToOneOrManyToOneNotEqual",
    "FilterRelationOneToManyOrManyToManyIn",
    "FilterRelationOneToManyOrManyToManyNotIn",
    "SQLAFilterConverter",
]


class BaseFilter:
    name: str
    arg_name: str
    datamodel: "SQLAInterface" = None
    query: "QueryManager" = None
    """
    A reference to the QueryManager instance that is using this filter.
    """
    is_heavy = False
    """
    If set to true, will run the filter in a separate thread. Useful for heavy filters that take a long time to execute. Default is False.

    Only works when apply function is not a coroutine.
    """

    def __init__(self, datamodel: "SQLAInterface"):
        self.datamodel = datamodel

    def _get_column(self, col_name: str) -> Column:
        return getattr(self.datamodel.obj, col_name)

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        """
        Apply the filter to the given SQLAlchemy Select statement.

        Args:
            stmt (Select): The SQLAlchemy Select statement to apply the filter to.
            col (str): The column name to filter by.
            value (Any): The value to filter by.

        Returns:
            Select: The SQLAlchemy Select statement with the filter applied.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError()


class FilterEqual(BaseFilter):
    name = "Equal to"
    arg_name = "eq"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if value == "NULL":
            value = None
        elif is_sqla_type(getattr(col, "type", None), sa_types.Date):
            value = datetime.fromisoformat(value).date()
        elif is_sqla_type(getattr(col, "type", None), sa_types.DateTime):
            value = datetime.fromisoformat(value).replace(tzinfo=None)
        elif is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(col == value)


class FilterNotEqual(BaseFilter):
    name = "Not Equal to"
    arg_name = "neq"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if value == "NULL":
            value = None
        elif is_sqla_type(getattr(col, "type", None), sa_types.Date):
            value = datetime.fromisoformat(value).date()
        elif is_sqla_type(getattr(col, "type", None), sa_types.DateTime):
            value = datetime.fromisoformat(value).replace(tzinfo=None)
        elif is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(col != value)


class FilterStartsWith(BaseFilter):
    name = "Starts with"
    arg_name = "sw"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(col.ilike(value + "%"))


class FilterNotStartsWith(BaseFilter):
    name = "Not Starts with"
    arg_name = "nsw"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(~col.ilike(value + "%"))


class FilterEndsWith(BaseFilter):
    name = "Ends with"
    arg_name = "ew"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(col.ilike("%" + value))


class FilterNotEndsWith(BaseFilter):
    name = "Not Ends with"
    arg_name = "new"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(~col.ilike("%" + value))


class FilterContains(BaseFilter):
    name = "Contains"
    arg_name = "ct"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(col.ilike("%" + value + "%"))


class FilterNotContains(BaseFilter):
    name = "Not Contains"
    arg_name = "nct"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(~col.ilike("%" + value + "%"))


class FilterGreater(BaseFilter):
    name = "Greater than"
    arg_name = "gt"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), sa_types.Date):
            value = datetime.fromisoformat(value).date()
        elif is_sqla_type(getattr(col, "type", None), sa_types.DateTime):
            value = datetime.fromisoformat(value).replace(tzinfo=None)
        return stmt.filter(col > value)


class FilterSmaller(BaseFilter):
    name = "Smaller than"
    arg_name = "lt"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), sa_types.Date):
            value = datetime.fromisoformat(value).date()
        elif is_sqla_type(getattr(col, "type", None), sa_types.DateTime):
            value = datetime.fromisoformat(value).replace(tzinfo=None)
        return stmt.filter(col < value)


class FilterGreaterEqual(BaseFilter):
    name = "Greater equal"
    arg_name = "ge"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), sa_types.Date):
            value = datetime.fromisoformat(value).date()
        elif is_sqla_type(getattr(col, "type", None), sa_types.DateTime):
            value = datetime.fromisoformat(value).replace(tzinfo=None)
        return stmt.filter(col >= value)


class FilterSmallerEqual(BaseFilter):
    name = "Smaller equal"
    arg_name = "le"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), sa_types.Date):
            value = datetime.fromisoformat(value).date()
        elif is_sqla_type(getattr(col, "type", None), sa_types.DateTime):
            value = datetime.fromisoformat(value).replace(tzinfo=None)
        return stmt.filter(col <= value)


class FilterIn(BaseFilter):
    name = "One of"
    arg_name = "in"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        col = self._get_column(col)
        if is_sqla_type(getattr(col, "type", None), sa_types.Date):
            value = datetime.fromisoformat(value).date()
        elif is_sqla_type(getattr(col, "type", None), sa_types.DateTime):
            value = datetime.fromisoformat(value).replace(tzinfo=None)
        elif is_sqla_type(getattr(col, "type", None), postgresql.JSONB):
            col = cast(col, sa_types.String)
        return stmt.filter(col.in_(value))


class BaseFilterRelationOneToOneOrManyToOne(BaseFilter):
    def _get_rel_value(self, col: str, value: Any):
        if isinstance(value, Model):
            return value
        rel_interface = self.datamodel.get_related_interface(col)
        rel_obj = rel_interface.obj
        pk_attrs = rel_interface.get_pk_attrs()
        if not isinstance(value, dict):
            value = {pk_attrs[0]: value}
        statements = [
            getattr(rel_obj, pk_attr) == val for pk_attr, val in value.items()
        ]
        return and_(*statements)


class FilterRelationOneToOneOrManyToOneEqual(
    BaseFilterRelationOneToOneOrManyToOne, FilterEqual
):
    arg_name = "rel_o_m"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        if not value:
            return stmt

        rel_val = self._get_rel_value(col, value)
        if isinstance(rel_val, Model):
            return super().apply(stmt, col, rel_val)
        col = self._get_column(col)
        return stmt.filter(col.has(rel_val))


class FilterRelationOneToOneOrManyToOneNotEqual(
    BaseFilterRelationOneToOneOrManyToOne, FilterNotEqual
):
    arg_name = "nrel_o_m"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        if not value:
            return stmt

        rel_val = self._get_rel_value(col, value)
        if isinstance(rel_val, Model):
            return super().apply(stmt, col, rel_val)
        col = self._get_column(col)
        return stmt.filter(~col.has(rel_val))


class BaseFilterRelationOneToManyOrManyToMany(BaseFilter):
    def _get_rel_value(self, col: str, value: Any):
        if not isinstance(value, list):
            return BaseFilterRelationOneToOneOrManyToOne._get_rel_value(
                self, col, value
            )
        if all(isinstance(val, Model) for val in value):
            return value

        rel_interface = self.datamodel.get_related_interface(col)
        rel_obj = rel_interface.obj
        pk_attrs = rel_interface.get_pk_attrs()
        statements = []
        pks = {}
        for val in value:
            if not isinstance(val, dict):
                val = {pk_attrs[0]: val}
            for pk_attr, val in val.items():
                if pk_attr not in pks:
                    pks[pk_attr] = []
                pks[pk_attr].append(val)

        for pk_attr, vals in pks.items():
            statements.append(getattr(rel_obj, pk_attr).in_(vals))
        return and_(*statements)


class FilterRelationOneToManyOrManyToManyIn(BaseFilterRelationOneToManyOrManyToMany):
    name = "In"
    arg_name = "rel_m_m"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        if not value:
            return stmt

        rel_val = self._get_rel_value(col, value)
        col = self._get_column(col)
        if isinstance(rel_val, list) or isinstance(rel_val, Model):
            if not isinstance(rel_val, list):
                rel_val = [rel_val]
            for val in rel_val:
                stmt = stmt.filter(col.contains(val))
            return stmt
        return stmt.filter(col.any(rel_val))


class FilterRelationOneToManyOrManyToManyNotIn(BaseFilterRelationOneToManyOrManyToMany):
    name = "Not In"
    arg_name = "nrel_m_m"

    def apply(self, stmt: Select, col: str, value: Any) -> Select:
        if not value:
            return stmt

        rel_val = self._get_rel_value(col, value)
        col = self._get_column(col)
        if isinstance(rel_val, list) or isinstance(rel_val, Model):
            if not isinstance(rel_val, list):
                rel_val = [rel_val]
            for val in rel_val:
                stmt = stmt.filter(col.contains(val))
            return stmt
        return stmt.filter(~col.any(rel_val))


class SQLAFilterConverter:
    """
    Helper class to get available filters for a column type.
    """

    conversion_table = (
        (
            "is_relation_one_to_one",
            [
                FilterRelationOneToOneOrManyToOneEqual,
                FilterRelationOneToOneOrManyToOneNotEqual,
            ],
        ),
        (
            "is_relation_many_to_one",
            [
                FilterRelationOneToOneOrManyToOneEqual,
                FilterRelationOneToOneOrManyToOneNotEqual,
            ],
        ),
        (
            "is_relation_one_to_many",
            [
                FilterRelationOneToManyOrManyToManyIn,
                FilterRelationOneToManyOrManyToManyNotIn,
            ],
        ),
        (
            "is_relation_many_to_many",
            [
                FilterRelationOneToManyOrManyToManyIn,
                FilterRelationOneToManyOrManyToManyNotIn,
            ],
        ),
        ("is_enum", [FilterEqual, FilterNotEqual, FilterIn]),
        ("is_boolean", [FilterEqual, FilterNotEqual]),
        (
            "is_text",
            [
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_binary",
            [
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_string",
            [
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_json",
            [
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_integer",
            [
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_float",
            [
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_numeric",
            [
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_date",
            [
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_datetime",
            [
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
    )
