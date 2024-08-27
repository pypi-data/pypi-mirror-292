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
from ...Core.Process.process_parameter_value import ProcessParameterValue
from ...Core.Process.protocol_parameter import ProtocolParameter
from ...Core.value import Value
from ..encode import (try_include, default_spaces)
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from ..property_value import (encoder, decoder as decoder_1)
from .protocol_parameter import (ProtocolParameter_ISAJson_encoder, ProtocolParameter_ISAJson_decoder)
from .value import (Value_ISAJson_encoder, Value_ISAJson_decoder)

ProcessParameterValue_ROCrate_encoder: Callable[[ProcessParameterValue], Json] = encoder

def _arrow1668(alternate_name: str | None=None, measurement_method: str | None=None, description: str | None=None, category: OntologyAnnotation | None=None, value: Value | None=None, unit: OntologyAnnotation | None=None) -> ProcessParameterValue:
    return ProcessParameterValue.create_as_pv(alternate_name, measurement_method, description, category, value, unit)


ProcessParameterValue_ROCrate_decoder: Decoder_1[ProcessParameterValue] = decoder_1(_arrow1668)

def ProcessParameterValue_ISAJson_genID(oa: ProcessParameterValue) -> Any:
    raise Exception("Not implemented")


def ProcessParameterValue_ISAJson_encoder(id_map: Any | None, oa: ProcessParameterValue) -> Json:
    def chooser(tupled_arg: tuple[str, Json], id_map: Any=id_map, oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1670(value: ProtocolParameter, id_map: Any=id_map, oa: Any=oa) -> Json:
        return ProtocolParameter_ISAJson_encoder(id_map, value)

    def _arrow1671(value_1: Value, id_map: Any=id_map, oa: Any=oa) -> Json:
        return Value_ISAJson_encoder(id_map, value_1)

    def _arrow1672(oa_1: OntologyAnnotation, id_map: Any=id_map, oa: Any=oa) -> Json:
        return OntologyAnnotation_ISAJson_encoder(id_map, oa_1)

    return Json(5, choose(chooser, of_array([try_include("category", _arrow1670, oa.Category), try_include("value", _arrow1671, oa.Value), try_include("unit", _arrow1672, oa.Unit)])))


def _arrow1676(get: IGetters) -> ProcessParameterValue:
    def _arrow1673(__unit: None=None) -> ProtocolParameter | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("category", ProtocolParameter_ISAJson_decoder)

    def _arrow1674(__unit: None=None) -> Value | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("value", Value_ISAJson_decoder)

    def _arrow1675(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("unit", OntologyAnnotation_ISAJson_decoder)

    return ProcessParameterValue(_arrow1673(), _arrow1674(), _arrow1675())


ProcessParameterValue_ISAJson_decoder: Decoder_1[ProcessParameterValue] = object(_arrow1676)

def ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_fromISAJsonString_Static_Z721C83C5(s: str) -> ProcessParameterValue:
    match_value: FSharpResult_2[ProcessParameterValue, str] = Decode_fromString(ProcessParameterValue_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[ProcessParameterValue], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1677(f: ProcessParameterValue, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: Json = ProcessParameterValue_ISAJson_encoder(id_map, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1677


def ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_ToISAJsonString_Z3B036AA(this: ProcessParameterValue, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


def ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_fromROCrateJsonString_Static_Z721C83C5(s: str) -> ProcessParameterValue:
    match_value: FSharpResult_2[ProcessParameterValue, str] = Decode_fromString(ProcessParameterValue_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ProcessParameterValue], str]:
    def _arrow1678(f: ProcessParameterValue, spaces: Any=spaces) -> str:
        value: Json = ProcessParameterValue_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1678


def ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_ToROCrateJsonString_71136F3F(this: ProcessParameterValue, spaces: int | None=None) -> str:
    return ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_toROCrateJsonString_Static_71136F3F(spaces)(this)


__all__ = ["ProcessParameterValue_ROCrate_encoder", "ProcessParameterValue_ROCrate_decoder", "ProcessParameterValue_ISAJson_genID", "ProcessParameterValue_ISAJson_encoder", "ProcessParameterValue_ISAJson_decoder", "ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_ToISAJsonString_Z3B036AA", "ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_toROCrateJsonString_Static_71136F3F", "ARCtrl_Process_ProcessParameterValue__ProcessParameterValue_ToROCrateJsonString_71136F3F"]

