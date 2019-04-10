from pathlib import Path
import datetime as dt
import pandas as pd
import src.query as qry


name_procesdef = 'procesdefinitie_BA1920_MATCHING_PRD.xlsx'

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
    'GEO': [
        'INMB', 'SGPB', 'AARD',
        ],
    'GW': [
        'ISAB', 'WBGB', 'LITB', 'TCSB', 'HISB',
        'CIWB', 'ENGB', 'THEB', 'GESB', 'LASB',
        'FRAB', 'KUNB', 'TLWB', 'SPAB', 'DUIB',
        'NEDB', 'MUZB', 'KELB', 'ITAB', 'THEO',
        ],
    'ECBB': ['ECBB'],
    'RGLB': ['RGLB'],
    'SW': [
        'ASWB', 'PEDB', 'SOCB', 'OWKB', 'CULB'
        ],
    }


def load_forms(file, matching_dates, programmes):
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

    # forms
    df_forms = qry.load_frame(file)
    df_forms['ANTWOORD'] = df_forms['SYSTEEM_ANTWOORD_CODE']\
        .fillna(df_forms['GESLOTEN_ANTWOORD_CODE'])\
        .fillna(df_forms['OPEN_ANTWOORD_STUDENT'])
    cols = [
        'SYSTEEM_ANTWOORD_CODE',
        'GESLOTEN_ANTWOORD_CODE',
        'OPEN_ANTWOORD_STUDENT',
    ]
    df_forms = df_forms.drop(cols, axis=1)

    filt1 = df_forms['PROCESSTAP'].str.contains('O_DATUM_')
    filt2 = df_forms['ANTWOORD'].isin(matching_dates)
    forms = list(df_forms.loc[filt1 & filt2]['IO_AANVR_ID'].unique())

    filt1 = df_forms['IO_AANVR_ID'].isin(forms)
    filt2 = df_forms['OPLEIDING'].isin(programmes)

    return df_forms.loc[filt1 & filt2]


def load_refs(lang):
    """
    Return reference DataFrames set to specified language.
    """

    file = Path(name_procesdef)

    # questions
    lang_colname = {'nl': 'TEKST', 'en': 'TEKST EN'}
    df_questions = pd.read_excel(
        file,
        sheet_name='processtappen',
        skiprows=[0, 1, 3],
    )
    cols = ['ACTOR', 'HS#']
    df_questions.loc[:, cols] = df_questions.loc[:, cols].fillna(method='ffill')
    cols = [
        'CHILD AANTAL H',
        'CHILD AANTAL V',
        'CHILD STRING',
        'PARENT AANTAL H',
        'PARENT AANTAL V',
        'PARENT STRING',
        'IPRO ID',
        'PARENT IPRO ID',
        ]
    df_questions = df_questions.query("ACTOR == 'S'")\
        .drop(cols, axis=1)\
        .set_index('PROCESSTAP')
    df_questions['TEKST'] = df_questions[lang_colname[lang]]

    # answers
    lang_colname = {'nl': 'ANTWOORD', 'en': 'ANTWOORD EN'}
    df_answers = pd.read_excel(
        file,
        sheet_name='antwoorden',
        skiprows=[1],
    )
    cols = ['ACTOR', 'HS#', 'PS#']
    df_answers.loc[:, cols] = df_answers.loc[:, cols].fillna(method='ffill')
    cols = [
        'HOOFDSTUK',
        'PROCESSTAP',
        'AW#',
        'ANTWOORD CODE',
        'ANTWOORD',
        'ANTWOORD EN'
        ]
    df_answers = df_answers.query("ACTOR == 'S'")[cols]\
        .set_index(['PROCESSTAP', 'ANTWOORD CODE'])
    df_answers['ANTWOORD'] = df_answers[lang_colname[lang]]

    # programmes
    lang_colname = {'nl': 'NAAM_NL', 'en': 'NAAM_EN'}
    df_programmes = qry.load_frame('r_opl').set_index('OPLEIDING')
    df_programmes['NAAM'] = df_programmes[lang_colname[lang]]

    # codings
    lang_colname = {'nl': 'NL', 'en': 'EN'}
    file = Path('codings.xlsx')
    df_codings = pd.read_excel(file).set_index('CODE')
    df_codings['TEKST'] = df_codings[lang_colname[lang]]

    return df_questions, df_answers, df_codings, df_programmes


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
