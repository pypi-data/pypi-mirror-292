import re
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

__all__ = ["Model", "metadata", "metadatas", "Base"]

camelcase_re = re.compile(r"([A-Z]+)(?=[a-z0-9])")


def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ("_%s_%s" % (word[:-1], word[-1])).lower()

        return "_" + word.lower()

    return camelcase_re.sub(_join, name).lstrip("_")


metadatas: dict[str, MetaData] = {
    "default": MetaData(),
}


class Model(DeclarativeBase):
    """
    Use this class has the base for your models,
    it will define your table names automatically
    MyModel will be called my_model on the database.

    ::

        from sqlalchemy import Integer, String
        from fastapi-rtk import Model

        class MyModel(Model):
            id = Column(Integer, primary_key=True)
            name = Column(String(50), unique = True, nullable=False)

    """

    __bind_key__: str | None = None
    """
    The bind key to use for this model. This allow you to use multiple databases. None means the default database. Default is None.
    """

    metadata = metadatas["default"]

    def __init_subclass__(cls, **kw: Any) -> None:
        # Overwrite the metadata if the bind key is set
        if cls.__bind_key__:
            if cls.__bind_key__ not in metadatas:
                metadatas[cls.__bind_key__] = MetaData()
            cls.metadata = metadatas[cls.__bind_key__]
        return super().__init_subclass__(**kw)

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Returns the table name for the given class.

        The table name is derived from the class name by converting
        any uppercase letters to lowercase and inserting an underscore
        before each uppercase letter.

        Returns:
            str: The table name.
        """
        return camel_to_snake_case(cls.__name__)

    __table_args__ = {"extend_existing": True}

    def update(self, data: dict[str, any]):
        """
        Updates the model instance with the given data.

        Args:
            data (dict): The data to update the model instance with.

        Returns:
            None
        """
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def name_(self):
        """
        Returns the string representation of the object.
        """
        return str(self)


metadata = metadatas["default"]


"""
    This is for retro compatibility
"""
Base = Model
