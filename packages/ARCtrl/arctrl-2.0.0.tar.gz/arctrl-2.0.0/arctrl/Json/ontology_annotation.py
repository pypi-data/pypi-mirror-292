from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.list import (of_array, choose)
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.seq import filter
from ..fable_modules.fable_library.string_ import (replace, to_text, printf)
from ..fable_modules.fable_library.types import (to_string, Array)
from ..fable_modules.fable_library.util import (int32_to_string, equals, IEnumerable_1)
from ..fable_modules.thoth_json_core.decode import (one_of, map, int_1, float_1, string, object, IOptionalGetter, IGetters)
from ..fable_modules.thoth_json_core.types import (Decoder_1, Json)
from ..fable_modules.thoth_json_python.decode import Decode_fromString
from ..fable_modules.thoth_json_python.encode import to_string as to_string_1
from ..Core.comment import Comment
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.Process.column_index import order_name
from ..Core.uri import URIModule_toString
from .comment import (Comment_encoder, Comment_decoder, Comment_ROCrate_encoderDisambiguatingDescription, Comment_ROCrate_decoderDisambiguatingDescription)
from .context.rocrate.isa_ontology_annotation_context import context_jsonvalue
from .context.rocrate.property_value_context import context_jsonvalue as context_jsonvalue_1
from .decode import Decode_resizeArray
from .encode import (try_include, try_include_seq, default_spaces)
from .idtable import encode
from .string_table import (encode_string, decode_string)

AnnotationValue_decoder: Decoder_1[str] = one_of(of_array([map(int32_to_string, int_1), map(to_string, float_1), string]))

def OntologyAnnotation_encoder(oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1263(value: str, oa: Any=oa) -> Json:
        return Json(0, value)

    def _arrow1264(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1265(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1266(comment: Comment, oa: Any=oa) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([try_include("annotationValue", _arrow1263, oa.Name), try_include("termSource", _arrow1264, oa.TermSourceREF), try_include("termAccession", _arrow1265, oa.TermAccessionNumber), try_include_seq("comments", _arrow1266, oa.Comments)])))


def _arrow1271(get: IGetters) -> OntologyAnnotation:
    def _arrow1267(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("annotationValue", AnnotationValue_decoder)

    def _arrow1268(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("termSource", string)

    def _arrow1269(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("termAccession", string)

    def _arrow1270(__unit: None=None) -> Array[Comment] | None:
        arg_7: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return OntologyAnnotation.create(_arrow1267(), _arrow1268(), _arrow1269(), _arrow1270())


OntologyAnnotation_decoder: Decoder_1[OntologyAnnotation] = object(_arrow1271)

def OntologyAnnotation_compressedEncoder(string_table: Any, oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], string_table: Any=string_table, oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1273(s: str, string_table: Any=string_table, oa: Any=oa) -> Json:
        return encode_string(string_table, s)

    def _arrow1274(s_1: str, string_table: Any=string_table, oa: Any=oa) -> Json:
        return encode_string(string_table, s_1)

    def _arrow1275(s_2: str, string_table: Any=string_table, oa: Any=oa) -> Json:
        return encode_string(string_table, s_2)

    def _arrow1276(comment: Comment, string_table: Any=string_table, oa: Any=oa) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([try_include("a", _arrow1273, oa.Name), try_include("ts", _arrow1274, oa.TermSourceREF), try_include("ta", _arrow1275, oa.TermAccessionNumber), try_include_seq("comments", _arrow1276, oa.Comments)])))


def OntologyAnnotation_compressedDecoder(string_table: Array[str]) -> Decoder_1[OntologyAnnotation]:
    def _arrow1281(get: IGetters, string_table: Any=string_table) -> OntologyAnnotation:
        def _arrow1277(__unit: None=None) -> str | None:
            arg_1: Decoder_1[str] = decode_string(string_table)
            object_arg: IOptionalGetter = get.Optional
            return object_arg.Field("a", arg_1)

        def _arrow1278(__unit: None=None) -> str | None:
            arg_3: Decoder_1[str] = decode_string(string_table)
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("ts", arg_3)

        def _arrow1279(__unit: None=None) -> str | None:
            arg_5: Decoder_1[str] = decode_string(string_table)
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("ta", arg_5)

        def _arrow1280(__unit: None=None) -> Array[Comment] | None:
            arg_7: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("comments", arg_7)

        return OntologyAnnotation(_arrow1277(), _arrow1278(), _arrow1279(), _arrow1280())

    return object(_arrow1281)


def OntologyAnnotation_ROCrate_genID(o: OntologyAnnotation) -> str:
    match_value: str | None = o.TermAccessionNumber
    if match_value is None:
        match_value_1: str | None = o.TermSourceREF
        if match_value_1 is None:
            match_value_2: str | None = o.Name
            if match_value_2 is None:
                return "#DummyOntologyAnnotation"

            else: 
                return "#UserTerm_" + replace(match_value_2, " ", "_")


        else: 
            return "#" + replace(match_value_1, " ", "_")


    else: 
        return URIModule_toString(match_value)



def OntologyAnnotation_ROCrate_encoderDefinedTerm(oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1282(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1283(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1284(value_6: str, oa: Any=oa) -> Json:
        return Json(0, value_6)

    def _arrow1285(comment: Comment, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoderDisambiguatingDescription(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, OntologyAnnotation_ROCrate_genID(oa))), ("@type", Json(0, "OntologyAnnotation")), try_include("annotationValue", _arrow1282, oa.Name), try_include("termSource", _arrow1283, oa.TermSourceREF), try_include("termAccession", _arrow1284, oa.TermAccessionNumber), try_include_seq("comments", _arrow1285, oa.Comments), ("@context", context_jsonvalue)])))


def _arrow1290(get: IGetters) -> OntologyAnnotation:
    def _arrow1286(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("annotationValue", AnnotationValue_decoder)

    def _arrow1287(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("termSource", string)

    def _arrow1288(__unit: None=None) -> str | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("termAccession", string)

    def _arrow1289(__unit: None=None) -> Array[Comment] | None:
        arg_7: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoderDisambiguatingDescription)
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("comments", arg_7)

    return OntologyAnnotation.create(_arrow1286(), _arrow1287(), _arrow1288(), _arrow1289())


OntologyAnnotation_ROCrate_decoderDefinedTerm: Decoder_1[OntologyAnnotation] = object(_arrow1290)

def OntologyAnnotation_ROCrate_encoderPropertyValue(oa: OntologyAnnotation) -> Json:
    def chooser(tupled_arg: tuple[str, Json], oa: Any=oa) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1291(value_2: str, oa: Any=oa) -> Json:
        return Json(0, value_2)

    def _arrow1292(value_4: str, oa: Any=oa) -> Json:
        return Json(0, value_4)

    def _arrow1293(comment: Comment, oa: Any=oa) -> Json:
        return Comment_ROCrate_encoderDisambiguatingDescription(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, OntologyAnnotation_ROCrate_genID(oa))), ("@type", Json(0, "PropertyValue")), try_include("category", _arrow1291, oa.Name), try_include("categoryCode", _arrow1292, oa.TermAccessionNumber), try_include_seq("comments", _arrow1293, oa.Comments), ("@context", context_jsonvalue_1)])))


def _arrow1297(get: IGetters) -> OntologyAnnotation:
    def _arrow1294(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("category", string)

    def _arrow1295(__unit: None=None) -> str | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("categoryCode", string)

    def _arrow1296(__unit: None=None) -> Array[Comment] | None:
        arg_5: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoderDisambiguatingDescription)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("comments", arg_5)

    return OntologyAnnotation.create(_arrow1294(), None, _arrow1295(), _arrow1296())


OntologyAnnotation_ROCrate_decoderPropertyValue: Decoder_1[OntologyAnnotation] = object(_arrow1297)

def OntologyAnnotation_ISAJson_encoder(id_map: Any | None, oa: OntologyAnnotation) -> Json:
    def f(oa_1: OntologyAnnotation, id_map: Any=id_map, oa: Any=oa) -> Json:
        def predicate(c: Comment, oa_1: Any=oa_1) -> bool:
            match_value: str | None = c.Name
            (pattern_matching_result,) = (None,)
            if match_value is not None:
                if match_value == order_name:
                    pattern_matching_result = 0

                else: 
                    pattern_matching_result = 1


            else: 
                pattern_matching_result = 1

            if pattern_matching_result == 0:
                return False

            elif pattern_matching_result == 1:
                return True


        comments: IEnumerable_1[Comment] = filter(predicate, oa_1.Comments)
        def chooser(tupled_arg: tuple[str, Json], oa_1: Any=oa_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1299(value: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value)

        def _arrow1300(value_2: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_2)

        def _arrow1301(value_4: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_4)

        def _arrow1302(value_6: str, oa_1: Any=oa_1) -> Json:
            return Json(0, value_6)

        def _arrow1303(comment: Comment, oa_1: Any=oa_1) -> Json:
            return Comment_encoder(comment)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1299, OntologyAnnotation_ROCrate_genID(oa_1)), try_include("annotationValue", _arrow1300, oa_1.Name), try_include("termSource", _arrow1301, oa_1.TermSourceREF), try_include("termAccession", _arrow1302, oa_1.TermAccessionNumber), try_include_seq("comments", _arrow1303, comments)])))

    if id_map is not None:
        def _arrow1304(o: OntologyAnnotation, id_map: Any=id_map, oa: Any=oa) -> str:
            return OntologyAnnotation_ROCrate_genID(o)

        return encode(_arrow1304, f, oa, id_map)

    else: 
        return f(oa)



OntologyAnnotation_ISAJson_decoder: Decoder_1[OntologyAnnotation] = OntologyAnnotation_decoder

def ARCtrl_OntologyAnnotation__OntologyAnnotation_fromJsonString_Static_Z721C83C5(s: str) -> OntologyAnnotation:
    match_value: FSharpResult_2[OntologyAnnotation, str] = Decode_fromString(OntologyAnnotation_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_OntologyAnnotation__OntologyAnnotation_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[OntologyAnnotation], str]:
    def _arrow1305(obj: OntologyAnnotation, spaces: Any=spaces) -> str:
        value: Json = OntologyAnnotation_encoder(obj)
        return to_string_1(default_spaces(spaces), value)

    return _arrow1305


def ARCtrl_OntologyAnnotation__OntologyAnnotation_ToJsonString_71136F3F(this: OntologyAnnotation, spaces: int | None=None) -> str:
    return ARCtrl_OntologyAnnotation__OntologyAnnotation_toJsonString_Static_71136F3F(spaces)(this)


def ARCtrl_OntologyAnnotation__OntologyAnnotation_fromROCrateJsonString_Static_Z721C83C5(s: str) -> OntologyAnnotation:
    match_value: FSharpResult_2[OntologyAnnotation, str] = Decode_fromString(OntologyAnnotation_ROCrate_decoderDefinedTerm, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_OntologyAnnotation__OntologyAnnotation_toROCrateJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[OntologyAnnotation], str]:
    def _arrow1306(obj: OntologyAnnotation, spaces: Any=spaces) -> str:
        value: Json = OntologyAnnotation_ROCrate_encoderDefinedTerm(obj)
        return to_string_1(default_spaces(spaces), value)

    return _arrow1306


def ARCtrl_OntologyAnnotation__OntologyAnnotation_ToROCrateJsonString_71136F3F(this: OntologyAnnotation, spaces: int | None=None) -> str:
    return ARCtrl_OntologyAnnotation__OntologyAnnotation_toROCrateJsonString_Static_71136F3F(spaces)(this)


def ARCtrl_OntologyAnnotation__OntologyAnnotation_fromISAJsonString_Static_Z721C83C5(s: str) -> OntologyAnnotation:
    match_value: FSharpResult_2[OntologyAnnotation, str] = Decode_fromString(OntologyAnnotation_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_OntologyAnnotation__OntologyAnnotation_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[OntologyAnnotation], str]:
    def _arrow1307(obj: OntologyAnnotation, spaces: Any=spaces) -> str:
        value: Json = OntologyAnnotation_ISAJson_encoder(None, obj)
        return to_string_1(default_spaces(spaces), value)

    return _arrow1307


def ARCtrl_OntologyAnnotation__OntologyAnnotation_ToISAJsonString_71136F3F(this: OntologyAnnotation, spaces: int | None=None) -> str:
    return ARCtrl_OntologyAnnotation__OntologyAnnotation_toISAJsonString_Static_71136F3F(spaces)(this)


__all__ = ["AnnotationValue_decoder", "OntologyAnnotation_encoder", "OntologyAnnotation_decoder", "OntologyAnnotation_compressedEncoder", "OntologyAnnotation_compressedDecoder", "OntologyAnnotation_ROCrate_genID", "OntologyAnnotation_ROCrate_encoderDefinedTerm", "OntologyAnnotation_ROCrate_decoderDefinedTerm", "OntologyAnnotation_ROCrate_encoderPropertyValue", "OntologyAnnotation_ROCrate_decoderPropertyValue", "OntologyAnnotation_ISAJson_encoder", "OntologyAnnotation_ISAJson_decoder", "ARCtrl_OntologyAnnotation__OntologyAnnotation_fromJsonString_Static_Z721C83C5", "ARCtrl_OntologyAnnotation__OntologyAnnotation_toJsonString_Static_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_ToJsonString_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_OntologyAnnotation__OntologyAnnotation_toROCrateJsonString_Static_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_ToROCrateJsonString_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_fromISAJsonString_Static_Z721C83C5", "ARCtrl_OntologyAnnotation__OntologyAnnotation_toISAJsonString_Static_71136F3F", "ARCtrl_OntologyAnnotation__OntologyAnnotation_ToISAJsonString_71136F3F"]

