import unittest
from ditrans2cldf import bibliography as bib


class ParseNames(unittest.TestCase):

    def test_parse_a_single_person(self):
        names = 'Doe, John'
        result = bib.parse_people(names)
        self.assertTrue(result)
        self.assertEqual(result[0].first_names, ['John'])
        self.assertEqual(result[0].last_names, ['Doe'])

    def test_people_separated_by_and(self):
        names = 'Doe, Jane and Doe, John'
        result = bib.parse_people(names)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].first_names, ['Jane'])
        self.assertEqual(result[0].last_names, ['Doe'])
        self.assertEqual(result[1].first_names, ['John'])
        self.assertEqual(result[1].last_names, ['Doe'])

    def test_people_separated_by_ampersand(self):
        names = 'Doe, Jane & Doe, John'
        result = bib.parse_people(names)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].first_names, ['Jane'])
        self.assertEqual(result[0].last_names, ['Doe'])
        self.assertEqual(result[1].first_names, ['John'])
        self.assertEqual(result[1].last_names, ['Doe'])

    def test_people_separated_by_semicolon(self):
        names = 'Doe, Jane ; Doe, John'
        result = bib.parse_people(names)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].first_names, ['Jane'])
        self.assertEqual(result[0].last_names, ['Doe'])
        self.assertEqual(result[1].first_names, ['John'])
        self.assertEqual(result[1].last_names, ['Doe'])


class BibkeyGeneration(unittest.TestCase):

    def test_use_existing_bibkey_if_any(self):
        row = {
            'LaTeX_cite_key': 'key',
            'title': 'Title'}
        bibkey = bib.generate_bibkey(row)
        self.assertEqual(bibkey, 'key')

    def test_fall_back_to_id(self):
        row = {
            'ID': 1,
            'title': 'Title'}
        bibkey = bib.generate_bibkey(row)
        self.assertEqual(bibkey, '1')

    def test_single_author(self):
        row = {
            'author': 'John Doe',
            'year': 2019,
            'title': 'Title'}
        bibkey = bib.generate_bibkey(row)
        self.assertEqual(bibkey, 'doe-2019')

    def test_two_authors(self):
        row = {
            'author': 'Jane Doe and John Doe',
            'year': 2019,
            'title': 'Title'}
        bibkey = bib.generate_bibkey(row)
        self.assertEqual(bibkey, 'doe-doe-2019')

    def test_more_authors(self):
        row = {
            'author': 'Jane Doe and John Doe and Max Mustermann',
            'year': 2019,
            'title': 'Title'}
        bibkey = bib.generate_bibkey(row)
        self.assertEqual(bibkey, 'doe-etal-2019')

    def test_disambiguation_letter(self):
        row = {
            'author': 'John Doe',
            'year': 2019,
            'Year_disambiguation_letter': 'a',
            'title': 'Title'}
        bibkey = bib.generate_bibkey(row)
        self.assertEqual(bibkey, 'doe-2019a')

    def test_unicode_removal(self):
        row = {
            'author': "Hanka Dvořaková and Seamus O'Brien",
            'year': 2019,
            'title': 'Title'}
        bibkey = bib.generate_bibkey(row)
        self.assertEqual(bibkey, 'dvorakova-obrien-2019')
