from functools import cached_property
from textwrap import wrap

import altair as alt

from report.core.chart import Chart


class ChartBar(Chart):
    preprocessing = [
        lambda df: df.assign(processtap = df.processtap.apply(wrap)),
    ]

    def _chart(self):
        base = self._base.mark_bar().encode(
            x = alt.X(
                'pct:Q',
                axis=alt.Axis(format='.0%'),
                title=self.spec.labels['pct'],
            ),
            y = alt.Y(
                'antwoord:O',
                sort=self.spec.antw.values,
                title=self.spec.labels['antwoord']),
            tooltip=self._tooltip,
            **self.modifiers
        )
        text = base.mark_text(dx=7).encode(
            text = 'aantal:Q',
            opacity = alt.condition(
                'datum.aantal < 1',
                alt.value(0),
                alt.value(1),
            ),
        )
        return alt.layer(base, text).facet(
            alt.Facet('processtap:N', title=self.spec.labels['vraag']),
            columns=1
        ).resolve_scale(x='independent')


class ChartBarOrdinal(ChartBar):
    @property
    def modifiers(self):
        return {
            'color': alt.Color(
                'antwoord:O',
                sort=self.spec.antw.values,
                scale=alt.Scale(domain=self.spec.antw.values),
                title=self.spec.labels['antwoord']),
            'order': alt.Order(
                'color_antwoord_sort_index:Q',
                sort='ascending'),
        }
