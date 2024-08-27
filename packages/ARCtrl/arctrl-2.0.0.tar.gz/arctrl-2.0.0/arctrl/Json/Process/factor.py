from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import (choose, of_array)
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.fable_library.types import Array
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.decode import (object, IOptionalGetter, string, IGetters)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.comment import Comment
from ...Core.ontology_annotation import OntologyAnnotation
from ...Core.Process.factor import Factor
from ..comment import (Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from ..decode import Decode_resizeArray
from ..encode import (try_include, try_include_seq, default_spaces)
from ..idtable import encode
from ..ontology_annotation import (OntologyAnnotation_ROCrate_genID, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)

def Factor_ISAJson_genID(f: Factor) -> str:
    match_value: str | None = f.Name
    if match_value is None:
        match_value_1: OntologyAnnotation | None = f.FactorType
        if match_value_1 is None:
            return "#EmptyFactor"

        else: 
            return ("#Factor/" + OntologyAnnotation_ROCrate_genID(match_value_1)) + ""


    else: 
        return ("#Factor/" + match_value) + ""



def Factor_ISAJson_encoder(id_map: Any | None, value: Factor) -> Json:
    def f_1(value_1: Factor, id_map: Any=id_map, value: Any=value) -> Json:
        def chooser(tupled_arg: tuple[str, Json], value_1: Any=value_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1450(value_2: str, value_1: Any=value_1) -> Json:
            return Json(0, value_2)

        def _arrow1451(value_4: str, value_1: Any=value_1) -> Json:
            return Json(0, value_4)

        def _arrow1452(oa: OntologyAnnotation, value_1: Any=value_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        def _arrow1453(comment: Comment, value_1: Any=value_1) -> Json:
            return Comment_ISAJson_encoder(id_map, comment)

        return Json(5, choose(chooser, of_array([try_include("@id", _arrow1450, Factor_ISAJson_genID(value_1)), try_include("factorName", _arrow1451, value_1.Name), try_include("factorType", _arrow1452, value_1.FactorType), try_include_seq("comments", _arrow1453, default_arg(value_1.Comments, []))])))

    if id_map is not None:
        def _arrow1454(f_2: Factor, id_map: Any=id_map, value: Any=value) -> str:
            return Factor_ISAJson_genID(f_2)

        return encode(_arrow1454, f_1, value, id_map)

    else: 
        return f_1(value)



def _arrow1458(get: IGetters) -> Factor:
    def _arrow1455(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("factorName", string)

    def _arrow1456(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("factorType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1457(__unit: None=None) -> Array[Comment] | None:
        arg_5: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ISAJson_decoder)
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("comments", arg_5)

    return Factor(_arrow1455(), _arrow1456(), _arrow1457())


Factor_ISAJson_decoder: Decoder_1[Factor] = object(_arrow1458)

def ARCtrl_Process_Factor__Factor_fromISAJsonString_Static_Z721C83C5(s: str) -> Factor:
    match_value: FSharpResult_2[Factor, str] = Decode_fromString(Factor_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_Factor__Factor_toISAJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[Factor], str]:
    def _arrow1459(f: Factor, spaces: Any=spaces) -> str:
        value: Json = Factor_ISAJson_encoder(None, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1459


def ARCtrl_Process_Factor__Factor_ToISAJsonString_71136F3F(this: Factor, spaces: int | None=None) -> str:
    return ARCtrl_Process_Factor__Factor_toISAJsonString_Static_71136F3F(spaces)(this)


__all__ = ["Factor_ISAJson_genID", "Factor_ISAJson_encoder", "Factor_ISAJson_decoder", "ARCtrl_Process_Factor__Factor_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_Factor__Factor_toISAJsonString_Static_71136F3F", "ARCtrl_Process_Factor__Factor_ToISAJsonString_71136F3F"]

