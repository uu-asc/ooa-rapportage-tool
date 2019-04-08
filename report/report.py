import sys
sys.path.insert(0, '../pandas-glit/')

import locale
locale.setlocale(locale.LC_NUMERIC, '')

import numpy as np
import pandas as pd
import pandas_glit as glit
import altair as alt

import report.data as data
import report.processing as process
from .body import Spec, Chapter, Body


def run(file, programmes, matching_dates, lang='nl'):
    """
    Return report of matching form statistics.

    Parameters
    ==========
    :param file: str
        Name of the .pkl file containing the data from the matching forms.
    :param programmes: {str, list}
        (List of) programme codes.
    :param matching_dates: {str, list}
        (List of) matching date codes.

    Optional key-word arguments
    ===========================
    :param lang: {'nl', 'en'}, default 'nl'
        Set output language.

    Return
    ======
    :run: Page
    """

    # some variables
    lang_page = {
        'nl': 'Statistieken matchingsformulier',
        'en': 'Statistics matching form'
        }
    width = 600

    # load data
    df_questions, df_answers, df_codings, df_programmes = data.load_refs(lang)
    df_forms = data.load_forms(file, matching_dates, programmes)
    if df_forms.empty:
        print(f"No results for {', '.join(programmes)}, {matching_dates}")
        return None

    reporter = process.Reporter(
        df_forms, df_questions, df_answers, df_codings, lang=lang
        )

    # introduction
    now, matching_dates, nforms = data.get_properties(df_forms, lang=lang)

    programme = None
    if len(programmes) == 1:
        programme = programmes[0]
        programme_name = df_programmes.at[programme, 'NAAM']
        paragraph = create_introduction(
            programme_name, now, matching_dates, f'{nforms:n}', lang=lang
            )
    else:
        programme_name = None

        # table programme overview
        lang_cols = {'nl': 'Aantal', 'en': 'Number'}
        lang_head = {
            'nl': 'Formulieren per opleiding',
            'en': 'Forms per programme',
            }

        cols = ['FACULTEIT', 'OPLEIDING', 'IO_AANVR_ID']
        df = df_forms[cols].drop_duplicates()
        df = df.groupby(['FACULTEIT', 'OPLEIDING'])['IO_AANVR_ID']\
            .count()\
            .to_frame()\
            .rename(columns={'IO_AANVR_ID': lang_cols[lang]})
        introduction = create_introduction(
            programme_name, now, matching_dates, f'{nforms:n}', lang=lang
            )
        paragraph = (
            f"{introduction}"
            f"<h4>{lang_head[lang]}</h4>\n"
            f"{glit.FancyTable(df).html}"
            )

    page_name_els = [
        programme,
        '2019',
        matching_dates.upper(),
        lang_page[lang],
        programme_name,
        ]
    page_name_els = [i for i in page_name_els if i is not None]
    title_els = [lang_page[lang], programme_name]
    title_els = [i for i in title_els if i is not None]

    # instantiate report
    page = ' '.join(page_name_els)
    title = ' '.join(title_els)
    page = Body(title, page, lang=lang)

    # chapter | introduction
    lang_chap = {'nl': 'Inleiding', 'en': 'Introduction'}
    chapter = Chapter(lang_chap[lang])
    chapter.add_par(paragraph)
    page.add(chapter)

    # chapter | choice
    # spec | tools/activities
    lang_chap = {'nl': 'Studiekeuze', 'en': 'Study choice'}
    lang_axis = {'nl': 'Middel', 'en': 'Tool/activity'}
    ps = 'U_ACTIV_MIDDEL'
    chapter = Chapter(lang_chap[lang])

    query = "PS == @ps and TYPE == 'Q'"
    codes = df_codings.query(query)
    questions = dict(zip(codes.index, codes['TEKST']))

    query = "PS == @ps and TYPE == 'A'"
    codes = df_codings.query(query)
    answers = dict(zip(codes.index, codes['TEKST']))

    df = pd.DataFrame(columns=['Middel', 'Antwoorden', 'Aantal', 'Percentage'])
    for i in questions:
        if len(programmes) == 1:
            if df_questions.at[i, programmes[0]] is np.nan:
                continue
        else:
            if not df_questions.loc[i, programmes].notnull().any():
                continue
        df_i = process.get_results(i, df_forms, answers)
        df_i['Vraag'] = questions[i]
        df = df.append(df_i, ignore_index=True, sort=False)
    answer = codes.at['W-GEBR-W-GEH', 'TEKST']
    query = "Antwoorden == @answer"
    sort = list(
        df.query(query).sort_values('Percentage', ascending=False)['Vraag']
        )
    chart = alt.Chart(df, width=width, height=len(sort)*32,
        ).mark_bar(
            clip=True,
        ).encode(
            x = alt.X('Percentage', scale=alt.Scale(domain=(0, 1))),
            y = alt.Y('Vraag', sort=sort, title=lang_axis[lang]),
            color = alt.Color('Antwoorden'),
        )
    title = (
        f"{df_codings.at[ps, 'TEKST']}, "
        f"n={df_i['Aantal'].sum():n}"
        )
    undertitle = f"<p>{df_questions.at[ps, 'TEKST']}</p>"
    json = chart.to_json()
    spec = Spec(ps, json, title, undertitle=undertitle)
    chapter.add_spec(spec)

    # spec | first choice
    spec = reporter.get_hspec('U_EERSTEKEUZE')
    chapter.add_spec(spec)

    # spec | factors
    lang_yes = {'nl': 'Ja', 'en': 'Yes'}
    lang_no = {'nl': 'Nee', 'en': 'No'}
    ps = 'U_FACTOREN'
    axis = 'Factor'
    query = "PS == @ps and TYPE == 'Q'"
    codes = df_codings.query(query)
    questions = dict(zip(codes.index, codes['TEKST']))

    query = "PROCESSTAP == @ps"
    df_q = df_forms.query(query)
    df = pd.DataFrame(columns=questions)

    for question in questions:
        df[question] = df_q['ANTWOORD'].str.contains(question)

    df = df.replace({True: lang_yes[lang], False: lang_no[lang]})
    index = [lang_yes[lang], lang_no[lang]]
    df_abs = pd.DataFrame(columns=questions, index=index)
    df_rel = pd.DataFrame(columns=questions, index=index)
    for question in questions:
        df_abs[question] = df[question].value_counts()
        df_rel[question] = df[question].value_counts(normalize=True)
    df_abs = df_abs.fillna(0)
    df_rel = df_rel.fillna(0)
    cols = {'level_0': 'Vraag', 'level_1': 'Antwoorden', 0: 'Aantal',}
    df_abs = df_abs.T.stack().reset_index().rename(columns=cols)
    cols = {'level_0': 'Vraag', 'level_1': 'Antwoorden', 0:  'Percentage',}
    df_rel = df_rel.T.stack().reset_index().rename(columns=cols)

    df = df_abs.merge(df_rel, on=['Vraag', 'Antwoorden'])
    df['Vraag'] = df['Vraag'].replace(questions)
    answer = lang_yes[lang]
    query = "Antwoorden == @answer"
    sort = list(
        df.query(query).sort_values('Percentage', ascending=False)['Vraag']
        )
    chart = alt.Chart(df, width=width, height=len(df) * 16).mark_bar().encode(
        x = alt.X('Percentage:Q'),
        y = alt.Y('Vraag:N', sort=sort, title=axis),
        color = alt.Color('Antwoorden:N', sort=['Nee', 'Ja'])
        )
    title = (
        f"{df_codings.at[ps, 'TEKST']}, "
        f"n={df['Aantal'].sum()/len(questions):n}"
        )
    undertitle = f"<p>{df_questions.at[ps, 'TEKST']}</p>"
    json = chart.to_json()
    spec = Spec(ps, json, title, undertitle=undertitle)
    chapter.add_spec(spec)
    page.add(chapter)

    # chapter | time use
    lang_chap = {'nl': 'Tijdsbesteding', 'en': 'Time use'}
    lang_axis = {'nl': 'Tijd in uren', 'en': 'Time in hours'}
    lang_mean = {'nl': 'Gemiddelde', 'en': 'Mean'}
    chapter = Chapter(lang_chap[lang])
    axis_title = lang_axis[lang]
    mean_title = lang_mean[lang]

    cols = ['PROCESSTAP', 'ANTWOORD']
    breaks = [0, 5, 10, 15, 20, 25, 30, 100]
    new_cols = [
        '[0-5)', '[5-10)', '[10-15)', '[15-20)', '[20-25)', '[25-30)', '[30>'
        ]

    chapter_names = list()
    lang_chap = {'nl': 'Schoolweek', 'en': 'School week'}
    chapter_names.append(lang_chap[lang])
    lang_chap = {'nl': 'Studieweek', 'en': 'Study week'}
    chapter_names.append(lang_chap[lang])
    codes = ['O_SCHOOLWK_TOE', 'U_STUDIEWK_TOEL']

    for chapter_name, ps in zip(chapter_names, codes):
        paragraph = df_questions.at[ps, 'TEKST']
        sub_chapter = Chapter(chapter_name)
        sub_chapter.add_par(paragraph)

        query = "PS == @ps and TYPE == 'Q'"
        codes = df_codings.query(query)
        ps = dict(zip(codes.index, codes['TEKST']))

        query = "PROCESSTAP in @ps"
        df_q = df_forms.query(query)[cols]
        if df_q.empty:
            continue
        df_q['ANTWOORD'] = df_q['ANTWOORD'].apply(process.validate_hours)
        df_q = process.add_bin(df_q, 'ANTWOORD', breaks, bin_str=True)

        df_sum = df_q.groupby(['PROCESSTAP'])['ANTWOORD']\
            .agg(['min', 'max', 'mean']).round(1)
        df_q['ANTWOORD'] = df_q['bin']
        cats = list(df_q.bin.cat.categories)
        col_dict = dict(zip(cats, new_cols))

        for i in ps:
            df = process.get_results(i, df_q, col_dict)
            chart = process.vbar_chart(
                df, axis_title=axis_title, colors=False
                )
            title = f"{ps[i]}, n={df['Aantal'].sum():n}"
            undertitle = (
                f"<p>{mean_title}: {df_sum.at[i, 'mean']:n} uren</p>"
                )
            json = chart.to_json()
            spec = Spec(i, json, title, undertitle=undertitle)
            sub_chapter.add_spec(spec)
        chapter.add_chap(sub_chapter)
    page.add(chapter)

    # chapter | statements
    lang_chap = {'nl': 'Stellingen', 'en': 'Statements'}
    chapter = Chapter(lang_chap[lang])

    # spec | conscientiousness
    lang_chap = {'nl': 'Consciëntieusheid', 'en': 'Conscientiousness'}
    sub_chapter = Chapter(lang_chap[lang])
    lang_axis = {'nl': 'Eigenschap', 'en': 'Quality'}

    ps = 'U_STEL_CONSC'
    query = "PS == @ps and TYPE == 'Q'"
    codes = df_codings.query(query)
    questions = dict(zip(codes.index, codes['TEKST']))

    ps = 'STELLING_EENS'
    query = "PS == @ps and TYPE == 'A'"
    codes = df_codings.query(query)
    answers = dict(zip(codes.index, codes['TEKST']))

    score = {
        'Helemaal eens': 2,
        'Eens': 1,
        'Neutraal': 0,
        'Oneens': -1,
        'Helemaal oneens': -2,
    }

    cols = ['Stelling', 'Antwoorden', 'Aantal', 'Percentage']
    df = pd.DataFrame(columns=cols)
    for question in questions:
        df_i = process.get_results(question, df_forms, answers)
        df_i['Vraag'] = questions[question]
        df = df.append(df_i, ignore_index=True, sort=False)

    df['Score'] = df['Antwoorden'].replace(score) * df['Aantal']
    sort = list(
        df.groupby('Vraag')['Score'].sum().sort_values(ascending=False).index
        )

    order = (
        f"if(datum.Antwoorden === '{answers['HELEMAAL-EENS']}', 5, "
        f"if(datum.Antwoorden === '{answers['EENS']}', 4, "
        f"if(datum.Antwoorden === '{answers['NEUTRAAL']}', 3, "
        f"if(datum.Antwoorden === '{answers['ONEENS']}', 2, "
        f"if(datum.Antwoorden === '{answers['HELEMAAL-ONEENS']}', 1, 0)))))"
        )
    chart = alt.Chart(df, width=width, height=len(sort)*32
        ).mark_bar(
            clip=True
        ).encode(
            x = alt.X('Percentage', scale=alt.Scale(domain=(0, 1))),
            y = alt.Y('Vraag', sort=sort, title=lang_axis[lang]),
            color = alt.Color('Antwoorden', sort=list(answers.values())),
            order = alt.Order('order:N')
        ).transform_calculate(
            order = order,
        )

    lang_ques = {
        'nl': 'Stellingen over consciëntieusheid',
        'en': 'Statements on conscientiousness',
        }
    title = f"{lang_ques[lang]}, n={df_i['Aantal'].sum():n}"
    ps = 'U_STELLING_TOEL'
    undertitle = f"<p>{df_questions.at[ps, 'TEKST']}</p>"
    json = chart.to_json()

    spec = Spec(ps, json, title, undertitle=undertitle)
    sub_chapter.add_spec(spec)
    chapter.add_chap(sub_chapter)

    # spec | other statements
    lang_chap = {'nl': 'Overige stellingen', 'en': 'Other statements'}
    sub_chapter = Chapter(lang_chap[lang])
    ps = 'O_STELLING_TOEL'
    paragraph = f"<p>{df_questions.at[ps, 'TEKST']}</p>\n"
    sub_chapter.add_par(paragraph)

    io_codes = ['AANM_5PUNTS', 'AANM_5PUNTS_B']
    answers = ['STELLING_EENS', 'STELLING_PAST']

    for io_code, answer in zip(io_codes, answers):
        filt1 = df_questions.index.str.contains('O_STEL')
        filt2 = df_questions['SYSTEEMLIJST IO'] == io_code
        if len(programmes) == 1:
            filt3 = df_questions[programmes[0]].notnull()
        else:
            filt3 = df_questions[programmes].notnull().any(axis=1)
        ps = list(df_questions.loc[filt1 & filt2 & filt3].index)

        query = "PS == @answer and TYPE == 'A'"
        codes = df_codings.query(query)
        answers = dict(zip(codes.index, codes['TEKST']))

        for i in ps:
            spec = reporter.get_hspec(i, answers=answers, colors=False)
            sub_chapter.add_spec(spec)

    chapter.add_chap(sub_chapter)
    page.add(chapter)

    # chapter | diploma
    chapter = Chapter('Diploma')

    # spec | Preeducation
    lang_axis = {'nl': 'Vooropleiding', 'en': 'Preeducation'}
    axis_title = lang_axis[lang]
    spec = reporter.get_hspec('U_DIPLOMA_BEH', axis_title=axis_title)
    chapter.add_spec(spec)

    # spec | preeducation
    lang_axis = {'nl': 'Profiel', 'en': 'Profile'}
    axis_title = lang_axis[lang]
    spec = reporter.get_hspec('U_PROFIEL', axis_title=axis_title)
    chapter.add_spec(spec)
    page.add(chapter)

    # chapter | grades
    lang_chap = {'nl': 'Cijfers', 'en': 'Grades'}
    chapter = Chapter(lang_chap[lang])
    lang_axis = {'nl': 'Cijfer', 'en': 'Grade'}
    lang_cols = {'nl': 'Vak', 'en': 'Subject'}
    lang_mean = {'nl': 'Gemiddeld cijfer', 'en': 'Average grade'}

    cols = ['PROCESSTAP', 'ANTWOORD']
    breaks = [0, 5, 6, 7, 8, 9, 10]
    new_cols = ['< 4', '5', '6', '7', '8', '9', '10']
    col_dict = dict(zip(breaks, new_cols))

    dct_grades = dict()
    # vwo
    answer = ['VWO_BEH', 'VWO_NOG_BEH']
    query = "PROCESSTAP == 'U_DIPLOMA_BEH' and ANTWOORD in @answer"
    dct_grades['vwo'] = [answer, query]
    # havo
    answer = ['HAVO']
    query = "PROCESSTAP == 'U_HBO_TOEGANG' and ANTWOORD in @answer"
    dct_grades['havo'] = [answer, query]

    for key in dct_grades:
        sub_chapter = Chapter(key)
        answer = dct_grades[key][0]
        query = dct_grades[key][1]
        grp = list(df_forms.query(query)['IO_AANVR_ID'])

        filt1 = df_forms['PROCESSTAP'].str.contains('_CIJF_')
        filt2 = df_forms['PROCESSTAP'].str.contains('_TOEL')
        filt3 = df_forms['IO_AANVR_ID'].isin(grp)

        df_q = df_forms.loc[filt1 & ~filt2 & filt3][cols]
        if df_q.empty:
            continue
        df_q['ANTWOORD'] = df_q['ANTWOORD'].apply(process.validate_grades)
        df_q = df_q.query("~ANTWOORD.isnull()", engine='python')
        ps = list(df_q['PROCESSTAP'].unique())
        ps.sort(key=lambda x:x[2:])
        rows = {i:df_questions.at[i, 'TEKST'] for i in ps}
        df_q = process.add_bin(df_q, 'ANTWOORD', breaks, bin_str=True)
        df_sum = df_q.groupby(['PROCESSTAP'])['ANTWOORD']\
            .agg(['count', 'min', 'max', 'mean'])\
            .round(1)

        df_prnt = df_sum.rename(index=rows)
        df_prnt.index = df_prnt.index.rename(lang_cols[lang])
        paragraph = glit.FancyTable(df_prnt.sort_index()).html
        sub_chapter.add_par(paragraph)

        for i in ps:
            df = process.get_results(i, df_q, col_dict)
            chart = process.vbar_chart(
                df, axis_title=lang_axis[lang], colors=False
                )
            title = (
                f"{df_questions.at[i, 'TEKST']}, "
                f"n={int(df['Aantal'].sum()):n}"
                )
            undertitle = f"<p>{lang_mean[lang]}: {df_sum.at[i, 'mean']:n}</p>"
            json = chart.to_json()
            spec = Spec(f'{i}_{key}', json, title, undertitle=undertitle)
            sub_chapter.add_spec(spec)
        chapter.add_chap(sub_chapter)
    page.add(chapter)

    # chapter | honours
    chapter = Chapter('Honours')
    spec = reporter.get_hspec('U_INTERESSE_HON')
    chapter.add_spec(spec)
    page.add(chapter)

    return page


def create_introduction(programme_name, now, matching_dates, nforms, lang='nl'):
    """
    Return introductory paragraph as html.
    """
    snippets = Body('_', '_', lang).snippets

    preposition = {'nl': 'voor', 'en': 'for'}
    programme_name = (
        '' if programme_name is None
        else f"{preposition[lang]} <b>{programme_name}</b> "
    )

    replacements = {
        '{{ programme_name }}': programme_name,
        }
    html = snippets['intro']
    for replacement in replacements:
        html = html.replace(replacement, replacements[replacement])

    replacements = {
        '{{ now }}': now,
        '{{ matching_dates }}': matching_dates,
        '{{ nforms }}': nforms,
        }
    html += snippets['introtable']
    for replacement in replacements:
        html = html.replace(replacement, replacements[replacement])
    return html
