import json
import itertools
import collections


# TODO Remove redundant fields
# TODO Use urls in column fields
DEFAULT_CONFIG = {

    'custom_columns': {
        'LanguageTable': [
            'ID', 'Name', 'Latitude', 'Longitude', 'Glottocode', 'ISO639P3code',
            'WALS_Code'],
        'ParameterTable': [
            'ID', 'Name', 'Description'],
        'CodeTable': [
            'ID', 'Parameter_ID', 'Name'],
        'ValueTable': [
            'ID', 'Language_ID', 'Parameter_ID', 'Example_IDs'],
        'constructions.csv': [
            'ID', 'Language_ID', 'Name', 'Description', 'Schema'],
        'cvalues.csv': [
            'ID', 'Construction_ID', 'Parameter_ID', 'Example_IDs'],
        'ExampleTable': [
            'ID', 'Language_ID', 'Primary_Text', 'Original_Orthography',
            'Translated_Text', 'Translation_Other', 'Analyzed_Text', 'Gloss',
            'Type', 'Comment']
    },

    'colname_maps': {
        'languages': {
            'Language_ID': 'ID',
            'Lotitude': 'Latitude',
            'ISO_code': 'ISO639P3code',
            'Language_name': 'Name'},
        'lparameters': {
            'Language_parameter_ID': 'ID',
            'Language_parameter_name': 'Name'},
        'lcodes': {
            'Language_parameter_value_name_ID': 'ID',
            'Language_parameter_ID': 'Parameter_ID',
            'Language_parameter_value_names_of_Language_data::Value_name': 'Name'},
        'lvalues': {
            'Value_Language_ID': 'ID',
            'Language_parameter_ID': 'Parameter_ID',
            'Language_parameter_value_name_ID': 'Code_ID',
            'Language_data_examples::Example_ID': 'Example_IDs',
            'Language_data_references::Reference_ID': 'Reference_ID',
            'Language_data_references::Pages': 'Reference_pages',
            'Value_description': 'Comment',
            'Language_parameter_value_names_of_Language_data::Value_name': 'Value'},
        'constructions': {
            'Construction_ID': 'ID',
            'Construction_name': 'Name',
            'Construction_schema': 'Schema',
            'Construction_examples::Example_ID': 'Example_IDs',
            'Construction_references::Reference_ID': 'Reference_ID',
            'Construction_references::Pages': 'Reference_pages',
            'Construction_meanings::Meaning_ID': 'Meaning_ID'},
        'cparameters': {
            'Construction_parameter_ID': 'ID',
            'Construction_parameter_name': 'Name'},
        'ccodes': {
            'Construction_parameter_value_name_ID': 'ID',
            'Construction_parameter_ID': 'Parameter_ID',
            'Construction_parameter_value_names_of_Construction_data::Value_name': 'Name'},
        'cvalues': {
            'Value_Construction_ID': 'ID',
            'Construction_parameter_ID': 'Parameter_ID',
            'Construction_parameter_value_name_ID': 'Code_ID',
            'Construction_data_examples::Example_ID': 'Example_IDs',
            'Construction_data_references::Reference_ID': 'Reference_ID',
            'Construction_data_references::Pages': 'Reference_pages',
            'Value_description': 'Comment',
            'Construction_parameter_value_names_of_Construction_data::Value_name': 'Value'},
        'examples': {
            'Example_ID': 'ID',
            'Original_orthography': 'Original_Orthography',
            'Analyzed_text': 'Analyzed_Word',
            'Primary_text': 'Primary_Text',
            'Translation': 'Translated_Text',
            'Translation_other': 'Translation_Other',
            'Example_type': 'Type',
            'Comments': 'Comment'
        }
    },

    'required_columns': {
        'lcodes': ['Parameter_ID'],
        'lvalues': ['Language_ID', 'Parameter_ID', 'Code_ID'],
        'constructions': ['Language_ID'],
        'ccodes': ['Parameter_ID'],
        'cvalues': ['Construction_ID', 'Parameter_ID', 'Code_ID'],
        'examples': ['Primary_Text', 'Language_ID']
    },

    'bibtex_map': {
        'Additional_information': 'note',
        'Article_title': 'title',
        'Authors': 'author',
        'Book_title': 'booktitle',
        'Chapter': 'chapter',
        'City': 'address',
        'Editors': 'editor',
        'Issue_number': 'number',
        'Journal': 'journal',
        'Pages': 'pages',
        'Publisher': 'publisher',
        'Reference_ID': 'ID',
        'School': 'school',
        'Series_title': 'series',
        'URL': 'url',
        'Volume': 'volume',
        'Year': 'year'
    },

    # XXX does this do anything yet?
    'tables_with_sources': ['ValueTable', 'ExampleTable', 'cvalues.csv']
}


def construct_config(json_data):
    json_maps = json_data.get('colname_maps') or {}
    json_cols = json_data.get('cols') or {}
    json_bibmap = json_data.get('bibtex_map') or {}
    json_req = json_data.get('required_columns') or {}

    colname_maps = {
        table_name: collections.ChainMap(json_maps.get(table_name) or {}, mapping)
        for table_name, mapping in DEFAULT_CONFIG['colname_maps'].items()}
    custom_columns = {
        table_name: sorted(set(itertools.chain(columns, json_cols.get(table_name) or ())))
        for table_name, columns in DEFAULT_CONFIG['custom_columns'].items()}
    required_columns = {
        table_name: sorted(set(itertools.chain(columns, json_req.get(table_name) or ())))
        for table_name, columns in DEFAULT_CONFIG['required_columns'].items()}
    bibtex_map = collections.ChainMap(json_bibmap, DEFAULT_CONFIG['bibtex_map'])
    tables_with_sources = sorted(set(itertools.chain(
        DEFAULT_CONFIG['tables_with_sources'],
        json_data.get('tables_with_sources') or ())))

    return {
        'colname_maps': colname_maps,
        'custom_columns': custom_columns,
        'required_columns': required_columns,
        'bibtex_map': bibtex_map,
        'tables_with_sources': tables_with_sources}


def load_config_file(filename):
    with open(filename, encoding='utf-8') as fptr:
        json_data = json.load(fptr)
    return construct_config(json_data)
