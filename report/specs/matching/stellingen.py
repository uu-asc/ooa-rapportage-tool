from functools import cache, cached_property

import altair as alt
import pandas as pd

from report.core.spec import Spec
from report.core.source import Source
from report.charts.api import ChartBarNormStack, ChartBarOrdinal
from report.core.getters import (
    VraagItemsQueryFromPDEF,
    AntwItemsFromSPEC,
    TitelFromPDEF,
)


def Conscientieus(data, taal, **props):
    spec = Spec.from_spec(
        'U_STEL_CONSC',
        antwcode='STELLING_EENS',
        titel=TitelFromPDEF('U_STELLING_TOEL', taal),
        labels={'vraag': {'nl': 'eigenschap', 'en': 'trait'}},
        taal=taal
    )
    source = Source(data, spec)
    return ChartBarNormStack(source, spec, **props)


def StellingEens(data, taal, **props):
    ps = 'O_STELLING_TOEL'
    stype = 'AANM_5PUNTS'
    antw = 'STELLING_EENS'
    query = (
        "processtap.str.contains('O_STELLING')"
        f"and systeemlijst_io == '{stype}'"
    )

    spec = Spec(
        vragen = VraagItemsQueryFromPDEF(query, taal),
        antw = AntwItemsFromSPEC(antw, taal),
        titel = TitelFromPDEF(ps, taal),
        taal = taal,
    )
    source = Source(data, spec)
    return ChartBarOrdinal(source, spec, **props)


def StellingPast(data, taal, **props):
    ps = 'O_STELLING_TOE2'
    stype = 'AANM_5PUNTS_B'
    antw = 'STELLING_PAST'
    query = (
        "processtap.str.contains('O_STELLING')"
        f"and systeemlijst_io == '{stype}'"
    )

    spec = Spec(
        vragen = VraagItemsQueryFromPDEF(query, taal),
        antw = AntwItemsFromSPEC(antw, taal),
        titel = TitelFromPDEF(ps, taal),
        taal = taal,
    )
    source = Source(data, spec)
    return ChartBarOrdinal(source, spec, **props)
