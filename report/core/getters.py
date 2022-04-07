from collections import UserDict

import pandas as pd


path = "data/ooa.ba2223.matching.pdef.xlsx"
PDEF = {
    'ps': pd.read_excel(path, index_col=0),
    'antw': pd.read_excel(path, sheet_name='antw', index_col=0),
}
SPECIFICATIONS = pd.read_excel("data/codings.xlsx").set_index('code')


class Map(UserDict):
    @property
    def values(self):
        return list(self.data.values())

    @property
    def keys(self):
        return list(self.data.keys())

    def __reversed__(self):
        return Map(reversed(tuple(self.data.items())))


def VraagItemsFromPDEF(processtap, /, taal) -> dict:
    """
    Retourneer uit PDEF tekst vraag in `taal` per opgegeven processtap(pen) als
    dict.
    """
    processtap = [processtap] if isinstance(processtap, str) else processtap
    data = PDEF['ps'].set_index('processtap').loc[processtap, f'tekst_{taal}']
    return Map(data.to_dict())



def TitelFromPDEF(processtap, /, taal) -> str:
    return VraagItemsFromPDEF(processtap, taal).values[0]


def VraagItemsQueryFromPDEF(qry, /, taal) -> dict:
    """
    Retourneer uit PDEF tekst vraag in `taal` per via opgegeven query gevonden
    processtap(pen) als dict.
    """
    data = PDEF['ps'].query(qry).set_index('processtap').loc[:, f'tekst_{taal}']
    return Map(data.to_dict())


def AntwItemsFromPDEF(ps, /, taal) -> dict:
    """
    Retourneer voor opgegeven processtap uit PDEF tekst antwoord in `taal` per
    antwoordcode als geordende categorische dict.
    """
    ps = [ps] if isinstance(ps, str) else ps
    data = (
        PDEF['antw']
        .query("processtap in @ps")
        .set_index('antwoord_code')
        .loc[:, f'antwoord_{taal}']
    )
    return Map(data.to_dict())


def VraagItemsFromJSON(key, /, taal) -> dict:
    pass


def AntwItemsFromJSON(key, /, taal) -> dict:
    pass


def VraagItemsFromSPEC(ps, /, taal):
    crit = lambda df: (df.ps == ps) & (df.type == 'Q')
    data= SPECIFICATIONS.loc[crit, taal]
    return Map(data.to_dict())


def AntwItemsFromSPEC(ps, /, taal):
    crit = lambda df: (df.ps == ps) & (df.type == 'A')
    data= SPECIFICATIONS.loc[crit, taal]
    return Map(data.to_dict())
