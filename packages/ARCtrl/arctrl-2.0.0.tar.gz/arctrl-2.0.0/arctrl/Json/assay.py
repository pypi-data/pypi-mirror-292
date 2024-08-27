from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ..fable_modules.fable_library.list import (choose, of_array, FSharpList, singleton, empty)
from ..fable_modules.fable_library.option import (default_arg, map, bind)
from ..fable_modules.fable_library.result import FSharpResult_2
from ..fable_modules.fable_library.string_ import (replace, to_text, printf, to_fail)
from ..fable_modules.fable_library.types import Array
from ..fable_modules.fable_library.util import equals
from ..fable_modules.thoth_json_core.decode import (object, IRequiredGetter, string, IOptionalGetter, IGetters, list_1 as list_1_2, map as map_1)
from ..fable_modules.thoth_json_core.encode import list_1 as list_1_1
from ..fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ..fable_modules.thoth_json_python.decode import Decode_fromString
from ..fable_modules.thoth_json_python.encode import to_string
from ..Core.arc_types import ArcAssay
from ..Core.comment import Comment
from ..Core.conversion import (ARCtrl_ArcTables__ArcTables_GetProcesses, ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D, JsonTypes_composeTechnologyPlatform, JsonTypes_decomposeTechnologyPlatform)
from ..Core.data import Data
from ..Core.data_map import DataMap
from ..Core.Helper.collections_ import Option_fromValueWithDefault
from ..Core.Helper.identifier import (Assay_fileNameFromIdentifier, create_missing_identifier, Assay_tryIdentifierFromFileName)
from ..Core.ontology_annotation import OntologyAnnotation
from ..Core.person import Person
from ..Core.Process.material_attribute import MaterialAttribute
from ..Core.Process.process import Process
from ..Core.Process.process_sequence import (get_data, get_units, get_characteristics)
from ..Core.Table.arc_table import ArcTable
from ..Core.Table.arc_tables import ArcTables
from ..Core.Table.composite_cell import CompositeCell
from .comment import (Comment_encoder, Comment_decoder, Comment_ROCrate_encoder, Comment_ROCrate_decoder, Comment_ISAJson_encoder, Comment_ISAJson_decoder)
from .context.rocrate.isa_assay_context import context_jsonvalue
from .data import (Data_ROCrate_encoder, Data_ISAJson_encoder)
from .DataMap.data_map import (encoder as encoder_3, decoder as decoder_1, encoder_compressed, decoder_compressed)
from .decode import (Decode_resizeArray, Decode_objectNoAdditionalProperties)
from .encode import (try_include, try_include_seq, try_include_list, default_spaces)
from .idtable import encode
from .ontology_annotation import (OntologyAnnotation_encoder, OntologyAnnotation_decoder, OntologyAnnotation_ROCrate_encoderPropertyValue, OntologyAnnotation_ROCrate_encoderDefinedTerm, OntologyAnnotation_ROCrate_decoderPropertyValue, OntologyAnnotation_ROCrate_decoderDefinedTerm, OntologyAnnotation_ISAJson_encoder, OntologyAnnotation_ISAJson_decoder)
from .person import (Person_encoder, Person_decoder, Person_ROCrate_encoder, Person_ROCrate_decoder)
from .Process.assay_materials import encoder as encoder_4
from .Process.material_attribute import MaterialAttribute_ISAJson_encoder
from .Process.process import (Process_ROCrate_encoder, Process_ROCrate_decoder, Process_ISAJson_encoder, Process_ISAJson_decoder)
from .Table.arc_table import (ArcTable_encoder, ArcTable_decoder, ArcTable_encoderCompressed, ArcTable_decoderCompressed)
from .Table.compression import (decode, encode as encode_1)

def Assay_encoder(assay: ArcAssay) -> Json:
    def chooser(tupled_arg: tuple[str, Json], assay: Any=assay) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1898(oa: OntologyAnnotation, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa)

    def _arrow1899(oa_1: OntologyAnnotation, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1900(oa_2: OntologyAnnotation, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow1901(dm: DataMap, assay: Any=assay) -> Json:
        return encoder_3(dm)

    def _arrow1902(table: ArcTable, assay: Any=assay) -> Json:
        return ArcTable_encoder(table)

    def _arrow1903(person: Person, assay: Any=assay) -> Json:
        return Person_encoder(person)

    def _arrow1904(comment: Comment, assay: Any=assay) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, assay.Identifier)), try_include("MeasurementType", _arrow1898, assay.MeasurementType), try_include("TechnologyType", _arrow1899, assay.TechnologyType), try_include("TechnologyPlatform", _arrow1900, assay.TechnologyPlatform), try_include("DataMap", _arrow1901, assay.DataMap), try_include_seq("Tables", _arrow1902, assay.Tables), try_include_seq("Performers", _arrow1903, assay.Performers), try_include_seq("Comments", _arrow1904, assay.Comments)])))


def _arrow1913(get: IGetters) -> ArcAssay:
    def _arrow1905(__unit: None=None) -> str:
        object_arg: IRequiredGetter = get.Required
        return object_arg.Field("Identifier", string)

    def _arrow1906(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("MeasurementType", OntologyAnnotation_decoder)

    def _arrow1907(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("TechnologyType", OntologyAnnotation_decoder)

    def _arrow1908(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("TechnologyPlatform", OntologyAnnotation_decoder)

    def _arrow1909(__unit: None=None) -> Array[ArcTable] | None:
        arg_9: Decoder_1[Array[ArcTable]] = Decode_resizeArray(ArcTable_decoder)
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("Tables", arg_9)

    def _arrow1910(__unit: None=None) -> DataMap | None:
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("DataMap", decoder_1)

    def _arrow1911(__unit: None=None) -> Array[Person] | None:
        arg_13: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("Performers", arg_13)

    def _arrow1912(__unit: None=None) -> Array[Comment] | None:
        arg_15: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
        object_arg_7: IOptionalGetter = get.Optional
        return object_arg_7.Field("Comments", arg_15)

    return ArcAssay.create(_arrow1905(), _arrow1906(), _arrow1907(), _arrow1908(), _arrow1909(), _arrow1910(), _arrow1911(), _arrow1912())


Assay_decoder: Decoder_1[ArcAssay] = object(_arrow1913)

def Assay_encoderCompressed(string_table: Any, oa_table: Any, cell_table: Any, assay: ArcAssay) -> Json:
    def chooser(tupled_arg: tuple[str, Json], string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1914(oa: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa)

    def _arrow1915(oa_1: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_1)

    def _arrow1916(oa_2: OntologyAnnotation, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return OntologyAnnotation_encoder(oa_2)

    def _arrow1917(table: ArcTable, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return ArcTable_encoderCompressed(string_table, oa_table, cell_table, table)

    def _arrow1918(dm: DataMap, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return encoder_compressed(string_table, oa_table, cell_table, dm)

    def _arrow1919(person: Person, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return Person_encoder(person)

    def _arrow1920(comment: Comment, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table, assay: Any=assay) -> Json:
        return Comment_encoder(comment)

    return Json(5, choose(chooser, of_array([("Identifier", Json(0, assay.Identifier)), try_include("MeasurementType", _arrow1914, assay.MeasurementType), try_include("TechnologyType", _arrow1915, assay.TechnologyType), try_include("TechnologyPlatform", _arrow1916, assay.TechnologyPlatform), try_include_seq("Tables", _arrow1917, assay.Tables), try_include("DataMap", _arrow1918, assay.DataMap), try_include_seq("Performers", _arrow1919, assay.Performers), try_include_seq("Comments", _arrow1920, assay.Comments)])))


def Assay_decoderCompressed(string_table: Array[str], oa_table: Array[OntologyAnnotation], cell_table: Array[CompositeCell]) -> Decoder_1[ArcAssay]:
    def _arrow1929(get: IGetters, string_table: Any=string_table, oa_table: Any=oa_table, cell_table: Any=cell_table) -> ArcAssay:
        def _arrow1921(__unit: None=None) -> str:
            object_arg: IRequiredGetter = get.Required
            return object_arg.Field("Identifier", string)

        def _arrow1922(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_1: IOptionalGetter = get.Optional
            return object_arg_1.Field("MeasurementType", OntologyAnnotation_decoder)

        def _arrow1923(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_2: IOptionalGetter = get.Optional
            return object_arg_2.Field("TechnologyType", OntologyAnnotation_decoder)

        def _arrow1924(__unit: None=None) -> OntologyAnnotation | None:
            object_arg_3: IOptionalGetter = get.Optional
            return object_arg_3.Field("TechnologyPlatform", OntologyAnnotation_decoder)

        def _arrow1925(__unit: None=None) -> Array[ArcTable] | None:
            arg_9: Decoder_1[Array[ArcTable]] = Decode_resizeArray(ArcTable_decoderCompressed(string_table, oa_table, cell_table))
            object_arg_4: IOptionalGetter = get.Optional
            return object_arg_4.Field("Tables", arg_9)

        def _arrow1926(__unit: None=None) -> DataMap | None:
            arg_11: Decoder_1[DataMap] = decoder_compressed(string_table, oa_table, cell_table)
            object_arg_5: IOptionalGetter = get.Optional
            return object_arg_5.Field("DataMap", arg_11)

        def _arrow1927(__unit: None=None) -> Array[Person] | None:
            arg_13: Decoder_1[Array[Person]] = Decode_resizeArray(Person_decoder)
            object_arg_6: IOptionalGetter = get.Optional
            return object_arg_6.Field("Performers", arg_13)

        def _arrow1928(__unit: None=None) -> Array[Comment] | None:
            arg_15: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_decoder)
            object_arg_7: IOptionalGetter = get.Optional
            return object_arg_7.Field("Comments", arg_15)

        return ArcAssay.create(_arrow1921(), _arrow1922(), _arrow1923(), _arrow1924(), _arrow1925(), _arrow1926(), _arrow1927(), _arrow1928())

    return object(_arrow1929)


def Assay_ROCrate_genID(a: ArcAssay) -> str:
    match_value: str = a.Identifier
    if match_value == "":
        return "#EmptyAssay"

    else: 
        return ("#assay/" + replace(match_value, " ", "_")) + ""



def Assay_ROCrate_encoder(study_name: str | None, a: ArcAssay) -> Json:
    file_name: str = Assay_fileNameFromIdentifier(a.Identifier)
    processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a)
    data_files: FSharpList[Data] = get_data(processes)
    def chooser(tupled_arg: tuple[str, Json], study_name: Any=study_name, a: Any=a) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1930(oa: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> Json:
        return OntologyAnnotation_ROCrate_encoderPropertyValue(oa)

    def _arrow1931(oa_1: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> Json:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_1)

    def _arrow1932(oa_2: OntologyAnnotation, study_name: Any=study_name, a: Any=a) -> Json:
        return OntologyAnnotation_ROCrate_encoderDefinedTerm(oa_2)

    def _arrow1933(oa_3: Person, study_name: Any=study_name, a: Any=a) -> Json:
        return Person_ROCrate_encoder(oa_3)

    def _arrow1934(oa_4: Data, study_name: Any=study_name, a: Any=a) -> Json:
        return Data_ROCrate_encoder(oa_4)

    def _arrow1936(__unit: None=None, study_name: Any=study_name, a: Any=a) -> Callable[[Process], Json]:
        assay_name: str | None = a.Identifier
        def _arrow1935(oa_5: Process) -> Json:
            return Process_ROCrate_encoder(study_name, assay_name, oa_5)

        return _arrow1935

    def _arrow1937(comment: Comment, study_name: Any=study_name, a: Any=a) -> Json:
        return Comment_ROCrate_encoder(comment)

    return Json(5, choose(chooser, of_array([("@id", Json(0, Assay_ROCrate_genID(a))), ("@type", list_1_1(singleton(Json(0, "Assay")))), ("additionalType", Json(0, "Assay")), ("identifier", Json(0, a.Identifier)), ("filename", Json(0, file_name)), try_include("measurementType", _arrow1930, a.MeasurementType), try_include("technologyType", _arrow1931, a.TechnologyType), try_include("technologyPlatform", _arrow1932, a.TechnologyPlatform), try_include_seq("performers", _arrow1933, a.Performers), try_include_list("dataFiles", _arrow1934, data_files), try_include_list("processSequence", _arrow1936(), processes), try_include_seq("comments", _arrow1937, a.Comments), ("@context", context_jsonvalue)])))


def _arrow1945(get: IGetters) -> ArcAssay:
    def _arrow1938(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("identifier", string)

    identifier: str = default_arg(_arrow1938(), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow1939(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(Process_ROCrate_decoder)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow1939())
    def _arrow1940(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("measurementType", OntologyAnnotation_ROCrate_decoderPropertyValue)

    def _arrow1941(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("technologyType", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow1942(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("technologyPlatform", OntologyAnnotation_ROCrate_decoderDefinedTerm)

    def _arrow1943(__unit: None=None) -> Array[Person] | None:
        arg_12: Decoder_1[Array[Person]] = Decode_resizeArray(Person_ROCrate_decoder)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("performers", arg_12)

    def _arrow1944(__unit: None=None) -> Array[Comment] | None:
        arg_14: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ROCrate_decoder)
        object_arg_6: IOptionalGetter = get.Optional
        return object_arg_6.Field("comments", arg_14)

    return ArcAssay(identifier, _arrow1940(), _arrow1941(), _arrow1942(), tables, None, _arrow1943(), _arrow1944())


Assay_ROCrate_decoder: Decoder_1[ArcAssay] = object(_arrow1945)

def Assay_ISAJson_encoder(study_name: str | None, id_map: Any | None, a: ArcAssay) -> Json:
    def f(a_1: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> Json:
        file_name: str = Assay_fileNameFromIdentifier(a_1.Identifier)
        processes: FSharpList[Process] = ARCtrl_ArcTables__ArcTables_GetProcesses(a_1)
        def encoder(oa: OntologyAnnotation, a_1: Any=a_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa)

        encoded_units: tuple[str, Json] = try_include_list("unitCategories", encoder, get_units(processes))
        def encoder_1(value_1: MaterialAttribute, a_1: Any=a_1) -> Json:
            return MaterialAttribute_ISAJson_encoder(id_map, value_1)

        encoded_characteristics: tuple[str, Json] = try_include_list("characteristicCategories", encoder_1, get_characteristics(processes))
        def _arrow1946(ps: FSharpList[Process], a_1: Any=a_1) -> Json:
            return encoder_4(id_map, ps)

        encoded_materials: tuple[str, Json] = try_include("materials", _arrow1946, Option_fromValueWithDefault(empty(), processes))
        def encoder_2(oa_1: Data, a_1: Any=a_1) -> Json:
            return Data_ISAJson_encoder(id_map, oa_1)

        encoced_data_files: tuple[str, Json] = try_include_list("dataFiles", encoder_2, get_data(processes))
        units: FSharpList[OntologyAnnotation] = get_units(processes)
        def chooser(tupled_arg: tuple[str, Json], a_1: Any=a_1) -> tuple[str, Json] | None:
            v: Json = tupled_arg[1]
            if equals(v, Json(3)):
                return None

            else: 
                return (tupled_arg[0], v)


        def _arrow1947(value_5: str, a_1: Any=a_1) -> Json:
            return Json(0, value_5)

        def _arrow1948(oa_2: OntologyAnnotation, a_1: Any=a_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_2)

        def _arrow1949(oa_3: OntologyAnnotation, a_1: Any=a_1) -> Json:
            return OntologyAnnotation_ISAJson_encoder(id_map, oa_3)

        def _arrow1950(value_7: str, a_1: Any=a_1) -> Json:
            return Json(0, value_7)

        def mapping(tp: OntologyAnnotation, a_1: Any=a_1) -> str:
            return JsonTypes_composeTechnologyPlatform(tp)

        def _arrow1952(__unit: None=None, a_1: Any=a_1) -> Callable[[Process], Json]:
            assay_name: str | None = a_1.Identifier
            def _arrow1951(oa_4: Process) -> Json:
                return Process_ISAJson_encoder(study_name, assay_name, id_map, oa_4)

            return _arrow1951

        def _arrow1953(comment: Comment, a_1: Any=a_1) -> Json:
            return Comment_ISAJson_encoder(id_map, comment)

        return Json(5, choose(chooser, of_array([("filename", Json(0, file_name)), try_include("@id", _arrow1947, Assay_ROCrate_genID(a_1)), try_include("measurementType", _arrow1948, a_1.MeasurementType), try_include("technologyType", _arrow1949, a_1.TechnologyType), try_include("technologyPlatform", _arrow1950, map(mapping, a_1.TechnologyPlatform)), encoced_data_files, encoded_materials, encoded_characteristics, encoded_units, try_include_list("processSequence", _arrow1952(), processes), try_include_seq("comments", _arrow1953, a_1.Comments)])))

    if id_map is not None:
        def _arrow1954(a_2: ArcAssay, study_name: Any=study_name, id_map: Any=id_map, a: Any=a) -> str:
            return Assay_ROCrate_genID(a_2)

        return encode(_arrow1954, f, a, id_map)

    else: 
        return f(a)



Assay_ISAJson_allowedFields: FSharpList[str] = of_array(["@id", "filename", "measurementType", "technologyType", "technologyPlatform", "dataFiles", "materials", "characteristicCategories", "unitCategories", "processSequence", "comments", "@type", "@context"])

def _arrow1961(get: IGetters) -> ArcAssay:
    def _arrow1955(__unit: None=None) -> str | None:
        object_arg: IOptionalGetter = get.Optional
        return object_arg.Field("filename", string)

    identifier: str = default_arg(bind(Assay_tryIdentifierFromFileName, _arrow1955()), create_missing_identifier())
    def mapping(arg_4: FSharpList[Process]) -> Array[ArcTable]:
        a: ArcTables = ARCtrl_ArcTables__ArcTables_fromProcesses_Static_62A3309D(arg_4)
        return a.Tables

    def _arrow1956(__unit: None=None) -> FSharpList[Process] | None:
        arg_3: Decoder_1[FSharpList[Process]] = list_1_2(Process_ISAJson_decoder)
        object_arg_1: IOptionalGetter = get.Optional
        return object_arg_1.Field("processSequence", arg_3)

    tables: Array[ArcTable] | None = map(mapping, _arrow1956())
    def _arrow1957(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_2: IOptionalGetter = get.Optional
        return object_arg_2.Field("measurementType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1958(__unit: None=None) -> OntologyAnnotation | None:
        object_arg_3: IOptionalGetter = get.Optional
        return object_arg_3.Field("technologyType", OntologyAnnotation_ISAJson_decoder)

    def _arrow1959(__unit: None=None) -> OntologyAnnotation | None:
        arg_10: Decoder_1[OntologyAnnotation] = map_1(JsonTypes_decomposeTechnologyPlatform, string)
        object_arg_4: IOptionalGetter = get.Optional
        return object_arg_4.Field("technologyPlatform", arg_10)

    def _arrow1960(__unit: None=None) -> Array[Comment] | None:
        arg_12: Decoder_1[Array[Comment]] = Decode_resizeArray(Comment_ISAJson_decoder)
        object_arg_5: IOptionalGetter = get.Optional
        return object_arg_5.Field("comments", arg_12)

    return ArcAssay(identifier, _arrow1957(), _arrow1958(), _arrow1959(), tables, None, None, _arrow1960())


Assay_ISAJson_decoder: Decoder_1[ArcAssay] = Decode_objectNoAdditionalProperties(Assay_ISAJson_allowedFields, _arrow1961)

def ARCtrl_ArcAssay__ArcAssay_fromJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(Assay_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcAssay__ArcAssay_toJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcAssay], str]:
    def _arrow1962(obj: ArcAssay, spaces: Any=spaces) -> str:
        value: Json = Assay_encoder(obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1962


def ARCtrl_ArcAssay__ArcAssay_ToJsonString_71136F3F(this: ArcAssay, spaces: int | None=None) -> str:
    return ARCtrl_ArcAssay__ArcAssay_toJsonString_Static_71136F3F(spaces)(this)


def ARCtrl_ArcAssay__ArcAssay_fromCompressedJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    try: 
        match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(decode(Assay_decoderCompressed), s)
        if match_value.tag == 1:
            raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

        else: 
            return match_value.fields[0]


    except Exception as e_1:
        arg_1: str = str(e_1)
        return to_fail(printf("Error. Unable to parse json string to ArcStudy: %s"))(arg_1)



def ARCtrl_ArcAssay__ArcAssay_toCompressedJsonString_Static_71136F3F(spaces: int | None=None) -> Callable[[ArcAssay], str]:
    def _arrow1963(obj: ArcAssay, spaces: Any=spaces) -> str:
        return to_string(default_arg(spaces, 0), encode_1(Assay_encoderCompressed, obj))

    return _arrow1963


def ARCtrl_ArcAssay__ArcAssay_ToCompressedJsonString_71136F3F(this: ArcAssay, spaces: int | None=None) -> str:
    return ARCtrl_ArcAssay__ArcAssay_toCompressedJsonString_Static_71136F3F(spaces)(this)


def ARCtrl_ArcAssay__ArcAssay_fromROCrateJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(Assay_ROCrate_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcAssay__ArcAssay_toROCrateJsonString_Static_5CABCA47(study_name: str | None=None, spaces: int | None=None) -> Callable[[ArcAssay], str]:
    def _arrow1964(obj: ArcAssay, study_name: Any=study_name, spaces: Any=spaces) -> str:
        value: Json = Assay_ROCrate_encoder(study_name, obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1964


def ARCtrl_ArcAssay__ArcAssay_ToROCrateJsonString_5CABCA47(this: ArcAssay, study_name: str | None=None, spaces: int | None=None) -> str:
    return ARCtrl_ArcAssay__ArcAssay_toROCrateJsonString_Static_5CABCA47(study_name, spaces)(this)


def ARCtrl_ArcAssay__ArcAssay_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[ArcAssay], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1965(obj: ArcAssay, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: Json = Assay_ISAJson_encoder(None, id_map, obj)
        return to_string(default_spaces(spaces), value)

    return _arrow1965


def ARCtrl_ArcAssay__ArcAssay_fromISAJsonString_Static_Z721C83C5(s: str) -> ArcAssay:
    match_value: FSharpResult_2[ArcAssay, str] = Decode_fromString(Assay_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_ArcAssay__ArcAssay_ToISAJsonString_Z3B036AA(this: ArcAssay, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_ArcAssay__ArcAssay_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


__all__ = ["Assay_encoder", "Assay_decoder", "Assay_encoderCompressed", "Assay_decoderCompressed", "Assay_ROCrate_genID", "Assay_ROCrate_encoder", "Assay_ROCrate_decoder", "Assay_ISAJson_encoder", "Assay_ISAJson_allowedFields", "Assay_ISAJson_decoder", "ARCtrl_ArcAssay__ArcAssay_fromJsonString_Static_Z721C83C5", "ARCtrl_ArcAssay__ArcAssay_toJsonString_Static_71136F3F", "ARCtrl_ArcAssay__ArcAssay_ToJsonString_71136F3F", "ARCtrl_ArcAssay__ArcAssay_fromCompressedJsonString_Static_Z721C83C5", "ARCtrl_ArcAssay__ArcAssay_toCompressedJsonString_Static_71136F3F", "ARCtrl_ArcAssay__ArcAssay_ToCompressedJsonString_71136F3F", "ARCtrl_ArcAssay__ArcAssay_fromROCrateJsonString_Static_Z721C83C5", "ARCtrl_ArcAssay__ArcAssay_toROCrateJsonString_Static_5CABCA47", "ARCtrl_ArcAssay__ArcAssay_ToROCrateJsonString_5CABCA47", "ARCtrl_ArcAssay__ArcAssay_toISAJsonString_Static_Z3B036AA", "ARCtrl_ArcAssay__ArcAssay_fromISAJsonString_Static_Z721C83C5", "ARCtrl_ArcAssay__ArcAssay_ToISAJsonString_Z3B036AA"]

