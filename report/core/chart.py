import altair as alt


class Chart:
    """
    Visualiseer data als vega-lite grafiek.
    """
    preprocessing = []
    modifiers = {}

    def __init__(self, source, spec, **props):
        self.source = source
        self.spec = spec
        self.props = props

    @property
    def _base(self):
        source = self.source.table.reset_index()
        for f in self.preprocessing:
            source = source.pipe(f)
        base = alt.Chart(source)
        return self._transform(base)

    def _transform(self, base):
        vraag_transform = (
            "isArray(datum.processtap) "
            "? join(datum.processtap, ' ') "
            ": datum.processtap"
        )
        return base.transform_fold(
            as_=['antwoord', 'aantal'],
            fold=self.spec.antw.values,
        ).transform_joinaggregate(
            totaal='sum(aantal)',
            groupby=['processtap'],
        ).transform_calculate(
            pct='datum.aantal / datum.totaal',
            vraag=vraag_transform,
        )

    @property
    def _tooltip(self):
        return [
            alt.Tooltip('vraag:N', title=self.spec.labels['vraag']),
            alt.Tooltip('antwoord:N', title=self.spec.labels['antwoord']),
            alt.Tooltip('totaal:Q', title=self.spec.labels['totaal']),
            alt.Tooltip('aantal:Q', title=self.spec.labels['aantal']),
            alt.Tooltip('pct:Q', title=self.spec.labels['pct'], format='.0%'),
        ]

    def _chart(self):
        pass

    def _apply_props(self, chart, **props):
        """
        Top-level configuratie van grafiek via `props`.
        Zie https://altair-viz.github.io/user_guide/configuration.html
        """
        props = {**self.props, **props}
        for key, props in props.items():
            chart = getattr(chart, key)(**props)
        return chart

    def chart(self):
        if self.source.table is None:
            return None
        return self._apply_props(self._chart())
