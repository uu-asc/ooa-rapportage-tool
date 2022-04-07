from functools import cached_property

import altair as alt

from report.core.chart import Chart


class ChartBarNormStack(Chart):
    @cached_property
    def _sort_y(self):
        return (
            self.source.table
            .sort_values(self.spec.antw.values[:2], ascending=False)
            .index.values
        )

    def _chart(self):
        return self._base.mark_bar().encode(
            x = alt.X(
                'pct:Q',
                axis=alt.Axis(format='.0%'),
                title=self.spec.labels['pct'],
            ),
            y = alt.Y(
                'processtap:N',
                sort=list(self._sort_y),
                title=self.spec.labels['vraag'],
            ),
            color = alt.Color(
                'antwoord:O',
                sort=self.spec.antw.values,
                scale=alt.Scale(domain=self.spec.antw.values),
                title=self.spec.labels['antwoord']),
            order=alt.Order(
                'color_antwoord_sort_index:Q',
                sort='ascending'),
            tooltip=self._tooltip
        )
