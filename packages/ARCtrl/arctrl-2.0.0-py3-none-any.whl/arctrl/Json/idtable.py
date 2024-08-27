from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_modules.fable_library.map_util import add_to_dict
from ..fable_modules.fable_library.util import to_enumerable
from ..fable_modules.thoth_json_core.types import Json

_VALUE = TypeVar("_VALUE")

def encode_id(id: str) -> Json:
    return Json(5, to_enumerable([("@id", Json(0, id))]))


def encode(gen_id: Callable[[_VALUE], str], encoder: Callable[[_VALUE], Json], value: _VALUE, table: Any) -> Json:
    id: str = gen_id(value)
    if id in table:
        return encode_id(id)

    else: 
        v: Json = encoder(value)
        add_to_dict(table, gen_id(value), v)
        return v



__all__ = ["encode_id", "encode"]

