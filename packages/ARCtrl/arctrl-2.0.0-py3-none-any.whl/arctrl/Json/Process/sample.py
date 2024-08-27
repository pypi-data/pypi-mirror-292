from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ...fable_modules.fable_library.list import (FSharpList, map, empty, append, choose, singleton, of_array)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (replace, to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (string, object, list_1 as list_1_3, IOptionalGetter, IGetters)
from ...fable_modules.thoth_json_core.encode import list_1 as list_1_2
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1, ErrorReason_1, IDecoderHelpers_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.Helper.collections_ import Option_fromValueWithDefault
from ...Core.Process.factor_value import FactorValue
from ...Core.Process.material_attribute_value import MaterialAttributeValue
from ...Core.Process.sample import Sample
from ...Core.Process.source import Source
from ..context.rocrate.isa_sample_context import context_jsonvalue
from ..decode import (Decode_uri, Decode_objectNoAdditionalProperties)
from ..encode import (try_include, try_include_list, try_include_list_opt, default_spaces)
from ..idtable import encode
from .factor_value import (FactorValue_ROCrate_encoder, FactorValue_ROCrate_decoder, FactorValue_ISAJson_encoder, FactorValue_ISAJson_decoder)
from .material_attribute_value import (MaterialAttributeValue_ROCrate_encoder, MaterialAttributeValue_ROCrate_decoder, MaterialAttributeValue_ISAJson_encoder, MaterialAttributeValue_ISAJson_decoder)
from .source import (Source_ROCrate_decoder, Source_ISAJson_encoder, Source_ISAJson_decoder)

__A_ = TypeVar("__A_")

def Sample_ROCrate_genID(s: Sample) -> str:
    match_value: str | None = s.ID
    if match_value is None:
        match_value_1: str | None = s.Name
        if match_value_1 is None:
            return "#EmptySample"

        else: 
            return "#Sample_" + replace(match_value_1, " ", "_")


    else: 
        return match_value



def Sample_ROCrate_encoder(oa: Sample) -> Json:
    additional_properties: FSharpList[Json]
    list_4: FSharpList[Json] = map(MaterialAttributeValue_ROCrate_encoder, default_arg(oa.Characteristics, empty()))
    additional_properties = append(map(FactorValue_ROCrate_encoder, default_arg(oa.FactorValues, empty())), list_4)
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1679(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1680(x: Json, oa: Any=oa) -> Json:
        return x

    return Json(5, choose(chooser, of_array([("@id", Json(0, Sample_ROCrate_genID(oa))), ("@type", list_1_2(singleton(Json(0, "Sample")))), try_include("name", _arrow1679, oa.Name), try_include_list("additionalProperties", _arrow1680, additional_properties), ("@context", context_jsonvalue)])))


class ObjectExpr1682(Decoder_1[tuple[MaterialAttributeValue | None, FactorValue | None]]):
    def Decode(self, s: IDecoderHelpers_1[__A_], json: __A_) -> FSharpResult_2[tuple[MaterialAttributeValue | None, FactorValue | None], tuple[str, ErrorReason_1[__A_]]]:
        def _arrow1681(__unit: None=None) -> str:
            match_value: FSharpResult_2[str, tuple[str, ErrorReason_1[__A_]]] = string.Decode(s, s.get_property("additionalType", json))
            return match_value.fields[0] if (match_value.tag == 0) else ""

        if (_arrow1681() if s.has_property("additionalType", json) else "") == "FactorValue":
            match_value_1: FSharpResult_2[FactorValue, tuple[str, ErrorReason_1[__A_]]] = FactorValue_ROCrate_decoder.Decode(s, json)
            return FSharpResult_2(1, match_value_1.fields[0]) if (match_value_1.tag == 1) else FSharpResult_2(0, (None, match_value_1.fields[0]))

        else: 
            match_value_2: FSharpResult_2[MaterialAttributeValue, tuple[str, ErrorReason_1[__A_]]] = MaterialAttributeValue_ROCrate_decoder.Decode(s, json)
            return FSharpResult_2(1, match_value_2.fields[0]) if (match_value_2.tag == 1) else FSharpResult_2(0, (match_value_2.fields[0], None))



Sample_ROCrate_additionalPropertyDecoder: Decoder_1[tuple[MaterialAttributeValue | None, FactorValue | None]] = ObjectExpr1682()

def _arrow1686(get: IGetters) -> Sample:
    additional_properties: FSharpList[tuple[MaterialAttributeValue | None, FactorValue | None]] | None
    arg_1: Decoder_1[FSharpList[tuple[MaterialAttributeValue | None, FactorValue | None]]] = list_1_3(Sample_ROCrate_additionalPropertyDecoder)
    object_arg: IOptionalGetter = get.Optional
    additional_properties = object_arg.Field("additionalProperties", arg_1)
    pattern_input: tuple[FSharpList[MaterialAttributeValue] | None, FSharpList[FactorValue] | None]
    if additional_properties is not None:
        additional_properties_1: FSharpList[tuple[MaterialAttributeValue | None, FactorValue | None]] = additional_properties
        def chooser(tuple: tuple[MaterialAttributeValue | None, FactorValue | None]) -> MaterialAttributeValue | None:
            return tuple[0]

        def chooser_1(tuple_1: tuple[MaterialAttributeValue | None, FactorValue | None]) -> FactorValue | None:
            return tuple_1[1]

        pattern_input = (Option_fromValueWithDefault(empty(), choose(chooser, additional_properties_1)), Option_fromValueWithDefault(empty(), choose(chooser_1, additional_properties_1)))

    else: 
        pattern_input = (None, None)

    def _arrow1683(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("@id", Decode_uri)

    def _arrow1684(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("name", string)

    def _arrow1685(__unit: None=None) -> FSharpList[Source] | None:
        arg_7: Decoder_1[FSharpList[Source]] = list_1_3(Source_ROCrate_decoder)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("derivesFrom", arg_7)

    return Sample(_arrow1683(), _arrow1684(), pattern_input[0], pattern_input[1], _arrow1685())


Sample_ROCrate_decoder: Decoder_1[Sample] = object(_arrow1686)

def Sample_ISAJson_encoder(id_map: Any | None, oa: Sample) -> Json:
    def f(oa_1: Sample, id_map: Any=id_map, oa: Any=oa) -> Json:
        def chooser(tupled_arg: tuple[str, Json], oa_1: Any=oa_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1688(value: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value)

        def _arrow1689(value_2: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_2)

        def _arrow1690(oa_2: MaterialAttributeValue, oa_1: Any=oa_1) -> Json:
            return MaterialAttributeValue_ISAJson_encoder(id_map, oa_2)

        def _arrow1691(fv: FactorValue, oa_1: Any=oa_1) -> Json:
            return FactorValue_ISAJson_encoder(id_map, fv)

        def _arrow1692(oa_3: Source, oa_1: Any=oa_1) -> Json:
            return Source_ISAJson_encoder(id_map, oa_3)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1688, Sample_ROCrate_genID(oa_1)), try_include("name", _arrow1689, oa_1.Name), try_include_list_opt("characteristics", _arrow1690, oa_1.Characteristics), try_include_list_opt("factorValues", _arrow1691, oa_1.FactorValues), try_include_list_opt("derivesFrom", _arrow1692, oa_1.DerivesFrom)])))

    if id_map is not None:
        def _arrow1693(s_1: Sample, id_map: Any=id_map, oa: Any=oa) -> str:
            return Sample_ROCrate_genID(s_1)

        return encode(_arrow1693, f, oa, id_map)

    else: 
        return f(oa)



Sample_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "name", "characteristics", "factorValues", "derivesFrom", "@type", "@context"])

def _arrow1699(get: IGetters) -> Sample:
    def _arrow1694(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1695(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow1696(__unit: None=None) -> FSharpList[MaterialAttributeValue] | None:
        arg_5: Decoder_1[FSharpList[MaterialAttributeValue]] = list_1_3(MaterialAttributeValue_ISAJson_decoder)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("characteristics", arg_5)

    def _arrow1697(__unit: None=None) -> FSharpList[FactorValue] | None:
        arg_7: Decoder_1[FSharpList[FactorValue]] = list_1_3(FactorValue_ISAJson_decoder)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("factorValues", arg_7)

    def _arrow1698(__unit: None=None) -> FSharpList[Source] | None:
        arg_9: Decoder_1[FSharpList[Source]] = list_1_3(Source_ISAJson_decoder)
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("derivesFrom", arg_9)

    return Sample(_arrow1694(), _arrow1695(), _arrow1696(), _arrow1697(), _arrow1698())


Sample_ISAJson_decoder: Decoder_1[Sample] = Decode_objectNoAdditionalProperties(Sample_ISAJson_allowedFields, _arrow1699)

def ARCtrl_Process_Sample__Sample_fromISAJsonString_Static_Z721C83C5(s: str) -> Sample:
    match_value: FSharpResult_2[Sample, str] = Decode_fromString(Sample_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Sample__Sample_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[Sample], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1700(f: Sample, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value_1: Json = Sample_ISAJson_encoder(id_map, f)
        return to_string(default_spaces(spaces), value_1)

    return _arrow1700


def ARCtrl_Process_Sample__Sample_ToISAJsonString_Z3B036AA(this: Sample, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_Process_Sample__Sample_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


def ARCtrl_Process_Sample__Sample_fromROCrateString_Static_Z721C83C5(s: str) -> Sample:
    match_value: FSharpResult_2[Sample, str] = Decode_fromString(Sample_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Sample__Sample_toROCrateString_Static_71136F3F(spaces: int | None=None) -> Callable[[Sample], str]:
    def _arrow1701(f: Sample, spaces: Any=spaces) -> str:
        value: Json = Sample_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1701


def ARCtrl_Process_Sample__Sample_ToROCrateString_71136F3F(this: Sample, spaces: int | None=None) -> str:
    return ARCtrl_Process_Sample__Sample_toROCrateString_Static_71136F3F(spaces)(this)


__all__ = ["Sample_ROCrate_genID", "Sample_ROCrate_encoder", "Sample_ROCrate_additionalPropertyDecoder", "Sample_ROCrate_decoder", "Sample_ISAJson_encoder", "Sample_ISAJson_allowedFields", "Sample_ISAJson_decoder", "ARCtrl_Process_Sample__Sample_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Sample__Sample_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_Sample__Sample_ToISAJsonString_Z3B036AA", "ARCtrl_Process_Sample__Sample_fromROCrateString_Static_Z721C83C5", "ARCtrl_Process_Sample__Sample_toROCrateString_Static_71136F3F", "ARCtrl_Process_Sample__Sample_ToROCrateString_71136F3F"]

