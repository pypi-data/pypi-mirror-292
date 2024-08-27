from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.seq import map
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import to_enumerable
from ...fable_modules.thoth_json_core.decode import (object, IRequiredGetter, IGetters)
from ...fable_modules.thoth_json_core.encode import seq
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...Core.data_context import DataContext
from ...Core.data_map import (DataMap__get_DataContexts, DataMap, DataMap__ctor_4E3220A7)
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Table.composite_cell import CompositeCell
from ..decode import Decode_resizeArray
from .data_context import (encoder as encoder_1, decoder as decoder_1)

def encoder(dm: DataMap) -> Json:
    def mapping(dc: DataContext, dm: Any=dm) -> Json:
        return encoder_1(dc)

    return Json(5, to_enumerable([("dataContexts", seq(map(mapping, DataMap__get_DataContexts(dm))))]))


def _arrow1864(get: IGetters) -> DataMap:
    def _arrow1863(__unit: None=None) -> Array[DataContext]:
        arg_1: Decoder_1[Array[DataContext]] = Decode_resizeArray(decoder_1)
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("dataContexts", arg_1)

    return DataMap__ctor_4E3220A7(_arrow1863())


decoder: Decoder_1[DataMap] = object(_arrow1864)

def encoder_compressed(string_table: Any, oa_table: Any, cell_table: Any, dm: DataMap) -> Json:
    return encoder(dm)


def decoder_compressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[DataMap]:
    return decoder


__all__ = ["encoder", "decoder", "encoder_compressed", "decoder_compressed"]

