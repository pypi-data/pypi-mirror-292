from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, singleton, of_array, FSharpList)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (replace, to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, string, list_1 as list_1_2, IGetters)
from ...fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.Process.material import Material
from ...Core.Process.material_attribute_value import MaterialAttributeValue
from ...Core.Process.material_type import MaterialType
from ..context.rocrate.isa_material_context import context_jsonvalue
from ..decode import (Decode_uri, Decode_objectNoAdditionalProperties)
from ..encode import (try_include, try_include_list_opt, default_spaces)
from ..idtable import encode
from .material_attribute_value import (MaterialAttributeValue_ROCrate_encoder, MaterialAttributeValue_ROCrate_decoder, MaterialAttributeValue_ISAJson_encoder, MaterialAttributeValue_ISAJson_decoder)
from .material_type import (MaterialType_ROCrate_encoder, MaterialType_ROCrate_decoder, MaterialType_ISAJson_encoder, MaterialType_ISAJson_decoder)

def Material_ROCrate_genID(m: Material) -> str:
    match_value: str | None = m.ID
    if match_value is None:
        match_value_1: str | None = m.Name
        if match_value_1 is None:
            return "#EmptyMaterial"

        else: 
            return "#Material_" + replace(match_value_1, " ", "_")


    else: 
        return match_value



def Material_ROCrate_encoder(oa: Material) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1627(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1628(value_4: MaterialType, oa: Any=oa) -> Json:
        return MaterialType_ROCrate_encoder(value_4)

    def _arrow1629(oa_1: Material, oa: Any=oa) -> Json:
        return Material_ROCrate_encoder(oa_1)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Material_ROCrate_genID(oa))), ("@type", list_1_1(singleton(Json(0, "Material")))), try_include("name", _arrow1627, oa.Name), try_include("type", _arrow1628, oa.MaterialType), try_include_list_opt("characteristics", MaterialAttributeValue_ROCrate_encoder, oa.Characteristics), try_include_list_opt("derivesFrom", _arrow1629, oa.DerivesFrom), ("@context", context_jsonvalue)])))


def _arrow1636(__unit: None=None) -> Decoder_1[Material]:
    def decode(__unit: None=None) -> Decoder_1[Material]:
        def _arrow1635(get: IGetters) -> Material:
            def _arrow1630(__unit: None=None) -> str | None:
                object_arg: IOptionalGetter = get.Optional
                return object_arg.Field("@id", Decode_uri)

            def _arrow1631(__unit: None=None) -> str | None:
                object_arg_1: IOptionalGetter = get.Optional
                return object_arg_1.Field("name", string)

            def _arrow1632(__unit: None=None) -> MaterialType | None:
                object_arg_2: IOptionalGetter = get.Optional
                return object_arg_2.Field("type", MaterialType_ROCrate_decoder)

            def _arrow1633(__unit: None=None) -> FSharpList[MaterialAttributeValue] | None:
                arg_7: Decoder_1[FSharpList[MaterialAttributeValue]] = list_1_2(MaterialAttributeValue_ROCrate_decoder)
                object_arg_3: IOptionalGetter = get.Optional
                return object_arg_3.Field("characteristics", arg_7)

            def _arrow1634(__unit: None=None) -> FSharpList[Material] | None:
                arg_9: Decoder_1[FSharpList[Material]] = list_1_2(decode(None))
                object_arg_4: IOptionalGetter = get.Optional
                return object_arg_4.Field("derivesFrom", arg_9)

            return Material(_arrow1630(), _arrow1631(), _arrow1632(), _arrow1633(), _arrow1634())

        return object(_arrow1635)

    return decode(None)


Material_ROCrate_decoder: Decoder_1[Material] = _arrow1636()

def Material_ISAJson_encoder(id_map: Any | None, c: Material) -> Json:
    def f(oa: Material, id_map: Any=id_map, c: Any=c) -> Json:
        def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1638(value: str, oa: Any=oa) -> Json:
            return Json(0, value)

        def _arrow1639(value_2: str, oa: Any=oa) -> Json:
            return Json(0, value_2)

        def _arrow1640(oa_1: MaterialAttributeValue, oa: Any=oa) -> Json:
            return MaterialAttributeValue_ISAJson_encoder(id_map, oa_1)

        def _arrow1641(c_1: Material, oa: Any=oa) -> Json:
            return Material_ISAJson_encoder(id_map, c_1)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1638, Material_ROCrate_genID(oa)), try_include("name", _arrow1639, oa.Name), try_include("type", MaterialType_ISAJson_encoder, oa.MaterialType), try_include_list_opt("characteristics", _arrow1640, oa.Characteristics), try_include_list_opt("derivesFrom", _arrow1641, oa.DerivesFrom)])))

    if id_map is not None:
        def _arrow1642(m_1: Material, id_map: Any=id_map, c: Any=c) -> str:
            return Material_ROCrate_genID(m_1)

        return encode(_arrow1642, f, c, id_map)

    else: 
        return f(c)



Material_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "@type", "name", "type", "characteristics", "derivesFrom", "@context"])

def _arrow1649(__unit: None=None) -> Decoder_1[Material]:
    def decode(__unit: None=None) -> Decoder_1[Material]:
        def _arrow1648(get: IGetters) -> Material:
            def _arrow1643(__unit: None=None) -> str | None:
                object_arg: IOptionalGetter = get.Optional
                return object_arg.Field("@id", Decode_uri)

            def _arrow1644(__unit: None=None) -> str | None:
                object_arg_1: IOptionalGetter = get.Optional
                return object_arg_1.Field("name", string)

            def _arrow1645(__unit: None=None) -> MaterialType | None:
                object_arg_2: IOptionalGetter = get.Optional
                return object_arg_2.Field("type", MaterialType_ISAJson_decoder)

            def _arrow1646(__unit: None=None) -> FSharpList[MaterialAttributeValue] | None:
                arg_7: Decoder_1[FSharpList[MaterialAttributeValue]] = list_1_2(MaterialAttributeValue_ISAJson_decoder)
                object_arg_3: IOptionalGetter = get.Optional
                return object_arg_3.Field("characteristics", arg_7)

            def _arrow1647(__unit: None=None) -> FSharpList[Material] | None:
                arg_9: Decoder_1[FSharpList[Material]] = list_1_2(decode(None))
                object_arg_4: IOptionalGetter = get.Optional
                return object_arg_4.Field("derivesFrom", arg_9)

            return Material(_arrow1643(), _arrow1644(), _arrow1645(), _arrow1646(), _arrow1647())

        return Decode_objectNoAdditionalProperties(Material_ISAJson_allowedFields, _arrow1648)

    return decode(None)


Material_ISAJson_decoder: Decoder_1[Material] = _arrow1649()

def ARCtrl_Process_Material__Material_fromISAJsonString_Static_Z721C83C5(s: str) -> Material:
    match_value: FSharpResult_2[Material, str] = Decode_fromString(Material_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Material__Material_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[Material], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1650(f: Material, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: Json = Material_ISAJson_encoder(id_map, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1650


def ARCtrl_Process_Material__Material_ToISAJsonString_Z3B036AA(this: Material, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_Process_Material__Material_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


def ARCtrl_Process_Material__Material_fromROCrateJsonString_Static_Z721C83C5(s: str) -> Material:
    match_value: FSharpResult_2[Material, str] = Decode_fromString(Material_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Material__Material_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Material], str]:
    def _arrow1651(f: Material, spaces: Any=spaces) -> str:
        value: Json = Material_ROCrate_encoder(f)
        return to_string(default_spaces(spaces), value)

    return _arrow1651


def ARCtrl_Process_Material__Material_ToROCrateJsonString_71136F3F(this: Material, spaces: int | None=None) -> str:
    return ARCtrl_Process_Material__Material_toROCrateJsonString_Static_71136F3F(spaces)(this)


__all__ = ["Material_ROCrate_genID", "Material_ROCrate_encoder", "Material_ROCrate_decoder", "Material_ISAJson_encoder", "Material_ISAJson_allowedFields", "Material_ISAJson_decoder", "ARCtrl_Process_Material__Material_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Material__Material_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_Material__Material_ToISAJsonString_Z3B036AA", "ARCtrl_Process_Material__Material_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_Process_Material__Material_toROCrateJsonString_Static_71136F3F", "ARCtrl_Process_Material__Material_ToROCrateJsonString_71136F3F"]

