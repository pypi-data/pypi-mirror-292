from __future__ import annotations
from collections.abc import Callable
from typing import (Any, TypeVar)
from ..fable_modules.fable_library.list import (choose, of_array)
from ..fable_modules.fable_library.option import map
from ..fable_modules.fable_library.util import equals
from ..fable_modules.thoth_json_core.decode import (object, IOptionalGetter, string, IGetters)
from ..fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..Core.iproperty_value import IPropertyValue
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.value import Value
from .context.rocrate.property_value_context import context_jsonvalue
from .encode import try_include
from .ontology_annotation import AnnotationValue_decoder

_T = TypeVar("_T")

def gen_id(p: IPropertyValue) -> str:
    matchValue: OntologyAnnotation | None = p.GetCategory()
    matchValue_1: Value | None = p.GetValue()
    matchValue_2: OntologyAnnotation | None = p.GetUnit()
    (pattern_matching_result, t, u, v, t_1, v_1) = (None, None, None, None, None, None)
    if matchValue is not None:
        if matchValue_1 is not None:
            if matchValue_2 is None:
                pattern_matching_result = 1
                t_1 = matchValue
                v_1 = matchValue_1

            else: 
                pattern_matching_result = 0
                t = matchValue
                u = matchValue_2
                v = matchValue_1


        else: 
            pattern_matching_result = 2


    else: 
        pattern_matching_result = 2

    if pattern_matching_result == 0:
        return ((((((("#" + p.GetAdditionalType()) + "/") + t.NameText) + "=") + v.Text) + "") + u.NameText) + ""

    elif pattern_matching_result == 1:
        return ((((("#" + p.GetAdditionalType()) + "/") + t_1.NameText) + "=") + v_1.Text) + ""

    elif pattern_matching_result == 2:
        return ("#Empty" + p.GetAdditionalType()) + ""



def encoder(pv: IPropertyValue) -> Json:
    pattern_input: tuple[str | None, str | None]
    match_value: OntologyAnnotation | None = pv.GetCategory()
    if match_value is None:
        pattern_input = (None, None)

    else: 
        oa: OntologyAnnotation = match_value
        pattern_input = (oa.Name, oa.TermAccessionNumber)

    pattern_input_1: tuple[Json | None, Json | None]
    match_value_1: Value | None = pv.GetValue()
    if match_value_1 is None:
        pattern_input_1 = (None, None)

    else: 
        v: Value = match_value_1
        if v.tag == 1:
            pattern_input_1 = (Json(7, int(v.fields[0]+0x100000000 if v.fields[0] < 0 else v.fields[0])), None)

        elif v.tag == 2:
            pattern_input_1 = (Json(2, v.fields[0]), None)

        elif v.tag == 0:
            oa_1: OntologyAnnotation = v.fields[0]
            def _arrow1308(value_3: str, pv: Any=pv) -> Json:
                return Json(0, value_3)

            def _arrow1309(value_5: str, pv: Any=pv) -> Json:
                return Json(0, value_5)

            pattern_input_1 = (map(_arrow1308, oa_1.Name), map(_arrow1309, oa_1.TermAccessionNumber))

        else: 
            pattern_input_1 = (Json(0, v.fields[0]), None)


    pattern_input_2: tuple[str | None, str | None]
    match_value_2: OntologyAnnotation | None = pv.GetUnit()
    if match_value_2 is None:
        pattern_input_2 = (None, None)

    else: 
        oa_2: OntologyAnnotation = match_value_2
        pattern_input_2 = (oa_2.Name, oa_2.TermAccessionNumber)

    def chooser(tupled_arg: tuple[str, Json], pv: Any=pv) -> tuple[str, Json] | None:
        v_1: Json = tupled_arg[1]
        if equals(v_1, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v_1)


    def _arrow1310(value_11: str, pv: Any=pv) -> Json:
        return Json(0, value_11)

    def _arrow1311(value_13: str, pv: Any=pv) -> Json:
        return Json(0, value_13)

    def _arrow1312(value_15: str, pv: Any=pv) -> Json:
        return Json(0, value_15)

    def _arrow1313(value_17: str, pv: Any=pv) -> Json:
        return Json(0, value_17)

    def _arrow1314(value_19: str, pv: Any=pv) -> Json:
        return Json(0, value_19)

    def _arrow1315(x: Json, pv: Any=pv) -> Json:
        return x

    def _arrow1316(x_1: Json, pv: Any=pv) -> Json:
        return x_1

    def _arrow1317(value_21: str, pv: Any=pv) -> Json:
        return Json(0, value_21)

    def _arrow1318(value_23: str, pv: Any=pv) -> Json:
        return Json(0, value_23)

    return Json(5, choose(chooser, of_array([("@id", Json(0, gen_id(pv))), ("@type", Json(0, "PropertyValue")), ("additionalType", Json(0, pv.GetAdditionalType())), try_include("alternateName", _arrow1310, pv.AlternateName()), try_include("measurementMethod", _arrow1311, pv.MeasurementMethod()), try_include("description", _arrow1312, pv.Description()), try_include("category", _arrow1313, pattern_input[0]), try_include("categoryCode", _arrow1314, pattern_input[1]), try_include("value", _arrow1315, pattern_input_1[0]), try_include("valueCode", _arrow1316, pattern_input_1[1]), try_include("unit", _arrow1317, pattern_input_2[0]), try_include("unitCode", _arrow1318, pattern_input_2[1]), ("@context", context_jsonvalue)])))


def decoder(create: Callable[[str | None, str | None, str | None, OntologyAnnotation | None, Value | None, OntologyAnnotation | None], _T]) -> Decoder_1[_T]:
    def _arrow1320(get: IGetters, create: Any=create) -> _T:
        alternate_name: str | None
        object_arg: IOptionalGetter = get.Optional
        alternate_name = object_arg.Field("alternateName", string)
        measurement_method: str | None
        object_arg_1: IOptionalGetter = get.Optional
        measurement_method = object_arg_1.Field("measurementMethod", string)
        description: str | None
        object_arg_2: IOptionalGetter = get.Optional
        description = object_arg_2.Field("description", string)
        category: OntologyAnnotation | None
        name: str | None
        object_arg_3: IOptionalGetter = get.Optional
        name = object_arg_3.Field("category", string)
        code: str | None
        object_arg_4: IOptionalGetter = get.Optional
        code = object_arg_4.Field("categoryCode", string)
        (pattern_matching_result, code_1) = (None, None)
        if name is None:
            if code is not None:
                if code == "":
                    pattern_matching_result = 0

                else: 
                    pattern_matching_result = 2
                    code_1 = code


            else: 
                pattern_matching_result = 0


        elif code is not None:
            if code == "":
                pattern_matching_result = 1

            else: 
                pattern_matching_result = 2
                code_1 = code


        else: 
            pattern_matching_result = 1

        if pattern_matching_result == 0:
            category = None

        elif pattern_matching_result == 1:
            try: 
                category = OntologyAnnotation.create(name)

            except Exception as err:
                raise Exception(((("Error while decoding category (name:" + str(name)) + "): ") + str(err)) + "")


        elif pattern_matching_result == 2:
            try: 
                category = OntologyAnnotation.from_term_annotation(code_1, name)

            except Exception as err_1:
                raise Exception(((((("Error while decoding category (name:" + str(name)) + ", code:") + code_1) + "): ") + str(err_1)) + "")


        unit: OntologyAnnotation | None
        name_1: str | None
        object_arg_5: IOptionalGetter = get.Optional
        name_1 = object_arg_5.Field("unit", string)
        code_2: str | None
        object_arg_6: IOptionalGetter = get.Optional
        code_2 = object_arg_6.Field("unitCode", string)
        (pattern_matching_result_1, code_3) = (None, None)
        if name_1 is None:
            if code_2 is not None:
                if code_2 == "":
                    pattern_matching_result_1 = 0

                else: 
                    pattern_matching_result_1 = 2
                    code_3 = code_2


            else: 
                pattern_matching_result_1 = 0


        elif code_2 is not None:
            if code_2 == "":
                pattern_matching_result_1 = 1

            else: 
                pattern_matching_result_1 = 2
                code_3 = code_2


        else: 
            pattern_matching_result_1 = 1

        if pattern_matching_result_1 == 0:
            unit = None

        elif pattern_matching_result_1 == 1:
            try: 
                unit = OntologyAnnotation.create(name_1)

            except Exception as err_2:
                raise Exception(((("Error while decoding unit (name:" + str(name_1)) + "): ") + str(err_2)) + "")


        elif pattern_matching_result_1 == 2:
            try: 
                unit = OntologyAnnotation.from_term_annotation(code_3, name_1)

            except Exception as err_3:
                raise Exception(((((("Error while decoding unit (name:" + str(name_1)) + ", code:") + code_3) + "): ") + str(err_3)) + "")


        def _arrow1319(__unit: None=None) -> Value | None:
            value: str | None
            object_arg_7: IOptionalGetter = get.Optional
            value = object_arg_7.Field("value", AnnotationValue_decoder)
            code_4: str | None
            object_arg_8: IOptionalGetter = get.Optional
            code_4 = object_arg_8.Field("valueCode", string)
            if (code_4 is None) if (value is None) else False:
                return None

            else: 
                try: 
                    return Value.from_options(value, None, code_4)

                except Exception as err_4:
                    raise Exception(((((("Error while decoding value " + str(value)) + ",") + str(code_4)) + ": ") + str(err_4)) + "")



        return create(alternate_name, measurement_method, description, category, _arrow1319(), unit)

    return object(_arrow1320)


__all__ = ["gen_id", "encoder", "decoder"]

