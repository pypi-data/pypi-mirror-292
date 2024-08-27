from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.protocol_parameter import ProtocolParameter
from ..encode import (try_include, default_spaces)
from ..idtable import encode
from ..ontology_annotation import (OntologyAnnotation_ROCrate_genID, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def ProtocolParameter_ISAJson_genID(p: ProtocolParameter) -> str:
    match_value: OntologyAnnotation | None = p.ParameterName
    if match_value is None:
        return "#EmptyProtocolParameter"

    else: 
        return ("#ProtocolParameter/" + OntologyAnnotation_ROCrate_genID(match_value)) + ""



def ProtocolParameter_ISAJson_encoder(id_map: Any | None, value: ProtocolParameter) -> Json:
    def f(value_1: ProtocolParameter, id_map: Any=id_map, value: Any=value) -> Json:
        def chooser(tupled_arg: tuple[str, Json], value_1: Any=value_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1551(value_2: str, value_1: Any=value_1) -> Json:
            return Json(0, value_2)

        def _arrow1552(oa: OntologyAnnotation, value_1: Any=value_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1551, ProtocolParameter_ISAJson_genID(value_1)), try_include("parameterName", _arrow1552, value_1.ParameterName)])))

    if id_map is not None:
        def _arrow1553(p_1: ProtocolParameter, id_map: Any=id_map, value: Any=value) -> str:
            return ProtocolParameter_ISAJson_genID(p_1)

        return encode(_arrow1553, f, value, id_map)

    else: 
        return f(value)



def _arrow1555(get: IGetters) -> ProtocolParameter:
    def _arrow1554(__unit: None=None) -> OntologyAnnotation | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("parameterName", OntologyAnnotation_ISAJson_decoder)

    return ProtocolParameter(None, _arrow1554())


ProtocolParameter_ISAJson_decoder: Decoder_1[ProtocolParameter] = object(_arrow1555)

def ARCtrl_Process_ProtocolParameter__ProtocolParameter_fromISAJsonString_Static_Z721C83C5(s: str) -> ProtocolParameter:
    match_value: FSharpResult_2[ProtocolParameter, str] = Decode_fromString(ProtocolParameter_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ProtocolParameter], str]:
    def _arrow1556(v: ProtocolParameter, spaces: Any=spaces) -> str:
        value: Json = ProtocolParameter_ISAJson_encoder(None, v)
        return to_string(default_spaces(spaces), value)

    return _arrow1556


def ARCtrl_Process_ProtocolParameter__ProtocolParameter_ToISAJsonString_71136F3F(this: ProtocolParameter, spaces: int | None=None) -> str:
    return ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F(spaces)(this)


__all__ = ["ProtocolParameter_ISAJson_genID", "ProtocolParameter_ISAJson_encoder", "ProtocolParameter_ISAJson_decoder", "ARCtrl_Process_ProtocolParameter__ProtocolParameter_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_ProtocolParameter__ProtocolParameter_toISAJsonString_Static_71136F3F", "ARCtrl_Process_ProtocolParameter__ProtocolParameter_ToISAJsonString_71136F3F"]

