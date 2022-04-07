from functools import cached_property

import pandas as pd

from report.core.spec import Spec
from report.core.source import Source
from report.charts.api import ChartBar

from report.core.getters import Map, VraagItemsFromSPEC, TitelFromPDEF


class SourceTijdsbesteding(Source):
    @cached_property
    def table(self):
        if self._base.empty:
            return None
        breaks = [0, 5, 10, 15, 20, 25, 30, 100]
        to_float = lambda i: float(i.replace(',', '.'))
        return (
            self._base
            .assign(
                antwoord = lambda df: pd.cut(
                    df.antwoord.apply(to_float),
                    bins=breaks,
                    labels=self.spec.antw.values))
            .replace({'processtap': self.spec.vragen})
            .pivot_table(
                index = 'processtap',
                columns = 'antwoord',
                aggfunc = 'size')
        )


def TijdsbestedingSchool(data, taal, **props):
    ps = 'O_SCHOOLWK_TOE'
    labels = {
        'vraag': {'nl': 'tijdsbesteding', 'en': 'time use'},
        'antwoord': {'nl': 'aantal uur', 'en': 'time in hours'},
    }
    antw = Map({
        0: '| 0-5 )',
        1: '| 5-10 )',
        2: '| 10-15 )',
        3: '| 15-20 )',
        4: '| 20-25 )',
        5: '| 25-30 )',
        6: '| 30+',
    })
    spec = Spec(
        titel = TitelFromPDEF(ps, taal),
        vragen = VraagItemsFromSPEC(ps, taal),
        antw = antw,
        labels = labels,
        taal = taal)
    source = SourceTijdsbesteding(data, spec)
    return ChartBar(source, spec, **props)


def TijdsbestedingStudie(data, taal, **props):
    ps = 'U_STUDIEWK_TOEL'
    labels = {
        'vraag': {'nl': 'tijdsbesteding', 'en': 'time use'},
        'antwoord': {'nl': 'aantal uur', 'en': 'time in hours'},
    }
    antw = Map({
        0: '| 0-5 )',
        1: '| 5-10 )',
        2: '| 10-15 )',
        3: '| 15-20 )',
        4: '| 20-25 )',
        5: '| 25-30 )',
        6: '| 30+',
    })
    spec = Spec(
        titel = TitelFromPDEF(ps, taal),
        vragen = VraagItemsFromSPEC(ps, taal),
        antw = antw,
        labels = labels,
        taal = taal)
    source = SourceTijdsbesteding(data, spec)
    return ChartBar(source, spec, **props)
