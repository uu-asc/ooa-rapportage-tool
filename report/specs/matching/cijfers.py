from functools import cached_property

import altair as alt
import pandas as pd

from report.core.spec import Spec
from report.core.source import Source
from report.core.chart import Chart
from report.charts.api import ChartBar

from report.core.getters import Map, VraagItemsFromSPEC, TitelFromPDEF, VraagItemsQueryFromPDEF


class HAVO:
    vraag = 'U_HBO_TOEGANG'
    dip = ['HAVO']


class VWO:
    vraag = 'U_DIPLOMA_BEH'
    dip = ['VWO_BEH', 'VWO_NOG_BEH']


class SourceCijfers(Source):
    query = "ooa_id in @ooa_ids and processtap in @self.spec.vragen"

    @property
    def _base(self):
        ooa_ids = self.data.query(
            "processtap == @self.vraag and antwoord in @self.dip"
        ).ooa_id
        base = self.data.query(self.query)
        return self._transform(base)

    def _transform(self, data):
        return super()._transform(data).assign(
            antwoord = lambda df: df.antwoord.map(self.validate_grades).round()
        )

    @cached_property
    def table(self):
        return self._base[['processtap', 'antwoord']].reset_index(drop=True)

    @staticmethod
    def validate_grades(x):
        """
        Return text as number or NaN if conversion fails.
        - Numbers larger than 100 are discarded.
        - Numbers between 10 and 100 are normalized to 1-10 range.
        - Numbers lower than a 4 are discarded.
        """
        x = pd.to_numeric(x, errors='coerce')
        if x > 100:
            return pd.NA
        if x > 10:
            return x / 10
        if x < 4:
            return pd.NA
        return x


class SourceCijfersHAVO(SourceCijfers, HAVO):
    pass


class SourceCijfersVWO(SourceCijfers, VWO):
    pass


class ChartCijfers(Chart):
    def _transform(self, base):
        return base.transform_joinaggregate(
            totaal='count()',
            groupby=['processtap']
        ).transform_bin(
            as_='binned',
            bin= alt.BinParams(extent=[4,10], step=1),
            field='antwoord'
        ).transform_joinaggregate(
            mean='mean(antwoord)',
            groupby=['processtap']
        ).transform_joinaggregate(
            bincount ='count()',
            groupby=['processtap', 'binned_end']
        ).transform_calculate(
            pct = 'datum.bincount / datum.totaal'
        )

    @property
    def _tooltip(self):
        return [
            alt.Tooltip('processtap:N', title=self.spec.labels['vraag']),
            alt.Tooltip('antwoord:N', title=self.spec.labels['antwoord']),
            alt.Tooltip('totaal:Q', title=self.spec.labels['totaal']),
            alt.Tooltip('count():Q', title=self.spec.labels['aantal']),
            alt.Tooltip('pct:Q', title=self.spec.labels['pct'], format='.0%'),
        ]

    def _chart(self):
        base = self._base
        bar = base.mark_bar().encode(
            x=alt.X('binned:Q', title='cijfer', axis=alt.Axis(tickMinStep=1)),
            x2='binned_end:Q',
            y=alt.Y('count():Q', title='aantal', axis=alt.Axis(tickMinStep=1)),
            tooltip=self._tooltip
        )
        rule = base.mark_rule(color='red', strokeDash=[15,5]).encode(
            x=alt.X('mean:Q'),
            size=alt.value(5),
            tooltip=[
                alt.Tooltip('processtap', title=self.spec.labels['vraag']),
                alt.Tooltip(
                    'mean:Q',
                    title=self.spec.labels['gemiddelde'],
                    format='.1f',
                )
            ],
        )
        return alt.layer(bar, rule).facet(
                alt.Facet('processtap:N'),
                columns=2
            ).resolve_axis(x='independent')


def GrafiekHAVO(data, taal, **props):
    query = (
        "processtap.str.contains('[OU]_CIJF_(?!TOEL.*$).*')"
    )
    antw = Map({
        4:  '4',
        5:  '5',
        6:  '6',
        7:  '7',
        8:  '8',
        9:  '9',
        10: '10',
    })
    spec = Spec(
        vragen = VraagItemsQueryFromPDEF(query, taal),
        titel = TitelFromPDEF('U_CIJF_TOEL3', taal),
        antw = antw,
        taal = taal,
    )
    source = SourceCijfersHAVO(data, spec)
    return ChartCijfers(source, spec, **props)


def GrafiekVWO(data, taal, **props):
    query = (
        "processtap.str.contains('[OU]_CIJF_(?!TOEL.*$).*')"
    )
    antw = Map({
        4:  '4',
        5:  '5',
        6:  '6',
        7:  '7',
        8:  '8',
        9:  '9',
        10: '10',
    })
    spec = Spec(
        vragen = VraagItemsQueryFromPDEF(query, taal),
        titel = TitelFromPDEF('O_CIJF_TOEL4', taal),
        antw = antw,
        taal = taal,
    )
    source = SourceCijfersVWO(data, spec)
    return ChartCijfers(source, spec, **props)


def TabelHAVO(data, taal, **props):
    query = (
        "processtap.str.contains('[OU]_CIJF_(?!TOEL.*$).*')"
    )
    antw = Map({
        4:  '4',
        5:  '5',
        6:  '6',
        7:  '7',
        8:  '8',
        9:  '9',
        10: '10',
    })
    spec = Spec(
        vragen = VraagItemsQueryFromPDEF(query, taal),
        titel = {
            'nl': 'Overzicht havo-cijfers',
            'en': 'Overview havo-grades'
        }[taal],
        antw = antw,
        taal = taal,
    )
    source = SourceCijfersHAVO(data, spec)
    return spec, (
        source._base
        .groupby('processtap')
        .antwoord
        .agg(['count', 'mean', 'min', 'max'])
        .assign(mean = lambda df: df['mean'].round(1))
        .dropna()
        .astype({'min': int, 'max': int})
        .rename_axis(index=None, columns=spec.labels['vraag'])
        .rename(
            columns={'count': 'n', 'mean': spec.labels['gemiddelde']},
            index=spec.vragen)
    )


def TabelVWO(data, taal, **props):
    query = (
        "processtap.str.contains('[OU]_CIJF_(?!TOEL.*$).*')"
    )
    antw = Map({
        4:  '4',
        5:  '5',
        6:  '6',
        7:  '7',
        8:  '8',
        9:  '9',
        10: '10',
    })
    spec = Spec(
        vragen = VraagItemsQueryFromPDEF(query, taal),
        titel = {
            'nl': 'Overzicht vwo-cijfers',
            'en': 'Overview vwo-grades'
        }[taal],
        antw = antw,
        taal = taal,
    )
    source = SourceCijfersVWO(data, spec)
    return spec, (
        source._base
        .groupby('processtap')
        .antwoord
        .agg(['count', 'mean', 'min', 'max'])
        .assign(mean = lambda df: df['mean'].round(1))
        .dropna()
        .astype({'min': int, 'max': int})
        .rename_axis(index=None, columns=spec.labels['vraag'])
        .rename(
            columns={'count': 'n', 'mean': spec.labels['gemiddelde']},
            index=spec.vragen)
    )
