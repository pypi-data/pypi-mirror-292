import unittest
from ditrans2cldf import process as p


class TableExtraction(unittest.TestCase):

    def test_extract_table_from_another(self):
        original_table = [
            {'ID': 'id1', 'Data': 'val1', 'SubID': 'sid1', 'SubData': 'sval1'},
            {'ID': 'id2', 'Data': 'val2', 'SubID': 'sid2', 'SubData': 'sval2'}]
        result = p.extract_table(original_table, 'SubID', ['SubData'])
        expected = [
            {'SubID': 'sid1', 'SubData': 'sval1'},
            {'SubID': 'sid2', 'SubData': 'sval2'}]
        self.assertEqual(result, expected)

    def test_collapse_identical_rows(self):
        original_table = [
            {'ID': 'id1', 'Data': 'val1', 'SubID': 'sid1', 'SubData': 'sval1'},
            {'ID': 'id2', 'Data': 'val2', 'SubID': 'sid2', 'SubData': 'sval2'},
            {'ID': 'id3', 'Data': 'val3', 'SubID': 'sid1', 'SubData': 'sval1'}]
        result = p.extract_table(original_table, 'SubID', ['SubData'])
        expected = [
            {'SubID': 'sid1', 'SubData': 'sval1'},
            {'SubID': 'sid2', 'SubData': 'sval2'}]
        self.assertEqual(result, expected)

    def test_ignore_rows_with_missing_primary_key(self):
        original_table = [
            {'ID': 'id1', 'Data': 'val1', 'SubID': 'sid1', 'SubData': 'sval1'},
            {'ID': 'id2', 'Data': 'val2', 'SubData': 'sval2'},
            {'ID': 'id3', 'Data': 'val3', 'SubID': 'sid3', 'SubData': 'sval3'}]
        result = p.extract_table(original_table, 'SubID', ['SubData'])
        expected = [
            {'SubID': 'sid1', 'SubData': 'sval1'},
            {'SubID': 'sid3', 'SubData': 'sval3'}]
        self.assertEqual(result, expected)


class ColNameMapping(unittest.TestCase):

    def test_convert_column_names(self):
        row = {'col1': 'val1', 'col2': 'val2'}
        mapping = {'col1': 'new_col1', 'col2': 'new_col2'}
        result = p.map_colnames(row, mapping)
        expected = {'new_col1': 'val1', 'new_col2': 'val2'}
        self.assertEqual(result, expected)

    def test_leave_unmapped_columns_alone(self):
        row = {'col1': 'val1', 'col2': 'val2'}
        mapping = {'col1': 'new_col1'}
        result = p.map_colnames(row, mapping)
        expected = {'new_col1': 'val1', 'col2': 'val2'}
        self.assertEqual(result, expected)


class CodeNumbers(unittest.TestCase):

    def test_codes_are_numbered(self):
        code_table = [
            {'ID': 'id1', 'Parameter_ID': 'param1'},
            {'ID': 'id2', 'Parameter_ID': 'param1'},
            {'ID': 'id3', 'Parameter_ID': 'param1'}]
        new_table = p.add_code_numbers(code_table)
        expected = [
            {'ID': 'id1', 'Parameter_ID': 'param1', 'Number': 1},
            {'ID': 'id2', 'Parameter_ID': 'param1', 'Number': 2},
            {'ID': 'id3', 'Parameter_ID': 'param1', 'Number': 3}]
        self.assertEqual(new_table, expected)

    def test_codes_are_numbered_for_each_parameter(self):
        code_table = [
            {'ID': 'id1', 'Parameter_ID': 'param1'},
            {'ID': 'id2', 'Parameter_ID': 'param2'},
            {'ID': 'id3', 'Parameter_ID': 'param1'}]
        new_table = p.add_code_numbers(code_table)
        expected = [
            {'ID': 'id1', 'Parameter_ID': 'param1', 'Number': 1},
            {'ID': 'id2', 'Parameter_ID': 'param2', 'Number': 1},
            {'ID': 'id3', 'Parameter_ID': 'param1', 'Number': 2}]
        self.assertEqual(new_table, expected)

    def test_ignore_missing_param_id(self):
        code_table = [
            {'ID': 'id1', 'Parameter_ID': 'param1'},
            {'ID': 'id2', 'Parameter_ID': 'param1'},
            {'ID': 'id3'}]
        new_table = p.add_code_numbers(code_table)
        expected = [
            {'ID': 'id1', 'Parameter_ID': 'param1', 'Number': 1},
            {'ID': 'id2', 'Parameter_ID': 'param1', 'Number': 2},
            {'ID': 'id3'}]
        self.assertEqual(new_table, expected)


class MergeArrays(unittest.TestCase):

    def test_only_merge_if_necessary(self):
        key = 'ID'
        fields = ['Example_IDs']
        table = [
            {'ID': 'id1', 'Example_IDs': 'ex1'},
            {'ID': 'id2', 'Example_IDs': 'ex2'},
            {'ID': 'id3', 'Example_IDs': 'ex3'}]
        new_table = p.merge_array_rows(table, key, fields)
        # I want all array fields consistently to be lists
        expected = [
            {'ID': 'id1', 'Example_IDs': ['ex1']},
            {'ID': 'id2', 'Example_IDs': ['ex2']},
            {'ID': 'id3', 'Example_IDs': ['ex3']}]
        self.assertEqual(new_table, expected)

    def test_row_with_missing_primary_key(self):
        key = 'ID'
        fields = ['Example_IDs']
        table = [
            {'ID': 'id1', 'Example_IDs': 'ex1'},
            {'Example_IDs': 'ex2'},
            {'ID': 'id3', 'Example_IDs': 'ex3'}]
        new_table = p.merge_array_rows(table, key, fields)
        expected = [
            {'ID': 'id1', 'Example_IDs': ['ex1', 'ex2']},
            {'ID': 'id3', 'Example_IDs': ['ex3']}]
        self.assertEqual(new_table, expected)

    def test_missing_merge_field_lhs(self):
        key = 'ID'
        fields = ['Example_IDs']
        table = [
            {'ID': 'id1'},
            {'Example_IDs': 'ex2'},
            {'ID': 'id3', 'Example_IDs': 'ex3'}]
        new_table = p.merge_array_rows(table, key, fields)
        expected = [
            {'ID': 'id1', 'Example_IDs': ['ex2']},
            {'ID': 'id3', 'Example_IDs': ['ex3']}]
        self.assertEqual(new_table, expected)

    def test_missing_merge_field_rhs(self):
        key = 'ID'
        fields = ['Example_IDs']
        table = [
            {'ID': 'id1', 'Example_IDs': 'ex1'},
            {},
            {'ID': 'id3', 'Example_IDs': 'ex3'}]
        new_table = p.merge_array_rows(table, key, fields)
        expected = [
            {'ID': 'id1', 'Example_IDs': ['ex1']},
            {'ID': 'id3', 'Example_IDs': ['ex3']}]
        self.assertEqual(new_table, expected)

    def test_missing_merge_fields_both_sides(self):
        key = 'ID'
        fields = ['Example_IDs']
        table = [
            {'ID': 'id1'},
            {},
            {'ID': 'id3', 'Example_IDs': 'ex3'}]
        new_table = p.merge_array_rows(table, key, fields)
        expected = [
            {'ID': 'id1'},
            {'ID': 'id3', 'Example_IDs': ['ex3']}]
        self.assertEqual(new_table, expected)

    def test_merge_multiple_rows(self):
        key = 'ID'
        fields = ['Example_IDs']
        table = [
            {'ID': 'id1', 'Example_IDs': 'ex1'},
            {'Example_IDs': 'ex2'},
            {'Example_IDs': 'ex3'}]
        new_table = p.merge_array_rows(table, key, fields)
        expected = [
            {'ID': 'id1', 'Example_IDs': ['ex1', 'ex2', 'ex3']}]
        self.assertEqual(new_table, expected)

    def test_first_elem_lacks_primary_key(self):
        key = 'ID'
        fields = ['Example_IDs']
        table = [
            {'Example_IDs': 'ex1'},
            {'Example_IDs': 'ex2'},
            {'ID': 'id3', 'Example_IDs': 'ex3'}]
        new_table = p.merge_array_rows(table, key, fields)
        expected = [
            {'Example_IDs': ['ex1', 'ex2']},
            {'ID': 'id3', 'Example_IDs': ['ex3']}]
        self.assertEqual(new_table, expected)


class FillEmptyFields(unittest.TestCase):

    def test_fill_fields_with_previous(self):
        table = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1'},
            {'Breaker': '1', 'ID': 'id2'},
            {'Breaker': '3', 'ID': 'id3', 'Column1': 'val3'}]
        new_table = p.fill_with_previous(table, ['Column1'], 'Breaker')
        expected = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1'},
            {'Breaker': '1', 'ID': 'id2', 'Column1': 'val1'},
            {'Breaker': '3', 'ID': 'id3', 'Column1': 'val3'}]
        self.assertEqual(new_table, expected)

    def test_cant_fill_first_row(self):
        table = [
            {'Breaker': '1', 'ID': 'id1'},
            {'Breaker': '1', 'ID': 'id2', 'Column1': 'val2'},
            {'Breaker': '3', 'ID': 'id3', 'Column1': 'val3'}]
        new_table = p.fill_with_previous(table, ['Column1'], 'Breaker')
        expected = [
            {'Breaker': '1', 'ID': 'id1'},
            {'Breaker': '1', 'ID': 'id2', 'Column1': 'val2'},
            {'Breaker': '3', 'ID': 'id3', 'Column1': 'val3'}]
        self.assertEqual(new_table, expected)

    def test_keep_filling(self):
        table = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1'},
            {'Breaker': '1', 'ID': 'id2'},
            {'Breaker': '1', 'ID': 'id3'},
            {'Breaker': '4', 'ID': 'id4', 'Column1': 'val4'}]
        new_table = p.fill_with_previous(table, ['Column1'], 'Breaker')
        expected = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1'},
            {'Breaker': '1', 'ID': 'id2', 'Column1': 'val1'},
            {'Breaker': '1', 'ID': 'id3', 'Column1': 'val1'},
            {'Breaker': '4', 'ID': 'id4', 'Column1': 'val4'}]
        self.assertEqual(new_table, expected)

    def test_stop_when_breaker_changes(self):
        table = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1'},
            {'Breaker': '1', 'ID': 'id2'},
            {'Breaker': '3', 'ID': 'id3'},
            {'Breaker': '4', 'ID': 'id4', 'Column1': 'val4'}]
        new_table = p.fill_with_previous(table, ['Column1'], 'Breaker')
        expected = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1'},
            {'Breaker': '1', 'ID': 'id2', 'Column1': 'val1'},
            {'Breaker': '3', 'ID': 'id3'},
            {'Breaker': '4', 'ID': 'id4', 'Column1': 'val4'}]
        self.assertEqual(new_table, expected)

    def test_fill_multiple(self):
        table = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1', 'Column2': 'val1b'},
            {'Breaker': '1', 'ID': 'id2'},
            {'Breaker': '3', 'ID': 'id3', 'Column1': 'val3', 'Column2': 'val3b'}]
        new_table = p.fill_with_previous(table, ['Column1', 'Column2'], 'Breaker')
        expected = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1', 'Column2': 'val1b'},
            {'Breaker': '1', 'ID': 'id2', 'Column1': 'val1', 'Column2': 'val1b'},
            {'Breaker': '3', 'ID': 'id3', 'Column1': 'val3', 'Column2': 'val3b'}]
        self.assertEqual(new_table, expected)

    def test_dont_override_columns(self):
        table = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1', 'Column2': 'val1b'},
            {'Breaker': '1', 'ID': 'id2'},
            {'Breaker': '1', 'ID': 'id3', 'Column1': 'val3'},
            {'Breaker': '1', 'ID': 'id4'}]
        new_table = p.fill_with_previous(table, ['Column1', 'Column2'], 'Breaker')
        expected = [
            {'Breaker': '1', 'ID': 'id1', 'Column1': 'val1', 'Column2': 'val1b'},
            {'Breaker': '1', 'ID': 'id2', 'Column1': 'val1', 'Column2': 'val1b'},
            {'Breaker': '1', 'ID': 'id3', 'Column1': 'val3'},
            {'Breaker': '1', 'ID': 'id4', 'Column1': 'val3'}]
        self.assertEqual(new_table, expected)


class DropDuplicats(unittest.TestCase):

    def test_duplicates_are_dropped(self):
        table = [
            {'Unique1': 'unique1.1', 'Unique2': 'unique2.1'},
            {'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'Unique1': 'unique1.3', 'Unique2': 'unique2.3'}]
        new_table = p.drop_duplicates(table, ['Unique1', 'Unique2'])
        expected = [
            {'Unique1': 'unique1.1', 'Unique2': 'unique2.1'},
            {'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'Unique1': 'unique1.3', 'Unique2': 'unique2.3'}]
        self.assertEqual(new_table, expected)

    def test_one_difference_is_enough(self):
        table = [
            {'Unique1': 'unique1.1', 'Unique2': 'unique2.1'},
            {'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'Unique1': 'unique1.2', 'Unique2': 'unique2.4'},
            {'Unique1': 'unique1.3', 'Unique2': 'unique2.3'}]
        new_table = p.drop_duplicates(table, ['Unique1', 'Unique2'])
        expected = [
            {'Unique1': 'unique1.1', 'Unique2': 'unique2.1'},
            {'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'Unique1': 'unique1.2', 'Unique2': 'unique2.4'},
            {'Unique1': 'unique1.3', 'Unique2': 'unique2.3'}]
        self.assertEqual(new_table, expected)

    def test_ignore_other_columns(self):
        table = [
            {'ID': 'id1', 'Unique1': 'unique1.1', 'Unique2': 'unique2.1'},
            {'ID': 'id2', 'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'ID': 'id3', 'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'ID': 'id4', 'Unique1': 'unique1.3', 'Unique2': 'unique2.3'}]
        new_table = p.drop_duplicates(table, ['Unique1', 'Unique2'])
        expected = [
            {'ID': 'id1', 'Unique1': 'unique1.1', 'Unique2': 'unique2.1'},
            {'ID': 'id2', 'Unique1': 'unique1.2', 'Unique2': 'unique2.2'},
            {'ID': 'id4', 'Unique1': 'unique1.3', 'Unique2': 'unique2.3'}]
        self.assertEqual(new_table, expected)


class FilterInvalidISOCodes(unittest.TestCase):

    def test_valid_isocodes_are_left_untouched(self):
        row = {'ID': 'id', 'ISO639P3code': 'abc'}
        result = p.remove_invalid_iso_codes(row)
        expected = {'ID': 'id', 'ISO639P3code': 'abc'}
        self.assertEqual(result, expected)

    def test_no_isocodes_with_more_than_three_letters(self):
        row = {'ID': 'id', 'ISO639P3code': 'abcd'}
        result = p.remove_invalid_iso_codes(row)
        expected = {'ID': 'id'}
        self.assertEqual(result, expected)

    def test_no_isocodes_with_less_than_three_letters(self):
        row = {'ID': 'id', 'ISO639P3code': 'ab'}
        result = p.remove_invalid_iso_codes(row)
        expected = {'ID': 'id'}
        self.assertEqual(result, expected)

    def test_isocode_must_be_lower_case_letters(self):
        table = [
            {'ID': 'id1', 'ISO639P3code': 'ab1'},
            {'ID': 'id2', 'ISO639P3code': 'ab!'},
            {'ID': 'id3', 'ISO639P3code': 'abC'}]
        result = [p.remove_invalid_iso_codes(row) for row in table]
        expected = [
            {'ID': 'id1'},
            {'ID': 'id2'},
            {'ID': 'id3'}]
        self.assertEqual(result, expected)


class GuessParamUsingCode(unittest.TestCase):

    def setUp(self):
        codes = [
            {'ID': 'code1', 'Parameter_ID': 'param1', 'Name': '1a'},
            {'ID': 'code2', 'Parameter_ID': 'param1', 'Name': '1b'},
            {'ID': 'code3', 'Parameter_ID': 'param2', 'Name': '2a'},
            {'ID': 'code4', 'Parameter_ID': 'param2', 'Name': '2b'}]
        self.guesser = p.ParameterGuesser(codes)

    def test_fix_missing_param_id(self):
        value_row = {'ID': 'val1', 'Code_ID': 'code2'}
        result = self.guesser.fixed_row(value_row)
        expected = {'ID': 'val1', 'Code_ID': 'code2', 'Parameter_ID': 'param1'}
        self.assertEqual(result, expected)


class EnsureRequiredColumns(unittest.TestCase):

    def test_drop_incomplete_rows(self):
        rows = [
            {'ID': 'id1', 'Required1': 'req1.1', 'Required2': 'req2.1'},
            {'ID': 'id2', 'Required1': 'req1.2'},
            {'ID': 'id3', 'Required2': 'req2.3'},
            {'ID': 'id4'}]
        required_columns = ['Required1', 'Required2']
        result = p.drop_incomplete(rows, required_columns)
        expected = [{'ID': 'id1', 'Required1': 'req1.1', 'Required2': 'req2.1'}]
        self.assertEqual(result, expected)


class SplitGlosses(unittest.TestCase):

    def test_split_field_at_whitespace(self):
        row = {'gloss': 'a b\tc'}
        gloss_fields = ['gloss']
        result = p.split_glosses(row, gloss_fields)
        expected = {'gloss': ['a', 'b', 'c']}
        self.assertEqual(result, expected)

    def test_leave_other_fields_alone(self):
        row = {'not-gloss': 'a b\tc'}
        gloss_fields = ['gloss']
        result = p.split_glosses(row, gloss_fields)
        expected = {'not-gloss': 'a b\tc'}
        self.assertEqual(result, expected)


class IDUniqueness(unittest.TestCase):

    def test_add_suffix_to_duplicated_ids(self):
        id1 = 'same-id'
        id2 = 'same-id'
        unique_maker = p.IDUniqueMaker()
        result1 = unique_maker.unique_id(id1)
        result2 = unique_maker.unique_id(id2)
        self.assertEqual(result1, 'same-id')
        self.assertEqual(result2, 'same-id-2')

    def test_deal_with_existing_suffix(self):
        id1 = 'same-id'
        id2 = 'same-id-2'
        id3 = 'same-id'
        unique_maker = p.IDUniqueMaker()
        result1 = unique_maker.unique_id(id1)
        result2 = unique_maker.unique_id(id2)
        result3 = unique_maker.unique_id(id3)
        self.assertEqual(result1, 'same-id')
        self.assertEqual(result2, 'same-id-2')
        self.assertEqual(result3, 'same-id-3')

    def test_deal_with_conflicting_suffix(self):
        id1 = 'same-id'
        id2 = 'same-id'
        id3 = 'same-id-2'
        unique_maker = p.IDUniqueMaker()
        result1 = unique_maker.unique_id(id1)
        result2 = unique_maker.unique_id(id2)
        result3 = unique_maker.unique_id(id3)
        self.assertEqual(result1, 'same-id')
        self.assertEqual(result2, 'same-id-2')
        self.assertEqual(result3, 'same-id-2-2')


class SequentialIDs(unittest.TestCase):

    def test_make_unique_ids(self):
        row = {'ID': 'old id 1', 'Data': 'Value 1'}
        different_row = {'ID': 'old id 2', 'Data': 'Value 2'}
        id_maker = p.SequentialIDMaker()
        id1 = id_maker.make_id(row)
        id2 = id_maker.make_id(different_row)
        self.assertEqual(id1, '1')
        self.assertEqual(id2, '2')

    def test_add_prefix_to_ids(self):
        row = {'ID': 'old id 1', 'Data': 'Value 1'}
        different_row = {'ID': 'old id 2', 'Data': 'Value 2'}
        id_maker = p.SequentialIDMaker('pre')
        id1 = id_maker.make_id(row)
        id2 = id_maker.make_id(different_row)
        self.assertEqual(id1, 'pre1')
        self.assertEqual(id2, 'pre2')


class CodeIDs(unittest.TestCase):

    def setUp(self):
        self.param_id_map = {
            'old_id_1': 'new_id_1',
            'old_id_2': 'new_id_2'}

    def test_make_ids_based_on_parameter(self):
        code_row = {'Parameter_ID': 'old_id_1', 'Number': 1}
        id_maker = p.CodeIDMaker(self.param_id_map)
        id_ = id_maker.make_id(code_row)
        self.assertEqual(id_, 'new_id_1-1')

    def test_add_prefix_before_code_number(self):
        code_row = {'Parameter_ID': 'old_id_1', 'Number': 1}
        id_maker = p.CodeIDMaker(self.param_id_map, 'c')
        id_ = id_maker.make_id(code_row)
        self.assertEqual(id_, 'new_id_1-c1')

    def test_fall_back_to_sequential_ids(self):
        code_row1 = {'Parameter_ID': 'old_id_1'}
        code_row2 = {'Number': 1}
        id_maker = p.CodeIDMaker(self.param_id_map)
        id1 = id_maker.make_id(code_row1)
        id2 = id_maker.make_id(code_row2)
        self.assertEqual(id1, '1')
        self.assertEqual(id2, '2')

    def test_fall_back_supports_prefix(self):
        code_row1 = {'Parameter_ID': 'old_id_1'}
        code_row2 = {'Number': 1}
        id_maker = p.CodeIDMaker(self.param_id_map, 'c')
        id1 = id_maker.make_id(code_row1)
        id2 = id_maker.make_id(code_row2)
        self.assertEqual(id1, 'c1')
        self.assertEqual(id2, 'c2')


class LanguageIDs(unittest.TestCase):

    def test_prefer_glottocode(self):
        lang = {
            'ID': 'lang_id',
            'Glottocode': 'abcd1234',
            'ISO639P3code': 'abc',
            'Name': 'Language Name',
            'Description': 'This is a language'}
        id_maker = p.LanguageIDMaker()
        result = id_maker.make_id(lang)
        self.assertEqual(result, 'abcd1234')

    def test_fallback_to_iso639_code(self):
        lang = {
            'ID': 'lang_id',
            'ISO639P3code': 'abc',
            'Name': 'Language Name',
            'Description': 'This is a language'}
        id_maker = p.LanguageIDMaker()
        result = id_maker.make_id(lang)
        self.assertEqual(result, 'abc')

    def test_fallback_to_normalised_name(self):
        lang = {
            'ID': 'lang_id',
            'Name': 'Language Name',
            'Description': 'This is a language'}
        id_maker = p.LanguageIDMaker()
        result = id_maker.make_id(lang)
        self.assertEqual(result, 'languagename')

    def test_fallback_to_old_id(self):
        lang = {
            'ID': 'lang_id',
            'Description': 'This is a language'}
        id_maker = p.LanguageIDMaker()
        result = id_maker.make_id(lang)
        self.assertEqual(result, 'lang_id')

    def test_fallback_to_seq_number(self):
        lang = {
            'Description': 'This is a language'}
        id_maker = p.LanguageIDMaker()
        result = id_maker.make_id(lang)
        self.assertEqual(result, '1')

    def test_seq_number_supports_prefix(self):
        lang1 = {
            'Description': 'This is a language'}
        lang2 = {
            'Description': 'This is another language'}
        id_maker = p.LanguageIDMaker()
        id1 = id_maker.make_id(lang1)
        id2 = id_maker.make_id(lang2)
        self.assertEqual(id1, '1')
        self.assertEqual(id2, '2')

    def test_uniqueness(self):
        lang1 = {
            'ID': 'lang_id',
            'Glottocode': 'abcd1234',
            'ISO639P3code': 'abc',
            'Name': 'Language Name',
            'Description': 'These two are identical'}
        lang2 = {
            'ID': 'lang_id',
            'Glottocode': 'abcd1234',
            'ISO639P3code': 'abc',
            'Name': 'Language Name',
            'Description': 'These two are identical'}
        id_maker = p.LanguageIDMaker()
        id1 = id_maker.make_id(lang1)
        id2 = id_maker.make_id(lang2)
        self.assertEqual(id1, 'abcd1234')
        self.assertEqual(id2, 'abcd1234-2')


class ValueIDs(unittest.TestCase):

    def setUp(self):
        self.unit_id_map = {
            'old_unit_1': 'new_unit_1',
            'old_unit_2': 'new_unit_2'}
        self.param_id_map = {
            'old_param_1': 'new_param_1',
            'old_param_2': 'new_param_2'}

    def test_make_ids(self):
        row = {'Parameter_ID': 'old_param_1', 'Unit_ID': 'old_unit_1'}
        different_row = {'Parameter_ID': 'old_param_2', 'Unit_ID': 'old_unit_2'}
        id_maker = p.ValueIDMaker(
            'Unit_ID', self.unit_id_map, self.param_id_map)
        id1 = id_maker.make_id(row)
        id2 = id_maker.make_id(different_row)
        self.assertEqual(id1, 'new_unit_1-new_param_1')
        self.assertEqual(id2, 'new_unit_2-new_param_2')

    def test_ensure_uniqueness(self):
        row = {'Parameter_ID': 'old_param_1', 'Unit_ID': 'old_unit_1'}
        same_row = {'Parameter_ID': 'old_param_1', 'Unit_ID': 'old_unit_1'}
        id_maker = p.ValueIDMaker(
            'Unit_ID', self.unit_id_map, self.param_id_map)
        id1 = id_maker.make_id(row)
        id2 = id_maker.make_id(same_row)
        self.assertEqual(id1, 'new_unit_1-new_param_1')
        self.assertEqual(id2, 'new_unit_1-new_param_1-2')

    def test_fallback_to_sequential_ids(self):
        row1 = {'Parameter_ID': 'old_param_1'}
        row2 = {'Unit_ID': 'old_unit_1'}
        id_maker = p.ValueIDMaker(
            'Unit_ID', self.unit_id_map, self.param_id_map)
        id1 = id_maker.make_id(row1)
        id2 = id_maker.make_id(row2)
        self.assertEqual(id1, '1')
        self.assertEqual(id2, '2')

    def test_sequential_ids_support_prefix(self):
        row1 = {'Parameter_ID': 'old_param_1'}
        row2 = {'Unit_ID': 'old_unit_1'}
        id_maker = p.ValueIDMaker(
            'Unit_ID', self.unit_id_map, self.param_id_map, 'val')
        id1 = id_maker.make_id(row1)
        id2 = id_maker.make_id(row2)
        self.assertEqual(id1, 'val1')
        self.assertEqual(id2, 'val2')


class ForeignKeyCorrection(unittest.TestCase):

    def test_correct_foreign_keys(self):
        table = [
            {'foreign': 'old id 1'},
            {'foreign': 'old id 2'}]
        id_map = {
            'old id 1': 'new id 1',
            'old id 2': 'new id 2'}
        result = p.fix_foreign_keys(table, 'foreign', id_map)
        expected = [
            {'foreign': 'new id 1'},
            {'foreign': 'new id 2'}]
        self.assertEqual(result, expected)

    def test_leave_other_columns_alone(self):
        table = [
            {'not foreign': 'old id 1'},
            {'not foreign': 'old id 2'}]
        id_map = {
            'old id 1': 'new id 1',
            'old id 2': 'new id 2'}
        result = p.fix_foreign_keys(table, 'foreign', id_map)
        expected = [
            {'not foreign': 'old id 1'},
            {'not foreign': 'old id 2'}]
        self.assertEqual(result, expected)

    def test_drop_nonexistent_keys(self):
        table = [
            {'foreign': 'not old id 1'},
            {'foreign': 'not old id 2'}]
        id_map = {
            'old id 1': 'new id 1',
            'old id 2': 'new id 2'}
        result = p.fix_foreign_keys(table, 'foreign', id_map)
        expected = [
            {},
            {}]
        self.assertEqual(result, expected)

    def test_correct_foreign_key_arrays(self):
        table = [
            {'foreign': ['old id 1', 'old id 2']},
            {'foreign': ['old id 3', 'old id 4']}]
        id_map = {
            'old id 1': 'new id 1',
            'old id 2': 'new id 2',
            'old id 3': 'new id 3',
            'old id 4': 'new id 4'}
        result = p.fix_foreign_keys(table, 'foreign', id_map)
        expected = [
            {'foreign': ['new id 1', 'new id 2']},
            {'foreign': ['new id 3', 'new id 4']}]
        self.assertEqual(result, expected)

    def test_correct_drop_nonexistent_ids_in_arrays(self):
        table = [
            {'foreign': ['old id 1', 'not old id 2']},
            {'foreign': ['old id 3', 'not old id 4']}]
        id_map = {
            'old id 1': 'new id 1',
            'old id 2': 'new id 2',
            'old id 3': 'new id 3',
            'old id 4': 'new id 4'}
        result = p.fix_foreign_keys(table, 'foreign', id_map)
        expected = [
            {'foreign': ['new id 1']},
            {'foreign': ['new id 3']}]
        self.assertEqual(result, expected)

    def test_deal_with_ids_that_are_not_strings(self):
        table = [
            {'foreign': 1},
            {'foreign': 2}]
        id_map = {
            '1': 'new 1',
            '2': 'new 2'}
        result = p.fix_foreign_keys(table, 'foreign', id_map)
        expected = [
            {'foreign': 'new 1'},
            {'foreign': 'new 2'}]
        self.assertEqual(result, expected)

    def test_non_string_ids_in_arrays(self):
        table = [
            {'foreign': [1, 2]},
            {'foreign': [3, 4]}]
        id_map = {
            '1': 'new 1',
            '2': 'new 2',
            '3': 'new 3',
            '4': 'new 4'}
        result = p.fix_foreign_keys(table, 'foreign', id_map)
        expected = [
            {'foreign': ['new 1', 'new 2']},
            {'foreign': ['new 3', 'new 4']}]
        self.assertEqual(result, expected)
