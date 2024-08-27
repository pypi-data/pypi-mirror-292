from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, singleton, of_array, empty, FSharpList, append)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (replace, to_text, printf)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, list_1 as list_1_2, IOptionalGetter, string, IGetters)
from ...fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.comment import Comment
from ...Core.Helper.collections_ import Option_fromValueWithDefault
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.component import Component
from ...Core.Process.protocol import Protocol
from ...Core.Process.protocol_parameter import ProtocolParameter
from ..comment import (Comment_ROCrate_encoder, Comment_ROCrate_decoder, Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from ..context.rocrate.isa_protocol_context import context_jsonvalue
from ..decode import Decode_uri
from ..encode import (try_include, try_include_list_opt, default_spaces)
from ..idtable import encode
from ..ontology_annotation import (OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .component import (Component_ROCrate_encoder, Component_ROCrate_decoder, Component_ISAJson_encoder, Component_ISAJson_decoder)
from .protocol_parameter import (ProtocolParameter_ISAJson_encoder, ProtocolParameter_ISAJson_decoder)

def Protocol_ROCrate_genID(study_name: str | None, assay_name: str | None, process_name: str | None, p: Protocol) -> str:
    match_value: str | None = p.ID
    (pattern_matching_result, id_1) = (None, None)
    if match_value is not None:
        if match_value != "":
            pattern_matching_result = 0
            id_1 = match_value

        else: 
            pattern_matching_result = 1


    else: 
        pattern_matching_result = 1

    if pattern_matching_result == 0:
        return id_1

    elif pattern_matching_result == 1:
        match_value_1: str | None = p.Uri
        if match_value_1 is None:
            match_value_2: str | None = p.Name
            if match_value_2 is None:
                (pattern_matching_result_1, an, pn, sn, pn_1, sn_1, pn_2) = (None, None, None, None, None, None, None)
                if study_name is None:
                    if assay_name is None:
                        if process_name is not None:
                            pattern_matching_result_1 = 2
                            pn_2 = process_name

                        else: 
                            pattern_matching_result_1 = 3


                    else: 
                        pattern_matching_result_1 = 3


                elif assay_name is None:
                    if process_name is not None:
                        pattern_matching_result_1 = 1
                        pn_1 = process_name
                        sn_1 = study_name

                    else: 
                        pattern_matching_result_1 = 3


                elif process_name is not None:
                    pattern_matching_result_1 = 0
                    an = assay_name
                    pn = process_name
                    sn = study_name

                else: 
                    pattern_matching_result_1 = 3

                if pattern_matching_result_1 == 0:
                    return (((("#Protocol_" + replace(sn, " ", "_")) + "_") + replace(an, " ", "_")) + "_") + replace(pn, " ", "_")

                elif pattern_matching_result_1 == 1:
                    return (("#Protocol_" + replace(sn_1, " ", "_")) + "_") + replace(pn_1, " ", "_")

                elif pattern_matching_result_1 == 2:
                    return "#Protocol_" + replace(pn_2, " ", "_")

                elif pattern_matching_result_1 == 3:
                    return "#EmptyProtocol"


            else: 
                return "#Protocol_" + replace(match_value_2, " ", "_")


        else: 
            return match_value_1




def Protocol_ROCrate_encoder(study_name: str | None, assay_name: str | None, process_name: str | None, oa: Protocol) -> Json:
    def chooser(tupled_arg: tuple[str, Json], study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1586(value_2: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1587(oa_1: OntologyAnnotation, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow1588(value_4: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1589(value_6: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_6)

    def _arrow1590(value_8: str, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Json(0, value_8)

    def _arrow1591(comment: Comment, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoder(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Protocol_ROCrate_genID(study_name, assay_name, process_name, oa))), ("@type", list_1_1(singleton(Json(0, "Protocol")))), try_include("name", _arrow1586, oa.Name), try_include("protocolType", _arrow1587, oa.ProtocolType), try_include("description", _arrow1588, oa.Description), try_include("uri", _arrow1589, oa.Uri), try_include("version", _arrow1590, oa.Version), try_include_list_opt("components", Component_ROCrate_encoder, oa.Components), try_include_list_opt("comments", _arrow1591, oa.Comments), ("@context", context_jsonvalue)])))


def _arrow1603(get: IGetters) -> Protocol:
    def _arrow1595(__unit: None=None) -> FSharpList[Component]:
        list_4: FSharpList[Component]
        def _arrow1592(__unit: None=None) -> FSharpList[Component] | None:
            arg_1: Decoder_1[FSharpList[Component]] = list_1_2(Component_ROCrate_decoder)
            object_arg: IOptionalGetter = get.Optional
            return object_arg.Field("components", arg_1)

        list_2: FSharpList[Component] = default_arg(_arrow1592(), empty())
        def _arrow1593(__unit: None=None) -> FSharpList[Component] | None:
            arg_3: Decoder_1[FSharpList[Component]] = list_1_2(Component_ROCrate_decoder)
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("reagents", arg_3)

        list_4 = append(default_arg(_arrow1593(), empty()), list_2)
        def _arrow1594(__unit: None=None) -> FSharpList[Component] | None:
            arg_5: Decoder_1[FSharpList[Component]] = list_1_2(Component_ROCrate_decoder)
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("computationalTools", arg_5)

        return append(default_arg(_arrow1594(), empty()), list_4)

    components: FSharpList[Component] | None = Option_fromValueWithDefault(empty(), _arrow1595())
    def _arrow1596(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("@id", Decode_uri)

    def _arrow1597(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("name", string)

    def _arrow1598(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("protocolType", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow1599(__unit: None=None) -> str | None:
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("description", string)

    def _arrow1600(__unit: None=None) -> str | None:
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("uri", Decode_uri)

    def _arrow1601(__unit: None=None) -> str | None:
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("version", string)

    def _arrow1602(__unit: None=None) -> FSharpList[Comment] | None:
        arg_19: Decoder_1[FSharpList[Comment]] = list_1_2(Comment_ROCrate_decoder)
        object_arg_9: IOptionalGetter = get.Optional
        return object_arg_9.Field("comments", arg_19)

    return Protocol(_arrow1596(), _arrow1597(), _arrow1598(), _arrow1599(), _arrow1600(), _arrow1601(), None, components, _arrow1602())


Protocol_ROCrate_decoder: Decoder_1[Protocol] = object(_arrow1603)

def Protocol_ISAJson_encoder(study_name: str | None, assay_name: str | None, process_name: str | None, id_map: Any | None, oa: Protocol) -> Json:
    def f(oa_1: Protocol, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, id_map: Any=id_map, oa: Any=oa) -> Json:
        def chooser(tupled_arg: tuple[str, Json], oa_1: Any=oa_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1605(value: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value)

        def _arrow1606(value_2: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_2)

        def _arrow1607(oa_2: OntologyAnnotation, oa_1: Any=oa_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_2)

        def _arrow1608(value_4: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_4)

        def _arrow1609(value_6: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_6)

        def _arrow1610(value_8: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_8)

        def _arrow1611(value_10: ProtocolParameter, oa_1: Any=oa_1) -> Json:
            return ProtocolParameter_ISAJson_encoder(id_map, value_10)

        def _arrow1612(c: Component, oa_1: Any=oa_1) -> Json:
            return Component_ISAJson_encoder(id_map, c)

        def _arrow1613(comment: Comment, oa_1: Any=oa_1) -> Json:
            return Comment_ISAJson_encoder(id_map, comment)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1605, Protocol_ROCrate_genID(study_name, assay_name, process_name, oa_1)), try_include("name", _arrow1606, oa_1.Name), try_include("protocolType", _arrow1607, oa_1.ProtocolType), try_include("description", _arrow1608, oa_1.Description), try_include("uri", _arrow1609, oa_1.Uri), try_include("version", _arrow1610, oa_1.Version), try_include_list_opt("parameters", _arrow1611, oa_1.Parameters), try_include_list_opt("components", _arrow1612, oa_1.Components), try_include_list_opt("comments", _arrow1613, oa_1.Comments)])))

    if id_map is not None:
        def _arrow1614(p_1: Protocol, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, id_map: Any=id_map, oa: Any=oa) -> str:
            return Protocol_ROCrate_genID(study_name, assay_name, process_name, p_1)

        return encode(_arrow1614, f, oa, id_map)

    else: 
        return f(oa)



def _arrow1624(get: IGetters) -> Protocol:
    def _arrow1615(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("@id", Decode_uri)

    def _arrow1616(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("name", string)

    def _arrow1617(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("protocolType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1618(__unit: None=None) -> str | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("description", string)

    def _arrow1619(__unit: None=None) -> str | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("uri", Decode_uri)

    def _arrow1620(__unit: None=None) -> str | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("version", string)

    def _arrow1621(__unit: None=None) -> FSharpList[ProtocolParameter] | None:
        arg_13: Decoder_1[FSharpList[ProtocolParameter]] = list_1_2(ProtocolParameter_ISAJson_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("parameters", arg_13)

    def _arrow1622(__unit: None=None) -> FSharpList[Component] | None:
        arg_15: Decoder_1[FSharpList[Component]] = list_1_2(Component_ISAJson_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("components", arg_15)

    def _arrow1623(__unit: None=None) -> FSharpList[Comment] | None:
        arg_17: Decoder_1[FSharpList[Comment]] = list_1_2(Comment_ISAJson_decoder)
        object_arg_8: IOptionalGetter = get.Optional
        return object_arg_8.Field("comments", arg_17)

    return Protocol(_arrow1615(), _arrow1616(), _arrow1617(), _arrow1618(), _arrow1619(), _arrow1620(), _arrow1621(), _arrow1622(), _arrow1623())


Protocol_ISAJson_decoder: Decoder_1[Protocol] = object(_arrow1624)

def ARCtrl_Process_Protocol__Protocol_fromISAJsonString_Static_Z721C83C5(s: str) -> Protocol:
    match_value: FSharpResult_2[Protocol, str] = Decode_fromString(Protocol_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Protocol__Protocol_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[Protocol], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1625(f: Protocol, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: Json = Protocol_ISAJson_encoder(None, None, None, id_map, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1625


def ARCtrl_Process_Protocol__Protocol_ToISAJsonString_71136F3F(this: Protocol, spaces: int | None=None) -> str:
    return ARCtrl_Process_Protocol__Protocol_toISAJsonString_Static_Z3B036AA(spaces)(this)


def ARCtrl_Process_Protocol__Protocol_fromROCrateString_Static_Z721C83C5(s: str) -> Protocol:
    match_value: FSharpResult_2[Protocol, str] = Decode_fromString(Protocol_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Protocol__Protocol_toROCrateString_Static_Z482224B9(study_name: str | None=None, assay_name: str | None=None, process_name: str | None=None, spaces: int | None=None) -> Callable[[Protocol], str]:
    def _arrow1626(f: Protocol, study_name: Any=study_name, assay_name: Any=assay_name, process_name: Any=process_name, spaces: Any=spaces) -> str:
        value: Json = Protocol_ROCrate_encoder(study_name, assay_name, process_name, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1626


def ARCtrl_Process_Protocol__Protocol_ToROCrateString_Z482224B9(this: Protocol, study_name: str | None=None, assay_name: str | None=None, process_name: str | None=None, spaces: int | None=None) -> str:
    return ARCtrl_Process_Protocol__Protocol_toROCrateString_Static_Z482224B9(study_name, assay_name, process_name, spaces)(this)


__all__ = ["Protocol_ROCrate_genID", "Protocol_ROCrate_encoder", "Protocol_ROCrate_decoder", "Protocol_ISAJson_encoder", "Protocol_ISAJson_decoder", "ARCtrl_Process_Protocol__Protocol_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Protocol__Protocol_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_Protocol__Protocol_ToISAJsonString_71136F3F", "ARCtrl_Process_Protocol__Protocol_fromROCrateString_Static_Z721C83C5", "ARCtrl_Process_Protocol__Protocol_toROCrateString_Static_Z482224B9", "ARCtrl_Process_Protocol__Protocol_ToROCrateString_Z482224B9"]

