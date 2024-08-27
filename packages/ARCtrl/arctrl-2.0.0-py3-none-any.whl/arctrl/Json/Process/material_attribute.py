from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.material_attribute import MaterialAttribute
from ..encode import (try_include, default_spaces)
from ..idtable import encode
from ..ontology_annotation import (OntologyAnnotation_ROCrate_genID, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def MaterialAttribute_ISAJson_genID(m: MaterialAttribute) -> str:
    match_value: OntologyAnnotation | None = m.CharacteristicType
    if match_value is None:
        return "#EmptyFactor"

    else: 
        return ("#MaterialAttribute/" + OntologyAnnotation_ROCrate_genID(match_value)) + ""



def MaterialAttribute_ISAJson_encoder(id_map: Any | None, value: MaterialAttribute) -> Json:
    def f(value_1: MaterialAttribute, id_map: Any=id_map, value: Any=value) -> Json:
        def chooser(tupled_arg: tuple[str, Json], value_1: Any=value_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1560(value_2: str, value_1: Any=value_1) -> Json:
            return Json(0, value_2)

        def _arrow1561(oa: OntologyAnnotation, value_1: Any=value_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1560, MaterialAttribute_ISAJson_genID(value_1)), try_include("characteristicType", _arrow1561, value_1.CharacteristicType)])))

    if id_map is not None:
        def _arrow1562(m_1: MaterialAttribute, id_map: Any=id_map, value: Any=value) -> str:
            return MaterialAttribute_ISAJson_genID(m_1)

        return encode(_arrow1562, f, value, id_map)

    else: 
        return f(value)



def _arrow1564(get: IGetters) -> MaterialAttribute:
    def _arrow1563(__unit: None=None) -> OntologyAnnotation | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("characteristicType", OntologyAnnotation_ISAJson_decoder)

    return MaterialAttribute(None, _arrow1563())


MaterialAttribute_ISAJson_decoder: Decoder_1[MaterialAttribute] = object(_arrow1564)

def ARCtrl_Process_MaterialAttribute__MaterialAttribute_fromISAJsonString_Static_Z721C83C5(s: str) -> MaterialAttribute:
    match_value: FSharpResult_2[MaterialAttribute, str] = Decode_fromString(MaterialAttribute_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_MaterialAttribute__MaterialAttribute_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[MaterialAttribute], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1565(v: MaterialAttribute, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: Json = MaterialAttribute_ISAJson_encoder(id_map, v)
        return to_string(default_spaces(spaces), value)

    return _arrow1565


def ARCtrl_Process_MaterialAttribute__MaterialAttribute_ToJsonString_Z3B036AA(this: MaterialAttribute, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_Process_MaterialAttribute__MaterialAttribute_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


__all__ = ["MaterialAttribute_ISAJson_genID", "MaterialAttribute_ISAJson_encoder", "MaterialAttribute_ISAJson_decoder", "ARCtrl_Process_MaterialAttribute__MaterialAttribute_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_MaterialAttribute__MaterialAttribute_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_MaterialAttribute__MaterialAttribute_ToJsonString_Z3B036AA"]

