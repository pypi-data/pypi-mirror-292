import re
import sys
import collections
from itertools import chain, zip_longest

from cldfbench.catalogs import Glottolog
import cldfcatalog
from clldutils.misc import slug

from ditrans2cldf import bibliography as bib


def extract_table(original_table, primary_key, columns):
    """Return a table extracted from another table.

    This will create a new table from all rows with unique values for
    `primary_key`.  Only columns set in `columns` will be included in the new
    table.
    """
    new_table = {}
    for orig_row in original_table:
        id_ = orig_row.get(primary_key)
        if not id_:
            continue
        new_row = {
            k: v for k, v in orig_row.items()
            if k == primary_key or k in columns}
        # TODO Check for conflicting rows
        if id_ not in new_table:
            new_table[id_] = new_row
    return list(new_table.values())


def map_colnames(row, name_map):
    """Return table row with renamed column names according to `name_map`."""
    return {
        name_map.get(k, k): v
        for k, v in row.items()}


def _add_code_numbers(code_table):
    numbers = collections.defaultdict(int)
    for row in code_table:
        if (param_id := row.get('Parameter_ID')):
            numbers[param_id] += 1
            row = dict(row)
            row['Number'] = numbers[param_id]
        yield row


def add_code_numbers(code_table):
    """Return a Code table, where all the 'Number' columns are filled.

    More precisely, all codes belonging to the same parameter are numbered
    sequentially.
    """
    return list(_add_code_numbers(code_table))


def _merge_two(row1, row2, merge_fields):
    for f in merge_fields:
        if row1.get(f) and row2.get(f):
            row1[f].extend(row2[f])
        elif not row1.get(f) and row2.get(f):
            row1[f] = row2[f]


def merge_array_rows(table, primary_key, merge_fields):
    """Return table where rows inserted to represent arrays are collapsed.

    Technically, FileMaker does not allow multiple values in a single cell of
    a table.  If a field *does* contain multiple values, there are spread out
    across multiple rows.

    This function collapses these rows into one for each data point.  More
    precisely, it looks for rows which lack a value for the `primary_key` field
    and collapses the values of all fields defined in `merge_fields`
    into a list.
    """
    new_table = []

    last_row = None
    for row in table:
        new_row = {
            k: [v] if k in merge_fields else v
            for k, v in row.items()}
        if not last_row:
            last_row = new_row
            continue
        if new_row.get(primary_key):
            new_table.append(last_row)
            last_row = new_row
        else:
            _merge_two(last_row, new_row, merge_fields)

    if last_row:
        new_table.append(last_row)
    return new_table


def _fill_with_previous(table, columns, breaker):
    filler = {}
    new_breaker = None
    for row in table:
        new_filler = {
            col: row[col]
            for col in columns
            if col in row}
        if new_filler:
            filler = new_filler
            new_breaker = row[breaker]
        elif new_breaker != row[breaker]:
            new_breaker = row[breaker]
            filler = {}
        else:
            row = dict(chain(row.items(), filler.items()))
        yield row


def fill_with_previous(table, columns, breaker):
    """Return table in which values for `columns` are filled.

    If a value for a column is empty, it is filled using information from the
    previous row.
    """
    return list(_fill_with_previous(table, columns, breaker))


def _drop_duplicates(table, columns, id_map=None):
    if id_map:
        reverse_index = {
            old_id: new_id
            for new_id, old_id in id_map.items()}
    else:
        reverse_index = {}
    previous = {}
    for row in table:
        unique_cols = tuple(row.get(col) for col in columns)
        if unique_cols in previous:
            if id_map and row.get('ID'):
                # make sure that stuff searching for duplicate's *old* ID is
                # pointed to the unique row's *new* id..
                this_old_id = reverse_index[row.get('ID')]
                prev_new_id = previous[unique_cols]
                id_map[this_old_id] = prev_new_id
            continue
        previous[unique_cols] = row.get('ID')
        yield row


def drop_duplicates(table, columns, id_map=None):
    """Return a table with duplicates removed.

    This works anologous to UNIQUE constraints in databases:  Every row is
    checked for uniqueness w.r.t. the values for a given set of `columns`.
    """
    return list(_drop_duplicates(table, columns, id_map))


def remove_invalid_iso_codes(row):
    """Return a row that only contains valid ISO639 codes.

    Invalid values are dropped.
    """
    # TODO Warn about dropped fields
    isocode = row.get('ISO639P3code', '')
    if re.fullmatch(r'[a-z]{3}', isocode):
        return row
    else:
        return {k: v for k, v in row.items() if k != 'ISO639P3code'}


class ParameterGuesser:
    """Fill in missing `Parameter_ID` based on a Codes table.

    Idea:  If a row in a value tables lacks a `Parameter_ID`, it can be
    recovered by looking up, which parameter the Code is associated with.
    """

    def __init__(self, codes_table):
        self._index = {
            code['ID']: code['Parameter_ID']
            for code in codes_table
            if 'ID' in code and 'Parameter_ID' in code}

    def fixed_row(self, row):
        if 'Parameter_ID' in row:
            return row
        if 'Code_ID' not in row:
            return row
        if row['Code_ID'] not in self._index:
            return row
        new_row = dict(row)
        new_row['Parameter_ID'] = self._index[row['Code_ID']]
        return new_row


class RowCompletenessEvaluator:

    def __init__(self, required_columns):
        self.required_columns = required_columns
        self.missing = {}

    def is_complete(self, row):
        row_id = row.get('ID')
        missing = [
            col
            for col in self.required_columns
            if not row.get(col)]
        if missing:
            self.missing[row_id] = missing
            return False
        else:
            return True


def drop_incomplete(table, required_columns, table_name=None):
    evaluator = RowCompletenessEvaluator(required_columns)
    new_table = list(filter(evaluator.is_complete, table))
    if table_name:
        for row_id, missing in evaluator.missing.items():
            print(
                '{}:{}:'.format(table_name, row_id),
                'Row dropped due to missing required columns:',
                ', '.join(missing),
                file=sys.stderr)
    return new_table


def drop_unused(table, used_ids, table_name=None):
    old_size = len(table)
    if old_size == len(used_ids):
        return table

    new_table = [
        row for row in table
        if row.get('ID') in used_ids]
    if table_name and old_size - len(new_table) > 0:
        print(
            'dropped', old_size - len(new_table), 'out of', old_size,
            table_name, "records because they aren't being referenced by anything",
            file=sys.stderr)
    return new_table


def _split_field(pair, gloss_fields):
    k, v = pair
    if k in gloss_fields:
        return k, v.split()
    else:
        return k, v


def split_glosses(row, gloss_fields):
    """Return row where all glosses split across whitespace.

    `gloss_fields` contains a collection of field names to be affected.
    """
    return dict(
        _split_field(pair, gloss_fields)
        for pair in row.items())


def render_example(example):
    words = example.get('Analyzed_Word') or []
    glosses = example.get('Gloss') or []
    id_width = len(example['ID'])
    widths = [max(len(w), len(g)) for w, g in zip(words, glosses)]
    padded_words = [
        word.ljust(width)
        for word, width in zip_longest(words, widths, fillvalue=0)]
    padded_glosses = [
        gloss.ljust(width)
        for gloss, width in zip_longest(glosses, widths, fillvalue=0)]
    return '({})  {}\n{}    {}\n{}    {}'.format(
        example['ID'],
        example['Primary_Text'].strip(),
        ' ' * id_width,
        '  '.join(padded_words).rstrip(),
        ' ' * id_width,
        '  '.join(padded_glosses).rstrip())


def warn_about_misaligned_glosses(examples):
    """Warn about misaligned glosses.

    In this case misalignment means the number of analysed words and
    the number of glosses are different."""
    for example in examples:
        word_count = len(example.get('Analyzed_Word') or ())
        gloss_count = len(example.get('Gloss') or ())
        if word_count != gloss_count:
            print(
                'examples:{}:'.format(example['ID']),
                'Number of words different from number of glosses',
                file=sys.stderr)
            print(render_example(example), file=sys.stderr)


class IDUniqueMaker:
    """Ensures uniqueness of ids."""

    def __init__(self):
        self._ids = set()

    def unique_id(self, id_):
        """Check uniqueness of `id_` and return an alternative.

        This will check if `id_` was encountered before and add a sequential
        number to the end if it was:

            >>> unique_maker = IDUniqueMaker()
            >>> unique_maker.unique_id('a')
            'a'
            >>> unique_maker.unique_id('a')
            'a-2'
            >>> unique_maker.unique_id('b')
            'b'
            >>> unique_maker.unique_id('b')
            'b-2'
            >>> unique_maker.unique_id('a')
            'a-3'

        """
        number = 1
        new_id = id_
        while new_id in self._ids:
            number += 1
            new_id = '{}-{}'.format(id_, number)
        self._ids.add(new_id)
        return new_id


class SequentialIDMaker:
    """Create unique primary keys for table rows."""

    def __init__(self, prefix=None):
        self._prefix = prefix or ''
        self._last_id = 0

    def make_id(self, row):
        """Return a unique primary key for `row`.

        The key is composed of a prefix and a sequential number.
        """
        self._last_id += 1
        return '{}{}'.format(self._prefix, self._last_id)


class CodeIDMaker:
    """Create unique primary keys for the `CodeTable`."""

    def __init__(self, param_ids, prefix=None):
        self._param_ids = param_ids
        self._prefix = prefix or ''
        self._seq_id_maker = SequentialIDMaker(prefix)
        self._unique_maker = IDUniqueMaker()

    def make_id(self, row):
        """Return a unique primary key for `row`.

        The key is composed of the parameter ID and the contents of the
        `Number` column.  The generation falls back to a sequential number if
        either column is empty or missing.
        """
        param_id = row.get('Parameter_ID')
        number = row.get('Number')
        if not param_id or not number:
            return self._seq_id_maker.make_id(row)
        param_id = self._param_ids.get(param_id, param_id)
        return self._unique_maker.unique_id(
            '{}-{}{}'.format(param_id, self._prefix, number))


class LanguageIDMaker:
    """Create a unique primary key for the `LanguageTable`."""

    def __init__(self, prefix=None):
        self._seq_id_maker = SequentialIDMaker(prefix)
        self._unique_maker = IDUniqueMaker()

    def make_id(self, row):
        """Return a unique primary key for `row`.

        This tries to use glottocode of the language as a key.  If the `row`
        lacks a glottocode, the method falls back to the following information:

            glottocode > iso code > normalised name > original id > seq. number
        """
        if row.get('Glottocode'):
            id_ = row.get('Glottocode')
        elif row.get('ISO639P3code'):
            id_ = row.get('ISO639P3code')
        elif row.get('Name'):
            id_ = slug(row.get('Name'))
        elif row.get('ID'):
            id_ = row.get('ID')
        else:
            id_ = self._seq_id_maker.make_id(row)
        return self._unique_maker.unique_id(id_)


class ValueIDMaker:
    """Create a unique primary key for the `ValueTable` etc."""

    def __init__(self, unit_field, unit_id_map, param_id_map, prefix=None):
        """Create a value id generator.

            `unit_field`:   Column name of the unit described by the parameter
                            (e.g. `Language_ID` or `Construction_ID`).
            `unit_id_map`:  Maps the original id of the unit to the new id,
                            which will ultimately end up in the CLDF output.
            `param_id_map`: Maps the original id of the unit to the new id,
                            which will ultimately end up in the CLDF output.
            `prefix`:       Prefix for sequentially numbered ids (if necessary)
        """
        self._unit_field = unit_field
        self._unit_ids = unit_id_map
        self._param_ids = param_id_map
        self._seq_id_maker = SequentialIDMaker(prefix)
        self._unique_maker = IDUniqueMaker()

    def make_id(self, row):
        """Return a unique primary key for `row`.

        The key consists of the id of the unit and the parameter the value
        belongs to.  If either is missing, this returns a sequentially numbered
        id instead.
        """
        unit_id = row.get(self._unit_field)
        unit_id = self._unit_ids.get(unit_id, unit_id)
        param_id = row.get('Parameter_ID')
        param_id = self._param_ids.get(param_id, param_id)
        if unit_id and param_id:
            id_ = '{}-{}'.format(unit_id, param_id)
        else:
            id_ = self._seq_id_maker.make_id(row)
        return self._unique_maker.unique_id(id_)


class ForeignKeyFixer:

    def __init__(self, key_column, foreign_id_map):
        self.key_column = key_column
        self.foreign_id_map = foreign_id_map
        self.missing = {}

    def _fix_single_foreign_key_field(self, row_id, old_id):
        new_id = self.foreign_id_map.get(str(old_id))
        if new_id:
            return new_id
        else:
            if row_id not in self.missing:
                self.missing[row_id] = []
            self.missing[row_id].append(old_id)
            return None

    def _fix_foreign_key_field(self, row_id, kv_pair):
        k, v = kv_pair
        if k != self.key_column:
            return kv_pair
        elif isinstance(v, list):
            new_refs = [
                new_id
                for old_id in v
                if (new_id := self._fix_single_foreign_key_field(row_id, old_id))]
            return k, new_refs
        elif (new_ref := self._fix_single_foreign_key_field(row_id, v)):
            return k, new_ref
        else:
            return None

    def _fix_row(self, row):
        new_kvpairs = [
            self._fix_foreign_key_field(row.get('ID'), kv_pair)
            for kv_pair in row.items()]
        return dict(filter(None, new_kvpairs))

    def fix_keys(self, table):
        return list(map(self._fix_row, table))


def fix_foreign_keys(table, key_column, foreign_id_map, table_name=None):
    fixer = ForeignKeyFixer(key_column, foreign_id_map)
    new_table = fixer.fix_keys(table)
    if table_name:
        for row_id, missing_keys in fixer.missing.items():
            for key in missing_keys:
                print(
                    '{}:{}:{}:'.format(table_name, row_id, key_column),
                    'Dropped unknown crossref:', key,
                    file=sys.stderr)
    return new_table


# TODO move to proper place
# FIXME also, unlike all other functions here this is mutating the table
def add_ids(id_maker, table):
    id_map = {}
    for row in table:
        new_id = id_maker.make_id(row)
        # XXX Check for collisions among old IDs?
        # Technically this should never happen, because FileMaker should keep
        # its own data valid, but you never know...
        if (old_id := row.get('ID')):
            id_map[str(old_id)] = new_id
        row['ID'] = new_id
    return id_map


# TODO move to proper place
def add_bibkeys(reference_table):
    bibkey_map = {}
    bibkeys = set()
    new_table = []
    for row in reference_table:
        old_id = row.get('ID')
        if not old_id:
            continue

        try:
            bibkey = bib.generate_bibkey(row)
        except ValueError as e:
            print(
                'Reference {}: Could not generate bibkey:'.format(old_id),
                str(e), file=sys.stderr)
            continue

        bibkey_map[str(old_id)] = bibkey

        # TODO Warn about potential duplicates
        if bibkey not in bibkeys:
            new_row = dict(row)
            new_row['ID'] = bibkey
            new_row['LaTeX_cite_key'] = bibkey
            new_table.append(new_row)
            bibkeys.add(bibkey)

    return new_table, bibkey_map


# TODO move to proper place
class SourceFixer:

    def __init__(self, bibkey_map):
        self.bibkey_map = bibkey_map
        self.missing = {}

    def _fix_single_source(self, row_id, ref_id, pages):
        bibkey = self.bibkey_map.get(str(ref_id))
        if not bibkey:
            if row_id not in self.missing:
                self.missing[row_id] = []
            self.missing[row_id].append(str(ref_id))
            return None
        elif pages:
            return '{}[{}]'.format(bibkey, pages.replace(';', ','))
        else:
            return bibkey

    def fix_source(self, row):
        ref_ids = row.get('Reference_ID')
        if not ref_ids:
            return row
        pages = row.get('Reference_pages', ())
        # sometimes there are more page numbers than ids...
        if len(pages) > len(ref_ids):
            pages = pages[:len(ref_ids)]
        row_id = row.get('ID')

        sources = [
            self._fix_single_source(row_id, ref_id, pages)
            for ref_id, pages in zip_longest(ref_ids, pages)]
        sources = list(filter(None, sources))
        new_row = dict(row)
        new_row['Source'] = sources
        return new_row


def fix_sources(table, bibkey_map, table_name=None):
    fixer = SourceFixer(bibkey_map)
    new_table = list(map(fixer.fix_source, table))
    if table_name:
        for row_id, missing_keys in fixer.missing.items():
            for key in missing_keys:
                print(
                    '{}:{}:'.format(table_name, row_id),
                    'Dropped unknown source:', key,
                    file=sys.stderr)
    return new_table


def make_cldf_tables(raw_data, config):
    # TODO Account for missing tables
    lcodes = extract_table(
        raw_data['Language_data'],
        'Language_parameter_value_name_ID',
        ['Language_parameter_value_names_of_Language_data::Value_name',
         'Language_parameter_ID'])
    lcodes = [
        map_colnames(row, config['colname_maps']['lcodes'])
        for row in lcodes]
    # keep the codes for the same parameter together for human-readability
    lcodes.sort(key=lambda r: r.get('Parameter_ID', ''))
    lcodes = add_code_numbers(lcodes)

    ccodes = extract_table(
        raw_data['Construction_data'],
        'Construction_parameter_value_name_ID',
        ['Construction_parameter_value_names_of_Construction_data::Value_name',
         'Construction_parameter_ID'])
    ccodes = [
        map_colnames(row, config['colname_maps']['ccodes'])
        for row in ccodes]
    # keep the codes for the same parameter together for human-readability
    ccodes.sort(key=lambda r: (r.get('Parameter_ID', ''), r.get('Name', '')))
    ccodes = add_code_numbers(ccodes)

    languages = [
        map_colnames(row, config['colname_maps']['languages'])
        for row in raw_data['Languages']]
    lparams = [
        map_colnames(row, config['colname_maps']['lparameters'])
        for row in raw_data['Language_parameters']]
    lvalues = [
        map_colnames(row, config['colname_maps']['lvalues'])
        for row in raw_data['Language_data']]
    constructions = [
        map_colnames(row, config['colname_maps']['constructions'])
        for row in raw_data['Constructions']]
    cparams = [
        map_colnames(row, config['colname_maps']['cparameters'])
        for row in raw_data['Construction_parameters']]
    cvalues = [
        map_colnames(row, config['colname_maps']['cvalues'])
        for row in raw_data['Construction_data']]
    examples = [
        map_colnames(row, config['colname_maps']['examples'])
        for row in raw_data['Examples']]

    references = [
        map_colnames(row, config['bibtex_map'])
        for row in raw_data['References']]

    # merge array fields
    constructions = merge_array_rows(
        constructions, 'ID',
        ['Example_IDs', 'Reference_ID', 'Reference_pages'])
    # I know, those are not really primary keys, but the actual primary keys are
    # all empty...
    cvalues = merge_array_rows(
        cvalues, 'Construction_ID',
        ['Example_IDs', 'Reference_ID', 'Reference_pages'])
    lvalues = merge_array_rows(
        lvalues, 'Language_ID',
        ['Example_IDs', 'Reference_ID', 'Reference_pages'])
    examples = merge_array_rows(
        examples, 'ID', ['Reference_ID', 'Reference_pages'])

    # Fill in some missing fields
    lvalues = fill_with_previous(
        lvalues, ['Parameter_ID', 'Code_ID', 'Value'], 'Language_ID')
    lparam_guesser = ParameterGuesser(lcodes)
    lvalues = [lparam_guesser.fixed_row(row) for row in lvalues]
    cvalues = fill_with_previous(
        cvalues, ['Parameter_ID', 'Code_ID', 'Value'], 'Construction_ID')

    # Process data

    languages = list(map(remove_invalid_iso_codes, languages))

    try:
        # FIXME move the whole Glottolog stuff to somewhere sane
        catconf = cldfcatalog.Config.from_file()
        glottolog_path = catconf.get_clone('glottolog')
        glottolog_api = Glottolog(glottolog_path).api

        glottocode_by_iso = glottolog_api.glottocode_by_iso
        glottocode_by_name = {
            k: slug(v)
            for k, v in glottolog_api.glottocode_by_name.items()}

        def add_glottocode(language_row):
            if 'Glottocode' in language_row:
                return language_row
            iso = language_row.get('ISO639P3code')
            name = slug(language_row.get('Name') or '')
            if iso and glottocode_by_iso.get(iso):
                glottocode = glottocode_by_iso[iso]
            elif name and glottocode_by_name.get(name):
                glottocode = glottocode_by_name[name]
            else:
                return language_row
            new_row = dict(language_row)
            new_row['Glottocode'] = glottocode
            return new_row

        languages = list(map(add_glottocode, languages))
    except KeyError:
        print(
            'Warning: Could not find glottolog'
            ' -- check your `~/.config/cldf/catalog.ini`.',
            file=sys.stderr)

    lang_id_map = add_ids(LanguageIDMaker('lang'), languages)

    lparam_id_map = add_ids(SequentialIDMaker('lparam'), lparams)
    cparam_id_map = add_ids(SequentialIDMaker('cparam'), cparams)

    old_size = len(references)
    references, bibkey_map = add_bibkeys(references)
    if len(references) != old_size:
        # TODO Actually print out *which* rows are potential duplicates
        print(
            'dropped', old_size - len(references), 'out of', old_size,
            'references for being potential duplicates',
            file=sys.stderr)

    examples = fix_foreign_keys(
        examples, 'Language_ID', lang_id_map, 'examples')
    examples = fix_sources(examples, bibkey_map, 'examples')
    examples = drop_incomplete(
        examples, config['required_columns']['examples'], 'examples')
    # split glosses
    examples = [
        split_glosses(row, ('Gloss', 'Analyzed_Word'))
        for row in examples]
    # show warnings *before* IDs are rewritten, so they're still useful on the
    # filemaker side
    warn_about_misaligned_glosses(examples)
    example_id_map = add_ids(SequentialIDMaker('ex'), examples)

    constructions = fix_foreign_keys(
        constructions, 'Language_ID', lang_id_map, 'constructions')
    constructions = fix_foreign_keys(
        constructions, 'Example_IDs', example_id_map, 'constructions')
    constructions = fix_sources(constructions, bibkey_map, 'constructions')
    constructions = drop_incomplete(
        constructions, config['required_columns']['constructions'], 'constructions')
    constr_id_map = add_ids(SequentialIDMaker('constr'), constructions)

    lcodes = fix_foreign_keys(lcodes, 'Parameter_ID', lparam_id_map, 'l-codes')
    lcodes = drop_incomplete(
        lcodes, config['required_columns']['lcodes'], 'lcodes')
    lcode_id_map = add_ids(CodeIDMaker(lparam_id_map, 'c'), lcodes)
    lcodes = drop_duplicates(lcodes, ['Parameter_ID', 'Name'], lcode_id_map)

    ccodes = fix_foreign_keys(ccodes, 'Parameter_ID', cparam_id_map, 'c-codes')
    ccodes = drop_incomplete(
        ccodes, config['required_columns']['ccodes'], 'ccodes')
    ccode_id_map = add_ids(CodeIDMaker(cparam_id_map, 'c'), ccodes)
    ccodes = drop_duplicates(ccodes, ['Parameter_ID', 'Name'], ccode_id_map)

    lvalues = fix_foreign_keys(lvalues, 'Language_ID', lang_id_map, 'l-values')
    lvalues = fix_foreign_keys(lvalues, 'Parameter_ID', lparam_id_map, 'l-values')
    lvalues = fix_foreign_keys(lvalues, 'Code_ID', lcode_id_map, 'l-values')
    lvalues = fix_foreign_keys(lvalues, 'Example_IDs', example_id_map, 'l-values')
    lvalues = fix_sources(lvalues, bibkey_map, 'l-values')
    lvalues = drop_incomplete(
        lvalues, config['required_columns']['lvalues'], 'lvalues')
    add_ids(
        ValueIDMaker('Language_ID', lang_id_map, lparam_id_map, 'lval'),
        lvalues)

    # Satisfy UNIQUE constraint of clld's UnitValue table
    cvalues = drop_duplicates(
        cvalues,
        ['Construction_ID', 'Parameter_ID', 'Code_ID', 'Value'])
    cparam_guesser = ParameterGuesser(ccodes)
    cvalues = [cparam_guesser.fixed_row(row) for row in cvalues]

    cvalues = fix_foreign_keys(
        cvalues, 'Construction_ID', constr_id_map, 'c-codes')
    cvalues = fix_foreign_keys(
        cvalues, 'Parameter_ID', cparam_id_map, 'c-values')
    cvalues = fix_foreign_keys(
        cvalues, 'Code_ID', ccode_id_map, 'c-values')
    cvalues = fix_foreign_keys(
        cvalues, 'Example_IDs', example_id_map, 'c-values')
    cvalues = fix_sources(cvalues, bibkey_map, 'c-values')
    cvalues = drop_incomplete(
        cvalues, config['required_columns']['cvalues'], 'cvalues')
    add_ids(
        ValueIDMaker('Construction_ID', constr_id_map, cparam_id_map, 'cval'),
        cvalues)

    # Drop unused rows

    used_lparams = {v['Parameter_ID'] for v in lvalues if v.get('Parameter_ID')}
    lcodes = [c for c in lcodes if c.get('Parameter_ID') in used_lparams]
    used_cparams = {v['Parameter_ID'] for v in cvalues if v.get('Parameter_ID')}
    ccodes = [c for c in ccodes if c.get('Parameter_ID') in used_cparams]

    languages = drop_unused(
        languages,
        set(chain(
            (v['Language_ID'] for v in lvalues if v.get('Language_ID')),
            (c['Language_ID'] for c in constructions if c.get('Language_ID')),
            (e['Language_ID'] for e in examples if e.get('Language_ID')))),
        'language')

    def remove_page(cite):
        return re.sub(r'\[[^\]]*\]$', '', cite)

    references = drop_unused(
        references,
        set(chain(
            (remove_page(cite) for row in lvalues for cite in row.get('Source') or ()),
            (remove_page(cite) for row in constructions for cite in row.get('Source') or ()),
            (remove_page(cite) for row in cvalues for cite in row.get('Source') or ()),
            (remove_page(cite) for row in examples for cite in row.get('Source') or ()))),
        'reference')

    return {
        'languages': languages,
        'lparameters': lparams,
        'lcodes': lcodes,
        'lvalues': lvalues,
        'constructions': constructions,
        'cparameters': cparams,
        'ccodes': ccodes,
        'cvalues': cvalues,
        'examples': examples,
        'references': references}
