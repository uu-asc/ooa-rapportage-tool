from functools import cached_property

from report.core.spec import Spec
from report.core.source import Source
from report.core.getters import Map
from report.charts.api import ChartBarNormStack, ChartPie


class SourceFactoren(Source):
    query = "processtap == 'U_FACTOREN'"

    @cached_property
    def table(self):
        return (
            self._base
            .assign(antwoord = lambda df: df.antwoord.str.split('|'))
            .explode('antwoord')
            .antwoord.value_counts()
            .rename_axis('processtap')
            .rename('ja')
            .to_frame()
            .assign(
                nee = lambda df: self._base.studentnummer.nunique() - df.ja)
            .rename(
                index=self.spec.vragen,
                columns=self.spec.labels)
        )


def StudiekeuzeMiddel(data, taal, **props):
    labels={'vraag': {'nl': 'middel', 'en': 'tool/activity'}}
    spec = Spec.from_spec('U_ACTIV_MIDDEL', taal=taal, labels=labels)
    spec.antw = reversed(spec.antw)
    source = Source(data, spec)
    return ChartBarNormStack(source, spec, **props)


def EersteKeus(data, taal, **props):
    spec = Spec.from_pdef('U_EERSTEKEUZE', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)


def StudiekeuzeFactoren(data, taal, **props):
    labels={'vraag': {'nl': 'factor', 'en': 'factor'}}
    spec = Spec.from_spec('U_FACTOREN', taal=taal, labels=labels)
    source = SourceFactoren(data, spec)
    return ChartBarNormStack(source, spec, **props)


def TrackLITB(data, taal, **props):
    spec = Spec.from_pdef('O_TRACK_LITB', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)


def TrackTHEB(data, taal, **props):
    spec = Spec.from_pdef('O_TRACK_THEB', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)


def TrackTLWB(data, taal, **props):
    spec = Spec.from_pdef('O_TRACK_TLWB', taal)
    source = Source(data, spec)
    return ChartPie(source, spec, **props)


class SourceBeroep(Source):
    query = "processtap == 'O_BEROEP'"

    @property
    def table(self):
        if self._base.empty:
            return None
        return (
            self._base
            .assign(antwoord = lambda df: df.antwoord.str.split('|'))
            .explode('antwoord')
            .antwoord.value_counts()
            .rename_axis('processtap')
            .rename('ja')
            .to_frame()
            .assign(
                nee = lambda df: self._base.studentnummer.nunique() - df.ja)
            .rename(
                index=self.spec.vragen,
                columns=self.spec.labels)
        )


def OverigBeroep(data, taal, **props):
    labels={'vraag': {'nl': 'beroep', 'en': 'profession'}}
    spec = Spec.from_pdef('O_BEROEP', taal=taal, labels=labels)
    spec.vragen = spec.antw
    spec.antw = Map({'ja': 'ja', 'nee': 'nee'})
    source = SourceBeroep(data, spec)
    return ChartBarNormStack(source, spec, **props)
