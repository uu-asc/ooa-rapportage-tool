from uuid import uuid4
from functools import cached_property

import pandas as pd

from report.core.getters import (
    VraagItemsFromPDEF,
    VraagItemsFromSPEC,
    TitelFromPDEF,
    AntwItemsFromPDEF,
    AntwItemsFromSPEC,
)


LABELS = {
    'vraag': {'nl': 'vraag', 'en': 'question'},
    'antwoord': {'nl': 'antwoord', 'en': 'answer'},
    'aantal': {'nl': 'aantal', 'en': 'count'},
    'totaal': {'nl': 'totaal', 'en': 'total'},
    'pct': {'nl': 'percentage', 'en': 'percentage'},
    'gemiddelde': {'nl': 'gem.', 'en': 'mean'},
    'ja': {'nl': 'ja', 'en': 'yes'},
    'nee': {'nl': 'nee', 'en': 'no'},
}


class Spec:
    def __init__(self, vragen, antw, taal, titel=None, labels=None):
        labels = {} if labels is None else labels
        self.uuid = f'uuid-{uuid4()}'
        self.vragen = vragen
        self.antw = antw
        self.titel = titel
        self.labels = {
            **{k:v[taal] for k,v in LABELS.items()},
            **{k:v[taal] for k,v in labels.items()},
        }
        self.taal = taal

    @classmethod
    def from_pdef(cls, ps, /, taal, titel=None, labels=None):
        antw = AntwItemsFromPDEF(ps, taal)
        vragen = VraagItemsFromPDEF(ps, taal)
        titel = vragen.values[0] if titel is None else titel
        return cls(vragen, antw, taal, titel=titel, labels=labels)

    @classmethod
    def from_spec(cls, ps, /, taal, antwcode=None, titel=None, labels=None):
        antwcode = ps if antwcode is None else antwcode
        antw = AntwItemsFromSPEC(antwcode, taal)
        vragen = VraagItemsFromSPEC(ps, taal)
        titel = TitelFromPDEF(ps, taal) if titel is None else titel
        return cls(vragen, antw, taal, titel=titel, labels=labels)
