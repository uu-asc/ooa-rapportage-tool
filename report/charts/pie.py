import altair as alt

from report.core.chart import Chart


class ChartPie(Chart):
    def _chart(self):
        base = self._base.encode(
            theta=alt.Theta(
                field='aantal',
                stack=True,
                type='quantitative'),
            color=alt.Color(
                field='antwoord',
                type='nominal',
                scale=alt.Scale(domain=self.spec.antw.values),
                title=self.spec.labels['antwoord']),
            order=alt.Order('aantal:Q', sort='descending'),
            tooltip=self._tooltip
        )
        pie = base.mark_arc(innerRadius=60, outerRadius=120)
        percs = base.mark_text(radius=90).encode(
            text=alt.Text('pct:Q', title=self.spec.labels['pct'], format='.0%'),
            color=alt.value('white')
        )
        return pie + percs
