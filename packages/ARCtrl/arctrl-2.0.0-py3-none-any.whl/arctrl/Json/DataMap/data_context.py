from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IRequiredGetter, IOptionalGetter, string, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...Core.data import Data
from ...Core.data_context import (DataContext__get_Explication, DataContext__get_Unit, DataContext__get_ObjectType, DataContext__get_Description, DataContext__get_GeneratedBy, DataContext__get_Label, DataContext, DataContext__ctor_Z780A8A2A)
from ...Core.ontology_annotation import OntologyAnnotation
from ..data import (Data_encoder, Data_decoder)
from ..encode import try_include
from ..ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder)

def encoder(dc: DataContext) -> Json:
    def chooser(tupled_arg: tuple[str, Json], dc: Any=dc) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1850(oa: OntologyAnnotation, dc: Any=dc) -> Json:
        return OntologyAnnotation_encoder(oa)

    def _arrow1851(oa_1: OntologyAnnotation, dc: Any=dc) -> Json:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1852(oa_2: OntologyAnnotation, dc: Any=dc) -> Json:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow1853(value: str, dc: Any=dc) -> Json:
        return Json(0, value)

    def _arrow1854(value_2: str, dc: Any=dc) -> Json:
        return Json(0, value_2)

    def _arrow1855(value_4: str, dc: Any=dc) -> Json:
        return Json(0, value_4)

    return Json(5, choose(chooser, of_array([("data", Data_encoder(dc)), try_include("explication", _arrow1850, DataContext__get_Explication(dc)), try_include("unit", _arrow1851, DataContext__get_Unit(dc)), try_include("objectType", _arrow1852, DataContext__get_ObjectType(dc)), try_include("description", _arrow1853, DataContext__get_Description(dc)), try_include("generatedBy", _arrow1854, DataContext__get_GeneratedBy(dc)), try_include("label", _arrow1855, DataContext__get_Label(dc))])))


def _arrow1862(get: IGetters) -> DataContext:
    data: Data
    object_arg: IRequiredGetter = get.Required
    data = object_arg.Field("data", Data_decoder)
    def _arrow1856(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("explication", OntologyAnnotation_decoder)

    def _arrow1857(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("unit", OntologyAnnotation_decoder)

    def _arrow1858(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("objectType", OntologyAnnotation_decoder)

    def _arrow1859(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("label", string)

    def _arrow1860(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("description", string)

    def _arrow1861(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("generatedBy", string)

    return DataContext__ctor_Z780A8A2A(data.ID, data.Name, data.DataType, data.Format, data.SelectorFormat, _arrow1856(), _arrow1857(), _arrow1858(), _arrow1859(), _arrow1860(), _arrow1861(), data.Comments)


decoder: Decoder_1[DataContext] = object(_arrow1862)

__all__ = ["encoder", "decoder"]

