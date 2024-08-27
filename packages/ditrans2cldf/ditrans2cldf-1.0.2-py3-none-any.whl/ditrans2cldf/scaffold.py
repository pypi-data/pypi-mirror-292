import sys
import pathlib

from cldfbench import CLDFSpec, CLDFWriter
from cldfbench import scaffold

import ditrans2cldf


class DitransDBWriter(CLDFWriter):
    """CLDF Writer which adds construction parameters to a StructureDataset."""

    def __enter__(self):
        super().__enter__()

        self.cldf.add_component('LanguageTable')
        self.cldf.add_component('ParameterTable')
        self.cldf.add_component('CodeTable')
        self.cldf.add_component('ExampleTable')

        self.cldf.add_columns(
            'CodeTable',
            {
                'datatype': 'integer',
                'name': 'Number',
            })

        self.cldf.add_columns(
            'ValueTable',
            {
                'datatype': {'base': 'string', 'format': '[a-zA-Z0-9_\\-]+'},
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#exampleReference',
                'separator': ';',
                'name': 'Example_IDs',
            })

        self.cldf.add_columns(
            'ExampleTable',
            'http://cldf.clld.org/v1.0/terms.rdf#source')

        self.cldf.add_table(
            'constructions.csv',
            'http://cldf.clld.org/v1.0/terms.rdf#id',
            'http://cldf.clld.org/v1.0/terms.rdf#languageReference',
            'http://cldf.clld.org/v1.0/terms.rdf#name',
            'http://cldf.clld.org/v1.0/terms.rdf#description',
            {
                'datatype': {'base': 'string', 'format': '[a-zA-Z0-9_\\-]+'},
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#exampleReference',
                'separator': ';',
                'name': 'Example_IDs',
            },
            'http://cldf.clld.org/v1.0/terms.rdf#source')
        self.cldf['constructions.csv'].tableSchema.get_column('ID').required = True
        self.cldf['constructions.csv'].tableSchema.get_column('Language_ID').required = True

        self.cldf.add_table(
            'cvalues.csv',
            'http://cldf.clld.org/v1.0/terms.rdf#id',
            {
                'datatype': {'base': 'string', 'format': '[a-zA-Z0-9_\\-]+'},
                'required': True,
                'name': 'Construction_ID',
            },
            'http://cldf.clld.org/v1.0/terms.rdf#parameterReference',
            'http://cldf.clld.org/v1.0/terms.rdf#codeReference',
            {
                'datatype': {'base': 'string', 'format': '[a-zA-Z0-9_\\-]+'},
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#exampleReference',
                'separator': ';',
                'name': 'Example_IDs',
            },
            'http://cldf.clld.org/v1.0/terms.rdf#source',
            'http://cldf.clld.org/v1.0/terms.rdf#value',
            'http://cldf.clld.org/v1.0/terms.rdf#comment')
        self.cldf['cvalues.csv'].tableSchema.get_column('ID').required = True
        self.cldf['cvalues.csv'].add_foreign_key('Construction_ID', 'constructions.csv', 'ID')

        return self


def cldfspec(cldf_dir):
    return CLDFSpec(
        dir=cldf_dir,
        metadata_fname='cldf-metadata.json',
        module='StructureDataset',
        writer_cls=DitransDBWriter)


class DitransDBTemplate(scaffold.Template):
    dirs = [pathlib.Path(ditrans2cldf.__file__).parent / 'dataset_template']


def add_custom_columns(dataset, config):
    if 'custom_columns' not in config:
        return
    for table_name, columns in config['custom_columns'].items():
        # TODO check if table actuallyexists
        # if table_name not in dataset.tables:
        #     continue
        for column in columns:
            try:
                dataset.add_columns(table_name, column)
            except ValueError as error:
                # Ignore columns that are already there
                # but warn about other errors
                msg = str(error)
                if not msg.startswith('Duplicate column name:'):
                    print(
                        '%s: couldn not add column: %s' % (table_name, msg),
                        file=sys.stderr)
