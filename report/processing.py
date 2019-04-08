import numpy as np
import pandas as pd
import altair as alt
import locale
from pandas.api.types import CategoricalDtype
from .body import Spec
locale.setlocale(locale.LC_NUMERIC, '')


class Reporter:
    """
    Reporter class
    ==============
    Class for creating standard specs.
    """

    def __init__(
        self,
        df_forms,
        df_questions,
        df_answers,
        df_codings,
        lang='nl'
        ):
        self.df_forms = df_forms
        self.df_questions = df_questions
        self.df_answers = df_answers
        self.df_codings = df_codings
        self.lang = lang

        self.lang_axis = {'nl': 'Antwoord', 'en': 'Answer'}
        self.colname_answer = {'nl': 'Antwoorden', 'en': 'Answers'}
        self.colname_abs = {'nl': 'Aantal', 'en': 'Number'}
        self.colname_rel = {'nl': 'Percentage', 'en': 'Percentage'}

    def get_hspec(
        self,
        ps,
        answers=None,
        axis_title=None,
        colors=True,
    ):
        """
        Return spec with hbar.

        Parameters
        ==========
        :param ps: str
            Key for selecting question.

        Optional keyword arguments
        ==========================
        :param answers: {DataFrame, list or dict}, default self.df_answers
            - df with reference table containing possible answers.
            - List of possible answer codes.
            - Dictionary of possible answer codes and answer text.

        Returns
        =======
        :get_hspec: Spec
        """

        # set variables
        if axis_title is None:
            axis_title = self.lang_axis[self.lang]
        if answers is None:
            answers = self.df_answers

        df = get_results(ps, self.df_forms, answers)
        title = f"{self.df_codings.at[ps, 'TEKST']}, n={df['Aantal'].sum():n}"
        undertitle = f"<p>{self.df_questions.at[ps, 'TEKST']}</p>"
        chart = hbar_chart(df, axis_title=axis_title, colors=colors)
        json = chart.to_json()
        return Spec(ps, json, title, undertitle=undertitle)


def get_results(
    ps,
    df_forms,
    answers,
    sort=None,
    colname_answer='Antwoorden',
    colname_abs='Aantal',
    colname_rel='Percentage',
):
    """
    Return df with absolute and relative frequencies for each possible answer.

    Parameters
    ==========
    :param ps: string
        Code for question ('processtap').
    :param df_forms: DataFrame
        Table containing filled out application form questions.
    :param answers: {DataFrame, list or dict}
        - df with reference table containing possible answers.
        - List of possible answer codes.
        - Dictionary of possible answer codes and answer text.

    Optional keyword arguments
    ==========================
    :param sort: {'asc', 'desc'} or None, default None
        Sort output DataFrame based on relative values.
        'asc' - Sort ascending
        'desc'- Sort descending
        None - Sort based on order in reference table
    :param colname_answer: str, default 'Antwoorden'
        Column name for answer labels.
    :param colname_abs: str, default 'Aantal'
        Column name for absolute frequencies.
    :param colname_rel: str, default 'Percentage'
        Column name for relative frequencies.

    Returns
    =======
    :get_results: DataFrame
    """

    # prepare index
    index = answers
    if isinstance(answers, pd.DataFrame):
        index = list(answers.xs(ps).index)
    df = pd.DataFrame(index=index)

    # get data
    query = "PROCESSTAP == @ps"
    df_q = df_forms.query(query)

    # prepare absolute values
    df = df.join(df_q['ANTWOORD'].value_counts())
    df = df.rename(columns={'ANTWOORD': colname_abs})
    df = df.fillna(0).astype('int')

    # prepare relative values
    df = df.join(df_q['ANTWOORD'].value_counts(normalize=True))
    df = df.rename(columns={'ANTWOORD': colname_rel})
    df = df.fillna(0)

    # convert codes to text
    df.index.name = colname_answer
    df = df.reset_index()
    if isinstance(answers, pd.DataFrame):
        df[colname_answer] = df[colname_answer]\
            .apply(lambda x: answers.at[(ps, x), 'ANTWOORD'])
    elif isinstance(answers, dict):
        df[colname_answer] = df[colname_answer].replace(answers)

    # sort output
    if sort is not None:
        if sort == 'asc':
            df = df.sort_values(colname_rel)
        else:
            df = df.sort_values(colname_rel, ascending=False)
    return df


def hbar_chart(df, axis_title=None, colors=True, width=600):
    """
    Create a horizontal bar chart form df.
    Height is calculated from number of bars.

    Parameters
    ==========
    :param df: DataFrame

    Optional keyword arguments
    ==========================
    :param axis_title: {str, None}, default None
        Title of the y-axis.
    :param colors: boolean, default True
        Color bars.
    :param width: int, default 600
        Set width of chart.

    Returns
    =======
    :hbar_chart: altair Chart
    """

    # set sort if none
    sort = list(df['Antwoorden'])

    # colors
    colorspec = alt.value('#1f77b4')
    if colors:
        colorspec = alt.Color(
            'Antwoorden:N',
            legend=None,
        )

    # bars
    bars = alt.Chart(
        df,
        width=width,
        height=len(df)*32,
    ).mark_bar().encode(
        x = alt.X(
            'Percentage:Q',
            scale=alt.Scale(domain=(0, 1)),
        ),
        y = alt.Y(
            'Antwoorden:N',
            sort=sort,
            title=axis_title,
        ),
        color = colorspec,
    )

    # numbers
    text = bars.mark_text(
        align='left',
        baseline='middle',
        dx=3,
    ).encode(
        text = 'Aantal:Q',
        y = alt.Y(
            'Antwoorden:N',
            sort=sort,
            title=None,
            axis=alt.Axis(labels=False, ticks=False),
        ),
        color = alt.value('black'),
        opacity = alt.condition(
            'datum.Aantal === 0', alt.value(0), alt.value(1)
        ),
    )

    # combine
    chart = (
        bars + text
    ).resolve_scale(
        y='independent'
    ).configure_axisY(minExtent=80)
    return chart


def vbar_chart(df, axis_title=None, colors=True, width=600, height=200):
    """
    Create a vertical bar chart form df.

    Parameters
    ==========
    :param df: DataFrame

    Optional keyword arguments
    ==========================
    :param axis_title: {str, None}, default None
        Title of the y-axis.
    :param colors: boolean, default True
        Color bars.
    :param width: int, default 600
        Set width of chart.
    :param height: int, default 200
        Set height of chart.

    Returns
    =======
    :hbar_chart: altair Chart
    """

    # set sort if none
    sort = list(df['Antwoorden'])

    # colors
    colorspec = alt.value('#1f77b4')
    if colors:
        colorspec = alt.Color(
            'Antwoorden:N',
            legend=None,
        )

    # bars
    bars = alt.Chart(
        df,
        width=width,
        height=height,
    ).mark_bar().encode(
        y = alt.Y(
            'Percentage:Q',
            scale=alt.Scale(domain=(0, 1)),
        ),
        x = alt.X(
            'Antwoorden:N',
            sort=sort,
            title=axis_title,
        ),
        color = colorspec,
    )

    # numbers
    text = bars.mark_text(
        align='left',
        baseline='middle',
        dy=-5,
    ).encode(
        text = 'Aantal:Q',
        x = alt.X(
            'Antwoorden:N',
            sort=sort,
            title=None,
            axis=alt.Axis(labels=False, ticks=False),
        ),
        color = alt.value('black'),
        opacity = alt.condition(
            'datum.Aantal === 0', alt.value(0), alt.value(1)
        ),
    )

    # combine
    chart = (
        bars + text
    ).resolve_scale(
        x='independent'
    )
    return chart


def add_bin(df, target_field, breaks, bin_col='bin', bin_str=False):
    """
    Add column to DataFrame where values from target field are categorized into bins of bin_size.

    Parameters
    ==========
    :param df: DataFrame
    :param target_field: string
        Name of field to be binned.
    :param breaks: list
        List of breakpoints.

    Optional keyword arguments
    ==========================
    :param bin_col: string, default 'bin'
        Name of bin field.
    :param bin_str: boolean, default False
        Convert interval to string.

    Returns
    =======
    :quick_bin: DataFrame
    """

    df = df.copy()

    # define bins according to bin size
    index=pd.IntervalIndex.from_breaks(breaks)
    df[bin_col] = pd.cut(df[target_field], bins=index)

    # convert interval to string rep
    if bin_str:
        cat_names = [
            f'[{x.left}-{x.right})'
            for x in df[bin_col].cat.categories.values
        ]
        cat = CategoricalDtype(categories=cat_names, ordered=True)
        df[bin_col] = df[bin_col].cat.rename_categories(cat_names)
        df[bin_col] = df[bin_col].astype(cat)
    return df


def validate_hours(x):
    """
    Return text as number or NaN if conversion fails.
    """

    try:
        return locale.atof(x)
    except:
        return np.nan


def validate_grades(x):
    """
    Return text as number or NaN if conversion fails.
    - Numbers larger than 100 are discarded.
    - Numbers between 10 and 100 are normalized to 1-10 range.
    - Numbers lower than a 4 are discarded.
    """

    x = pd.to_numeric(x, errors='coerce')
    if x > 100:
        return np.nan
    if x > 10:
        return x / 10
    if x < 4:
        return np.nan
    return x
