from report.core.spec import Spec
from report.core.source import Source
from report.charts.api import ChartPie


def Honours(data, taal, **props):
    spec = Spec.from_pdef('U_INTERESSE_HON', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)

def ExtraExamenVak(data, taal, **props):
    spec = Spec.from_pdef('O_EXTRA EXVAK', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)

def Plusprogramma(data, taal, **props):
    spec = Spec.from_pdef('O_PLUSPROGRAMMA', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)

def ExtraActiviteit(data, taal, **props):
    spec = Spec.from_pdef('O_EXTRA_ACTIVIT', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)

def Verdiepen(data, taal, **props):
    spec = Spec.from_pdef('O_VERDIEPEN', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)
