from report.core.spec import Spec
from report.core.source import Source
from report.charts.api import ChartPie


def Vooropleiding(data, taal, **props):
    spec = Spec.from_pdef('U_DIPLOMA_BEH', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)


def Profiel(data, taal, **props):
    spec = Spec.from_pdef('U_PROFIEL', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)
