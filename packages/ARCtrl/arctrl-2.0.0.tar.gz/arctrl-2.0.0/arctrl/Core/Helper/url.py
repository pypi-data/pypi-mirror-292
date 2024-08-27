from collections.abc import Callable
from typing import Any
from ...fable_modules.fable_library.util import to_enumerable
from .collections_ import (Dictionary_ofSeq, Dictionary_tryFind)

def OntobeeParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "http://purl.obolibrary.org/obo/") + "") + tsr) + "_") + local_tan) + ""


def BioregistryParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://bioregistry.io/") + "") + tsr) + ":") + local_tan) + ""


def OntobeeDPBOParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "http://purl.org/nfdi4plants/ontology/dpbo/") + "") + tsr) + "_") + local_tan) + ""


def MSParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/ms/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def POParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/po/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def ROParser(tsr: str, local_tan: str) -> str:
    return ((((("" + "https://www.ebi.ac.uk/ols4/ontologies/ro/classes/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F") + "") + tsr) + "_") + local_tan) + ""


def _arrow399(tsr: str) -> Callable[[str], str]:
    def _arrow398(local_tan: str) -> str:
        return OntobeeDPBOParser(tsr, local_tan)

    return _arrow398


def _arrow401(tsr_1: str) -> Callable[[str], str]:
    def _arrow400(local_tan_1: str) -> str:
        return MSParser(tsr_1, local_tan_1)

    return _arrow400


def _arrow403(tsr_2: str) -> Callable[[str], str]:
    def _arrow402(local_tan_2: str) -> str:
        return POParser(tsr_2, local_tan_2)

    return _arrow402


def _arrow405(tsr_3: str) -> Callable[[str], str]:
    def _arrow404(local_tan_3: str) -> str:
        return ROParser(tsr_3, local_tan_3)

    return _arrow404


def _arrow407(tsr_4: str) -> Callable[[str], str]:
    def _arrow406(local_tan_4: str) -> str:
        return BioregistryParser(tsr_4, local_tan_4)

    return _arrow406


def _arrow409(tsr_5: str) -> Callable[[str], str]:
    def _arrow408(local_tan_5: str) -> str:
        return BioregistryParser(tsr_5, local_tan_5)

    return _arrow408


def _arrow411(tsr_6: str) -> Callable[[str], str]:
    def _arrow410(local_tan_6: str) -> str:
        return BioregistryParser(tsr_6, local_tan_6)

    return _arrow410


def _arrow413(tsr_7: str) -> Callable[[str], str]:
    def _arrow412(local_tan_7: str) -> str:
        return BioregistryParser(tsr_7, local_tan_7)

    return _arrow412


def _arrow415(tsr_8: str) -> Callable[[str], str]:
    def _arrow414(local_tan_8: str) -> str:
        return BioregistryParser(tsr_8, local_tan_8)

    return _arrow414


def _arrow417(tsr_9: str) -> Callable[[str], str]:
    def _arrow416(local_tan_9: str) -> str:
        return BioregistryParser(tsr_9, local_tan_9)

    return _arrow416


def _arrow419(tsr_10: str) -> Callable[[str], str]:
    def _arrow418(local_tan_10: str) -> str:
        return BioregistryParser(tsr_10, local_tan_10)

    return _arrow418


def _arrow421(tsr_11: str) -> Callable[[str], str]:
    def _arrow420(local_tan_11: str) -> str:
        return BioregistryParser(tsr_11, local_tan_11)

    return _arrow420


def _arrow423(tsr_12: str) -> Callable[[str], str]:
    def _arrow422(local_tan_12: str) -> str:
        return BioregistryParser(tsr_12, local_tan_12)

    return _arrow422


def _arrow425(tsr_13: str) -> Callable[[str], str]:
    def _arrow424(local_tan_13: str) -> str:
        return BioregistryParser(tsr_13, local_tan_13)

    return _arrow424


def _arrow427(tsr_14: str) -> Callable[[str], str]:
    def _arrow426(local_tan_14: str) -> str:
        return BioregistryParser(tsr_14, local_tan_14)

    return _arrow426


uri_parser_collection: Any = Dictionary_ofSeq(to_enumerable([("DPBO", _arrow399), ("MS", _arrow401), ("PO", _arrow403), ("RO", _arrow405), ("ENVO", _arrow407), ("CHEBI", _arrow409), ("GO", _arrow411), ("OBI", _arrow413), ("PATO", _arrow415), ("PECO", _arrow417), ("TO", _arrow419), ("UO", _arrow421), ("EFO", _arrow423), ("NCIT", _arrow425), ("OMP", _arrow427)]))

def create_oauri(tsr: str, local_tan: str) -> str:
    match_value: Callable[[str, str], str] | None = Dictionary_tryFind(tsr, uri_parser_collection)
    if match_value is None:
        return OntobeeParser(tsr, local_tan)

    else: 
        return match_value(tsr)(local_tan)



__all__ = ["OntobeeParser", "BioregistryParser", "OntobeeDPBOParser", "MSParser", "POParser", "ROParser", "uri_parser_collection", "create_oauri"]

