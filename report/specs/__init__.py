from collections import defaultdict


def transform_specs(specs, data, taal):
    sections = {}
    for key, spec in specs.items():
        section = {}
        section['titel'] = spec['titel'][taal]
        items = []
        for item in spec['items']:
            if item['type'] == 'chart':
                obj = build_chart(item, data, taal)
                output = obj.chart()
                if output is None:
                    continue
                item['uuid'] = obj.spec.uuid
                item['titel'] = obj.spec.titel
                item['output'] = output.to_json(indent=None)
            if item['type'] == 'table':
                tablespec, df = item['item'](data, taal)
                if df.empty:
                    continue
                item['output'] = df.to_html()
                item['titel'] = tablespec.titel
            items.append(item)
        section['items_'] = items
        sections[key] = section
    return sections


def build_jsondata(sections):
    return {
        i['uuid']:i['output']
        for section in sections.values()
        for i in section['items_']
        if i['type'] == 'chart'
    }


def build_chart(spec, data, taal):
    args = spec.get('args', [])
    kwargs = defaultdict(dict)
    for i in spec.get('kwargs', []):
        for key, val in configurations[i].items():
            kwargs[key].update(val)
    return spec['item'](
        *args,
        data=data,
        taal=taal,
        **kwargs
    )


configurations = {
    'noborder': {'configure_view': {'strokeWidth': 0}},
    'nogrid': {'configure_axis': {'grid': False}},
    'small': {
        'configure_view': {
            'continuousWidth': 260,
            'continuousHeight': 150,
        },
    },
}
