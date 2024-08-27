from __future__ import annotations
from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.list import of_array
from ...fable_modules.fable_library.option import default_arg
from ...fable_modules.fable_library.result import FSharpResult_2
from ...fable_modules.fable_library.string_ import (to_text, printf)
from ...fable_modules.thoth_json_core.decode import (one_of, map)
from ...fable_modules.thoth_json_core.types import (Json, Decoder_1)
from ...fable_modules.thoth_json_python.decode import Decode_fromString
from ...fable_modules.thoth_json_python.encode import to_string
from ...Core.data import Data
from ...Core.Process.material import Material
from ...Core.Process.process_input import ProcessInput
from ...Core.Process.sample import Sample
from ...Core.Process.source import Source
from ..data import (Data_ROCrate_encoder, Data_ROCrate_decoder, Data_ISAJson_encoder, Data_ISAJson_decoder)
from ..encode import default_spaces
from .material import (Material_ROCrate_encoder, Material_ROCrate_decoder, Material_ISAJson_encoder, Material_ISAJson_decoder)
from .sample import (Sample_ROCrate_encoder, Sample_ROCrate_decoder, Sample_ISAJson_encoder, Sample_ISAJson_decoder)
from .source import (Source_ROCrate_encoder, Source_ROCrate_decoder, Source_ISAJson_encoder, Source_ISAJson_decoder)

def ProcessInput_ROCrate_encoder(value: ProcessInput) -> Json:
    if value.tag == 1:
        return Sample_ROCrate_encoder(value.fields[0])

    elif value.tag == 2:
        return Data_ROCrate_encoder(value.fields[0])

    elif value.tag == 3:
        return Material_ROCrate_encoder(value.fields[0])

    else: 
        return Source_ROCrate_encoder(value.fields[0])



def _arrow1703(Item: Source) -> ProcessInput:
    return ProcessInput(0, Item)


def _arrow1704(Item_1: Sample) -> ProcessInput:
    return ProcessInput(1, Item_1)


def _arrow1705(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow1706(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ProcessInput_ROCrate_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow1703, Source_ROCrate_decoder), map(_arrow1704, Sample_ROCrate_decoder), map(_arrow1705, Data_ROCrate_decoder), map(_arrow1706, Material_ROCrate_decoder)]))

def ProcessInput_ISAJson_encoder(id_map: Any | None, value: ProcessInput) -> Json:
    if value.tag == 1:
        return Sample_ISAJson_encoder(id_map, value.fields[0])

    elif value.tag == 2:
        return Data_ISAJson_encoder(id_map, value.fields[0])

    elif value.tag == 3:
        return Material_ISAJson_encoder(id_map, value.fields[0])

    else: 
        return Source_ISAJson_encoder(id_map, value.fields[0])



def _arrow1708(Item: Source) -> ProcessInput:
    return ProcessInput(0, Item)


def _arrow1709(Item_1: Sample) -> ProcessInput:
    return ProcessInput(1, Item_1)


def _arrow1710(Item_2: Data) -> ProcessInput:
    return ProcessInput(2, Item_2)


def _arrow1711(Item_3: Material) -> ProcessInput:
    return ProcessInput(3, Item_3)


ProcessInput_ISAJson_decoder: Decoder_1[ProcessInput] = one_of(of_array([map(_arrow1708, Source_ISAJson_decoder), map(_arrow1709, Sample_ISAJson_decoder), map(_arrow1710, Data_ISAJson_decoder), map(_arrow1711, Material_ISAJson_decoder)]))

def ARCtrl_Process_ProcessInput__ProcessInput_fromISAJsonString_Static_Z721C83C5(s: str) -> ProcessInput:
    match_value: FSharpResult_2[ProcessInput, str] = Decode_fromString(ProcessInput_ISAJson_decoder, s)
    if match_value.tag == 1:
        raise Exception(to_text(printf("Error decoding string: %O"))(match_value.fields[0]))

    else: 
        return match_value.fields[0]



def ARCtrl_Process_ProcessInput__ProcessInput_toISAJsonString_Static_Z3B036AA(spaces: int | None=None, use_idreferencing: bool | None=None) -> Callable[[ProcessInput], str]:
    id_map: Any | None = dict([]) if default_arg(use_idreferencing, False) else None
    def _arrow1712(f: ProcessInput, spaces: Any=spaces, use_idreferencing: Any=use_idreferencing) -> str:
        value: Json = ProcessInput_ISAJson_encoder(id_map, f)
        return to_string(default_spaces(spaces), value)

    return _arrow1712


def ARCtrl_Process_ProcessInput__ProcessInput_ToISAJsonString_Z3B036AA(this: ProcessInput, spaces: int | None=None, use_idreferencing: bool | None=None) -> str:
    return ARCtrl_Process_ProcessInput__ProcessInput_toISAJsonString_Static_Z3B036AA(spaces, use_idreferencing)(this)


__all__ = ["ProcessInput_ROCrate_encoder", "ProcessInput_ROCrate_decoder", "ProcessInput_ISAJson_encoder", "ProcessInput_ISAJson_decoder", "ARCtrl_Process_ProcessInput__ProcessInput_fromISAJsonString_Static_Z721C83C5", "ARCtrl_Process_ProcessInput__ProcessInput_toISAJsonString_Static_Z3B036AA", "ARCtrl_Process_ProcessInput__ProcessInput_ToISAJsonString_Z3B036AA"]

