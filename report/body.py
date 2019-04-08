import re
import textwrap
from pathlib import Path
from .data import BODY, SPEC, CSS, TEMPLATE_PATH

tab = 4 * ' '


class Body:
    def __init__(self, title, page_name, lang='nl'):
        self.language = lang
        self.title = title
        self.page_name = page_name
        self.chapters = []
        self.snippets = self.load_snippets(lang)

    @staticmethod
    def load_snippets(lang):
        # snippets
        snippets = dict()
        for file in TEMPLATE_PATH.glob(f'snippet_*_{lang}.html'):
            name_parts = file.stem.split('_')
            snippets[name_parts[1]] = file.read_text()
        return snippets

    def add(self, item):
        if not isinstance(item, Chapter):
            raise TypeError(
                f'Object of type {type(item)}. '
                'Only instances of Chapter class may be added.')
        self.chapters.append(item)

    @property
    def html(self):
        """
        Return report as html.
        """
        replacements = {
            '{{ page }}': self.page_name,
            '{{ title }}': self.title,
            '{{ toc }}': self.toc,
            '{{ body }}': self.body(),
            '{{ author }}': self.snippets['author'],
            '{{ footer }}': self.snippets['footer'],
            '{{ logo }}': self.snippets['logo'],
            '{{ css }}': CSS,
        }
        html = BODY
        for replacement in replacements:
            html = html.replace(replacement, replacements[replacement])
        return html

    @property
    def toc(self):
        """
        Return table of contents.
        """
        name = {'nl': 'Inhoudsopgave', 'en': 'Table of contents'}

        toc_frame = (
            '<div class="chapter">'
            f'<h2 id="toc">{name[self.language]}</h2>'
            '</div>\n'
            '<ol class="toc">\n'
            '{{ toc }}'
            '</ol>\n'
        )

        toc = ''
        for item in self.headers:
            toc += (
                "<li>"
                f"<a class= \"toc__link\" href=\"#{codify(item)}\">{item}</a>"
                "</li>\n"
            )
        toc = textwrap.indent(toc, tab)

        return toc_frame.replace('{{ toc }}', toc)

    def body(self):
        return self.unpack(self.chapters, 0)

    def unpack(self, chapters, depth):
        body = []
        for chapter in chapters:
            # header
            if depth == 0:
                body.append(self.create_header(chapter.header))
            else:
                body.append(self.create_subheader(chapter.header, depth+3))

            # chapters
            if chapter.chapters:
                body.append(self.unpack(chapter.chapters, depth+1))

            # paragraphs
            if chapter.paragraph is not None:
                body.append(chapter.paragraph)

            # specs
            for spec in chapter.specs:
                body.append(spec.spec)
        return '\n'.join(body)

    @property
    def headers(self):
        return [chapter.header for chapter in self.chapters]

    @staticmethod
    def create_header(item):
        """
        Create header.
        """
        header = (
            f"<a href=\"#toc\">"
            f"<div class=\"chapter\" id=\"{codify(item)}\">"
            f"<h2>{item}</h2>"
            f"<p>&#9651;</p>"
            f"</div>"
            f"</a>\n"
        )
        return header

    @staticmethod
    def create_subheader(item, level):
        """
        Create subheader.
        """
        return f"<h{level}>{item}</h{level}>"


class Chapter:
    def __init__(self, header):
        self.header = header
        self.paragraph = None
        self.chapters = []
        self.specs = []

    def add_chap(self, item):
        if not isinstance(item, Chapter):
            raise TypeError(
                f'Object of type {type(item)}. '
                'Only instances of Chapter class may be added.')
        self.chapters.append(item)

    def add_par(self, html):
        self.paragraph = html

    def add_spec(self, item):
        if not isinstance(item, Spec):
            raise TypeError(
                f'Object of type {type(item)}. '
                'Only instances of Spec class may be added.')
        self.specs.append(item)


class Spec:
    def __init__(self, ps, json, title, undertitle=None):
        self.ps = ps
        self.vis = codify(ps)
        self.el = codify(ps)
        self.json = json
        self.title = title
        self.undertitle = '' if undertitle is None else undertitle

    @property
    def spec(self):
        """
        Set spec based on arguments.
        """
        replacements = {
            '{{ title }}': self.title,
            '{{ undertitle }}': self.undertitle,
            '{{ json }}': self.json,
            '{{ vis }}': self.vis,
            '{{ el }}': self.el,
        }
        spec = SPEC
        for replacement in replacements:
            spec = spec.replace(replacement, replacements[replacement])
        return spec


def codify(item):
    """
    Convert string to lowercase and replace non-alphanumeric characters with
    underscores.
    """
    i = item.lower()
    i = re.sub('[^0-9a-zA-Z]+', '_', i)
    return i
