from pathlib import Path
import datetime as dt
import numpy as np
import pandas as pd

import sys
sys.path.insert(0, '../../../osiris_query')
from query.result import QueryResult


# name_procesdef = 'procesdefinitie_BA1920_MATCHING_PRD.xlsx'
name_procesdef = 'ooa.ba2122.matching.pdef.xlsx'

# templates
TEMPLATE_PATH = Path('templates')
OUTPUT_PATH = Path('output')
BODY_PATH = TEMPLATE_PATH / 'template_body.html'
SPEC_PATH = TEMPLATE_PATH / 'template_spec.html'
CSS_PATH = TEMPLATE_PATH / 'template_css.css'
BODY = BODY_PATH.read_text()
SPEC = SPEC_PATH.read_text()
CSS = CSS_PATH.read_text()

# faculties
faculties = {
    'BETA': [
        'BIOL', 'INCA', 'WSKT', 'SCHK', 'WISK',
        'INKU', 'NAST',
    ],
    'GEO': ['INMB', 'SGPB', 'AARD'],
    'GW': [
        'ISAB', 'WBGB', 'LITB', 'TCSB', 'HISB',
        'CIWB', 'ENGB', 'THEB', 'GESB', 'LASB',
        'FRAB', 'KUNB', 'TLWB', 'SPAB', 'DUIB',
        'NEDB', 'MUZB', 'KELB', 'ITAB', 'THEO',
    ],
    'ECBB': ['ECBB'],
    'RGLB': ['RGLB'],
    'SW': ['ASWB', 'PEDB', 'SOCB', 'OWKB', 'CULB'],
}


def load_forms(df, matching_dates, programmes):
    """
    Return forms relevant to specified matching dates and programmes.

    Parameters
    ==========
    :param matching_dates: {str or list}
        Matching dates to be selected.
    :param programmes: {str or list}
        Programmes to be selected.

    Returns
    =======
    :load_forms: DataFrame
    """

    if not isinstance(matching_dates, list):
        matching_dates = [matching_dates]
    if not isinstance(programmes, list):
        programmes = [programmes]

    df.columns = [col.upper() for col in df.columns]
    df = df.rename(columns={'OOA_ID': 'IO_AANVR_ID'})
    cols = [
        'PROCESSTAP',
        'SYSTEEM_ANTWOORD_CODE',
        'GESLOTEN_ANTWOORD_CODE',
        'OPEN_ANTWOORD_STUDENT',
    ]
    df = df.astype(
        dtype={col:'str' for col in cols}
        ).replace('nan', np.nan)
    cols = [
        'SYSTEEM_ANTWOORD_CODE',
        'GESLOTEN_ANTWOORD_CODE',
        'OPEN_ANTWOORD_STUDENT',
    ]
    df['ANTWOORD'] = df['SYSTEEM_ANTWOORD_CODE']\
        .fillna(df['GESLOTEN_ANTWOORD_CODE'])\
        .fillna(df['OPEN_ANTWOORD_STUDENT'])
    df = df.drop(cols, axis=1)

    filt1 = df['PROCESSTAP'].str.contains('O_DATUM_')
    filt2 = df['ANTWOORD'].isin(matching_dates)
    forms = list(df.loc[filt1 & filt2]['IO_AANVR_ID'].unique())

    filt1 = df['IO_AANVR_ID'].isin(forms)
    filt2 = df['OPLEIDING'].isin(programmes)

    df = df.loc[filt1 & filt2]
    return df


# def load_ps(file, lang):
#     file = Path(file)
#     lang_colname = {'nl': 'tekst_nl', 'en': 'tekst_en'}
#     df = pd.read_excel(file, index_col=0, sheet_name='ps')
#     df = df.query("actor == 'S'").set_index('processtap')
#     df['TEKST'] = df[lang_colname[lang]]
#     return df


def load_ps(file, lang):
    file = Path(file)
    lang_colname = {'nl': 'tekst_nl', 'en': 'tekst_en'}
    df = pd.read_excel(
        file,
        index_col=0,
        header=3,
        skiprows=[4],
        sheet_name='opl'
    ).rename(columns={
        ' .1': 'actor',
        ' .2': 'hoofdstuk',
        ' .3': 'hs_nr',
        ' .4': 'processtap',
        ' .5': 'ps_nr',
        ' .6': 'tekst_nl',
        ' .7': 'tekst_en',
        ' .8': 'SYSTEEMLIJST_IO',
        'opleiding': 'actueel',
        'Unnamed: 50': 'aantal',
    })
    df = df.query("actor == 'S'").set_index('processtap')
    df['TEKST'] = df[lang_colname[lang]]
    return df


def load_antw(file, lang):
    lang_colname = {'nl': 'antwoord_nl', 'en': 'antwoord_en'}
    df = pd.read_excel(file, sheet_name='antw')
    cols = [
        'hoofdstuk',
        'processtap',
        'volgnummer',
        'antwoord_code',
        'antwoord_nl',
        'antwoord_en',
    ]
    df = df.query("actor == 'S'")[cols
    ].set_index(['processtap', 'antwoord_code'])
    df['ANTWOORD'] = df[lang_colname[lang]]
    return df


def load_prog(lang):
    lang_colname = {'nl': 'NAAM_NL', 'en': 'NAAM_EN'}
    df = QueryResult.read_pickle('referentie/ref_OST_OPLEIDING').frame
    df.columns = [col.upper() for col in df.columns]
    df = df.set_index('OPLEIDING')
    df['NAAM'] = df[lang_colname[lang]]
    return df


def load_codings(lang):
    lang_colname = {'nl': 'NL', 'en': 'EN'}
    file = Path('codings.xlsx')
    df = pd.read_excel(file).set_index('CODE')
    df['TEKST'] = df[lang_colname[lang]]
    return df


def load_refs(file, lang):
    """
    Return reference DataFrames set to specified language.
    """
    file = Path(file)
    ps = load_ps(file, lang)
    antw = load_antw(file, lang)
    prog = load_prog(lang)
    codings = load_codings(lang)
    return ps, antw, codings, prog


def get_properties(df_forms, lang='nl'):
    """
    Return current date, matching dates and number of forms used for the report.
    """

    # datetime
    now = dt.datetime.now().strftime('%d-%m-%Y')

    # matching dates
    sort = {
        'FEBRUARI': 0,
        'APRIL': 1,
        'JUNI': 2,
        'JUNI_1': 3,
        'JUNI_2': 4,
        'JUNI_3': 5,
        'AUGUSTUS': 6,
    }

    names = {
        'FEBRUARI': {'nl': 'februari', 'en': 'Februari'},
        'APRIL': {'nl': 'april', 'en': 'April'},
        'JUNI': {'nl': 'juni', 'en': 'June'},
        'JUNI_1': {'nl': 'juni (1)', 'en': 'June (1)'},
        'JUNI_2': {'nl': 'juni (2)', 'en': 'June (2)'},
        'JUNI_3': {'nl': 'juni (3)', 'en': 'June (3)'},
        'AUGUSTUS': {'nl': 'augustus', 'en': 'August'},
        'INDIVIDUEEL': {'nl': 'individueel', 'en': 'Individual'},
    }

    filt = df_forms['PROCESSTAP'].str.contains('O_DATUM_')
    matching_dates = list(df_forms.loc[filt]['ANTWOORD'].unique())
    matching_dates = sorted(matching_dates, key=sort.get)
    matching_dates = [names[date][lang] for date in matching_dates]
    matching_dates = ', '.join(matching_dates)

    # forms
    nforms = df_forms['IO_AANVR_ID'].nunique()

    return now, matching_dates, nforms
