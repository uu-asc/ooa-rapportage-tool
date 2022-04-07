from functools import cached_property


class Source:
    """
    Brondata.
    Vertaalt en ordent vraag en antwoorden volgens `spec`.
    """
    query : str = "processtap in @self.spec.vragen"

    def __init__(self, data, spec):
        self.data = data
        self.spec = spec

    @property
    def _base(self):
        base = self.data.query(self.query)
        return self._transform(base)

    def _transform(self, data):
        return (
            data
            .replace({
                'processtap': self.spec.vragen,
                'antwoord': self.spec.antw})
        )

    @cached_property
    def table(self):
        if self._base.empty:
            return None
        cols = [
            col for col in self.spec.antw.values
            if col in self._base.antwoord.values]
        return (
            self._base
            .pivot_table(
                index='processtap',
                columns='antwoord',
                aggfunc='size')
            [cols] # order columns
        )

    @classmethod
    def from_processtap(cls, data, spec):
        source = cls(data, spec)
        source.query = "processtap in @self.spec.vragen"
        return source
