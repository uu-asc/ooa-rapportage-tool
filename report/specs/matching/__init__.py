import report.specs.matching.api as charts


def load_specs():
    return {
        'Studiekeuze': {
            'titel': {'nl': 'Studiekeuze', 'en': 'Study choice'},
            'items': [
                {
                    'item': charts.StudiekeuzeMiddel,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                },
                {
                    'item': charts.EersteKeus,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.StudiekeuzeFactoren,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                },
                {
                    'item': charts.TrackLITB,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.TrackTHEB,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.TrackTLWB,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.OverigBeroep,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                }
            ],
        },
        'Tijdsbesteding': {
            'titel': {'nl': 'Tijdsbesteding', 'en': 'Time use'},
            'items': [
                {
                    'item': charts.TijdsbestedingSchool,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                },
                {
                    'item': charts.TijdsbestedingStudie,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                },
            ],
        },
        'Stellingen': {
            'titel': {'nl': 'Stellingen', 'en': 'Statements'},
            'items': [
                {
                    'item': charts.Conscientieus,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                },
                {
                    'item': charts.StellingEens,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                },
                {
                    'item': charts.StellingPast,
                    'type': 'chart',
                    'kwargs': ['noborder', 'nogrid'],
                },
            ]
        },
        'Vooropleiding': {
            'titel': {'nl': 'Vooropleiding', 'en': 'Preeducation'},
            'items': [
                {
                    'item': charts.Vooropleiding,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.Profiel,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
            ],
        },
        'Cijfers': {
            'titel': {'nl': 'Cijfers', 'en': 'Grades'},
            'items': [
                {
                    'item': charts.TabelVWO,
                    'type': 'table',
                },
                {
                    'item': charts.GrafiekVWO,
                    'type': 'chart',
                    'kwargs': ['small', 'noborder', 'nogrid'],
                },
                {
                    'item': charts.TabelHAVO,
                    'type': 'table',
                },
                {
                    'item': charts.GrafiekHAVO,
                    'type': 'chart',
                    'kwargs': ['small', 'noborder', 'nogrid'],
                },
            ],
        },
        'Honours': {
            'titel': {'nl': 'Honours', 'en': 'Honours'},
            'items': [
                {
                    'item': charts.Honours,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.ExtraExamenVak,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.Plusprogramma,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.ExtraActiviteit,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
                {
                    'item': charts.Verdiepen,
                    'type': 'chart',
                    'kwargs': ['noborder'],
                },
            ],
        },
    }
