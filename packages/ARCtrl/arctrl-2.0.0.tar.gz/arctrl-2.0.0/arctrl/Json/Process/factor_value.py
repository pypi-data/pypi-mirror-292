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
from ...Core.Process.factor import Factor
from ...Core.Process.factor_value import (FactorValue, FactorValue_createAsPV)
from ...Core.value import Value as Value_1
from ..decode import Decode_uri
from ..encode import (try_include, default_spaces)
from ..idtable import encode
from ..ontology_annotation import (OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from ..property_value import (encoder, decoder as decoder_1, gen_id)
from .factor import (Factor_ISAJson_encoder, Factor_ISAJson_decoder)
from .value import (Value_ISAJson_encoder, Value_ISAJson_decoder)

FactorValue_ROCrate_encoder: Callable[[FactorValue], Json] = encoder

FactorValue_ROCrate_decoder: Decoder_1[FactorValue] = decoder_1(FactorValue_createAsPV)

def FactorValue_ISAJson_genID(fv: FactorValue) -> str:
    return gen_id(fv)


def FactorValue_ISAJson_encoder(id_map: Any | None, fv: FactorValue) -> Json:
    def f(fv_1: FactorValue, id_map: Any=id_map, fv: Any=fv) -> Json:
        def chooser(tupled_arg: tuple[str, Json], fv_1: Any=fv_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1539(value: str, fv_1: Any=fv_1) -> Json:
            return Json(0, value)

        def _arrow1540(value_2: Factor, fv_1: Any=fv_1) -> Json:
            return Factor_ISAJson_encoder(id_map, value_2)

        def _arrow1541(value_3: Value_1, fv_1: Any=fv_1) -> Json:
            return Value_ISAJson_encoder(id_map, value_3)

        def _arrow1542(oa: OntologyAnnotation, fv_1: Any=fv_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1539, FactorValue_ISAJson_genID(fv_1)), try_include("category", _arrow1540, fv_1.Category), try_include("value", _arrow1541, fv_1.Value), try_include("unit", _arrow1542, fv_1.Unit)])))

    if id_map is not None:
        def _arrow1543(fv_3: FactorValue, id_map: Any=id_map, fv: Any=fv) -> str:
            return FactorValue_ISAJson_genID(fv_3)

        return encode(_arrow1543, f, fv, id_map)

    else: 
        return f(fv)



def _arrow1548(get: IGetters) -> FactorValue:
    def _arrow1544(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1545(__unit: None=None) -> Factor | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("category", Factor_ISAJson_decoder)

    def _arrow1546(__unit: None=None) -> Value_1 | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("value", Value_ISAJson_decoder)

    def _arrow1547(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("unit", OntologyAnnotation_ISAJson_decoder)

    return FactorValue(_arrow1544(), _arrow1545(), _arrow1546(), _arrow1547())


FactorValue_ISAJson_decoder: Decoder_1[FactorValue] = object(_arrow1548)

def ARCtrl_Process_FactorValue__FactorValue_fromISAJsonString_Static_Z721C83C5(s: str) -> FactorValue:
    match_value: FSharpResult_2[FactorValue, str] = Decode_fromString(FactorValue_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[FactorValue], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1549(f: FactorValue, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: Json = FactorValue_ISAJson_encoder(id_map, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1549


def ARCtrl_Process_FactorValue__FactorValue_ToISAJsonString_Z3B036AA(this: FactorValue, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


__all__ = ["FactorValue_ROCrate_encoder", "FactorValue_ROCrate_decoder", "FactorValue_ISAJson_genID", "FactorValue_ISAJson_encoder", "FactorValue_ISAJson_decoder", "ARCtrl_Process_FactorValue__FactorValue_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_FactorValue__FactorValue_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_FactorValue__FactorValue_ToISAJsonString_Z3B036AA"]

