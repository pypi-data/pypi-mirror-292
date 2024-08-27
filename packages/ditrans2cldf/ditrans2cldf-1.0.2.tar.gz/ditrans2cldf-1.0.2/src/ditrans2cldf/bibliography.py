import re
import sys

from pybtex.database.input.bibtex import Entry as BibEntry
from pybtex.database import (
    Person as BibPerson, BibliographyData, InvalidNameString
)

from unidecode import unidecode


BIBTEX_FIELDS = {
    'address',
    'booktitle',
    'chapter',
    'journal',
    'note',
    'number',
    'pages',
    'publisher',
    'school',
    'series',
    'title',
    'url',
    'volume',
    'year'}


def _split_people(people_string):
    return re.split(r'\s*(?:&|and|;)\s*', people_string)


def parse_people(people_string):
    people_list = _split_people(people_string)
    try:
        bib_people = [BibPerson(string=s) for s in people_list]
    except InvalidNameString as e:
        msg = 'Could not parse authors/editors: {}'.format(str(e))
        raise ValueError(msg)
    return bib_people


def _clean_key(bibkey):
    bibkey = unidecode(bibkey)

    # Actually, a lot of these are *technically* allowed in bibtex keys, but
    # I don't think we'll do anyone a favour by generating keys like
    # `foo:bar&baz {ham]`
    bibkey = re.sub(r'[!"#%()*,.:<>?@[]\\^`{}]', '', bibkey)
    bibkey = re.sub("'", '', bibkey)
    bibkey = re.sub(r"[&+/;=_|~]", '-', bibkey)
    bibkey = re.sub(r'\s+', '-', bibkey)

    return bibkey.lower()


def generate_bibkey(row):
    bibkey = row.get('LaTeX_cite_key')
    if bibkey:
        return _clean_key(str(bibkey))
    people_str = row.get('author') or row.get('editor')
    if not people_str:
        return _clean_key(str(row.get('ID', 'missing-key')))

    people = parse_people(people_str)

    if len(people) == 1:
        author = '-'.join(people[0].last_names)
    elif len(people) == 2:
        name1 = '-'.join(people[0].last_names)
        name2 = '-'.join(people[1].last_names)
        author = '{}-{}'.format(name1, name2)
    else:
        author = '{}-etal'.format('-'.join(people[0].last_names))
    year = row.get('year', 'na')
    letter = row.get('Year_disambiguation_letter', '')
    bibkey = '{}-{}{}'.format(author, year, letter)
    return _clean_key(bibkey)


def make_bibentry(row, authors, editors):  # pragma: nocover
    key = row.get('LaTeX_cite_key', 'missing-key')
    type_ = row.get('BibTeX_type', 'misc')
    people = {}
    if authors:
        people['author'] = authors
    if editors:
        people['editor'] = editors
    fields = sorted(
        (k, v) for k, v in row.items()
        if k in BIBTEX_FIELDS)
    entry = BibEntry(type_, fields, people)
    entry.key = key
    return entry


def row_to_bibentry(row):  # pragma: nocover
    authors = parse_people(row['author']) if 'author' in row else None
    editors = parse_people(row['editor']) if 'editor' in row else None
    return make_bibentry(row, authors, editors)


def make_bibliography(table):  # pragma: nocover
    db = BibliographyData()
    for row in table:
        try:
            entry = row_to_bibentry(row)
        except ValueError as e:
            print('Reference', row.get('Reference_ID'), 'dropped:', str(e), file=sys.stderr)
            continue
        db.add_entry(entry.key, entry)
    return db
