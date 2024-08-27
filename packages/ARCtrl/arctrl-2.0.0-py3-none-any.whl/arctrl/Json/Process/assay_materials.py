from __future__ import annotations
from typing import Any
from ...fable_modules.fable_library.list import (FSharpList, choose, of_array)
from ...fable_modules.fable_library.util import equals
from ...fable_modules.thoth_json_core.types import Json
from ...Core.Process.material import Material
from ...Core.Process.process import Process
from ...Core.Process.process_sequence import (get_samples, get_materials)
from ...Core.Process.sample import Sample
from ..encode import try_include_list
from .material import Material_ISAJson_encoder
from .sample import Sample_ISAJson_encoder

def encoder(id_map: Any | None, ps: FSharpList[Process]) -> Json:
    samples: FSharpList[Sample] = get_samples(ps)
    materials: FSharpList[Material] = get_materials(ps)
    def chooser(tupled_arg: tuple[str, Json], id_map: Any=id_map, ps: Any=ps) -> tuple[str, Json] | None:
        v: Json = tupled_arg[1]
        if equals(v, Json(3)):
            return None

        else: 
            return (tupled_arg[0], v)


    def _arrow1727(oa: Sample, id_map: Any=id_map, ps: Any=ps) -> Json:
        return Sample_ISAJson_encoder(id_map, oa)

    def _arrow1728(c: Material, id_map: Any=id_map, ps: Any=ps) -> Json:
        return Material_ISAJson_encoder(id_map, c)

    return Json(5, choose(chooser, of_array([try_include_list("samples", _arrow1727, samples), try_include_list("otherMaterials", _arrow1728, materials)])))


__all__ = ["encoder"]

