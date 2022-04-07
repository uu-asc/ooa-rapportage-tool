import pandas as pd


def selecteer_forms(df, data, progs, studentnummers=None):
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
    loaded forms
        pd.DataFrame
    """
    data = [data] if not isinstance(data, list) else data
    progs = [progs] if not isinstance(progs, list) else progs

    cols = [
        'processtap',
        'systeem_antwoord_code',
        'gesloten_antwoord_code',
        'open_antwoord_student',
    ]

    df = (
        df
        .astype(dtype={col:object for col in cols})
        .assign(
            antwoord=lambda df: (
                df.systeem_antwoord_code
                .fillna(df.gesloten_antwoord_code)
                .fillna(df.open_antwoord_student)))
        .drop(columns=[
            'systeem_antwoord_code',
            'gesloten_antwoord_code',
            'open_antwoord_student'])
        .query("opleiding in @progs")
    )

    query = "processtap.str.contains('O_DATUM') and antwoord in @data"
    if studentnummers is not None:
        query += ' and studentnummer in @studentnummers'
    forms = df.query(query).ooa_id.unique()
    return df.loc[lambda df: df.ooa_id.isin(forms)]
