from typing import Callable

from ..api import ModelRestApi
from ..dependencies import get_query_manager
from .db import GenericQueryManager
from .interface import GenericInterface

__all__ = ["GenericApi"]


class GenericApi(ModelRestApi):
    datamodel: GenericInterface

    def get_query_manager(self) -> Callable[..., GenericQueryManager]:
        return get_query_manager(self.datamodel, True)
