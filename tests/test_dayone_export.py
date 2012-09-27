import unittest
import dayone_export as doe
import dayone_export.cli
from mock import patch
import os
import jinja2

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class TestEntryObject(unittest.TestCase):
    def setUp(self):
        self.entry = doe.Entry('tests/fake_journal/entries/full.doentry')
        self.entry.set_photo('foo')
        self.no_location = doe.Entry('tests/fake_journal/entries/00-first.doentry')

    def test_tag_parsing(self):
        self.assertEqual(self.entry.data['Tags'], ['tag'])

    def test_set_photo(self):
        self.assertEqual(self.entry.data['Photo'], 'foo')

    def test_place_no_arguments(self):
        expected = 'Zoo, Seattle, Washington, United States'
        actual = self.entry.place()
        self.assertEqual(expected, actual)

    def test_place_int_argument(self):
        expected = 'Zoo, Seattle, Washington'
        actual = self.entry.place(3)
        self.assertEqual(expected, actual)

    def test_place_range_argument(self):
        expected = 'Seattle, Washington'
        actual = self.entry.place(1,3)
        self.assertEqual(expected, actual)

    def test_place_list_argument(self):
        expected = 'Seattle, United States'
        actual = self.entry.place([1, 3])
        self.assertEqual(expected, actual)

    def test_place_no_location(self):
        self.assertEqual(self.no_location.place(), "")

    def test_place_ignore_argument(self):
        expected = 'Washington'
        actual = self.entry.place(2, 3, ignore='United States')
        self.assertEqual(expected, actual)

    def test_getitem_data_key(self):
        self.assertEqual(self.entry['Photo'], 'foo')

    def test_getitem_text(self):
        self.assertEqual(self.entry['Text'], self.entry['Entry Text'])

    def test_getitem_date(self):
        self.assertEqual(self.entry['Date'], self.entry['Creation Date'])

    def test_getitem_raises_keyerror(self):
        self.assertRaises(KeyError, lambda:self.entry['foo'])

    def test_getitem_flattened_dict(self):
        self.assertEqual(self.entry['Country'], self.entry['Location']['Country'])

    def test_get_keys_are_actually_keys(self):
        for key in self.entry.keys():
            self.assertTrue(key in self.entry, key)

class TestJournalParser(unittest.TestCase):
    def setUp(self):
        self.j = doe.parse_journal('tests/fake_journal')
        self.reversed = doe.parse_journal('tests/fake_journal', reverse=True)

    def test_automatically_set_photos(self):
        expected = 'photos/00F9FA96F29043D09638DF0866EC73B2.jpg'
        actual = self.j[0]['Photo']
        self.assertEqual(expected, actual)

    def test_sort_order(self):
        j = self.j
        result = j[0]['Date'] <= j[1]['Date'] <= j[2]['Date']
        self.assertTrue(result)

    def test_sort_order(self):
        j = self.reversed
        result = j[2]['Date'] <= j[1]['Date'] <= j[0]['Date']
        self.assertTrue(result)

    @patch('jinja2.Template.render')
    def test_dayone_export_run(self, mock_render):
        doe.dayone_export('tests/fake_journal')
        mock_render.assert_called()

    def test_after_filter(self):
        filtered = doe._filter_by_after_date(self.j, "2012-09-01", "utc")
        self.assertEqual(len(filtered), 1)

    def test_tags_any_tag(self):
        filtered = doe._filter_by_tag(self.j, 'any')
        self.assertEqual(len(filtered), 1)

    def test_tags_one_tag(self):
        filtered = doe._filter_by_tag(self.j, ['tag'])
        self.assertEqual(len(filtered), 1)

    def test_tags_no_matches(self):
        filtered = doe._filter_by_tag(self.j, ['porcupine'])
        self.assertEqual(len(filtered), 0)

class TestTemplateInheritance(unittest.TestCase):
    def setUp(self):
        self.patcher1 = patch('jinja2.ChoiceLoader', side_effect=lambda x:x)
        self.patcher2 = patch('jinja2.FileSystemLoader', side_effect=lambda x:x)
        self.patcher3 = patch('jinja2.PackageLoader', side_effect=lambda x:x)
        self.patcher1.start()
        self.patcher2.start()
        self.patcher3.start()
        self.dir = os.path.expanduser('~/.dayone_export')

    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()

    def test_explicit_template(self):
        actual = doe._determine_inheritance('a/b', 'ccc', 'ddd')
        expected = 'a', 'b'
        self.assertEqual(actual, expected)

    def test_no_template_no_dir_no_format(self):
        actual = doe._determine_inheritance(None, None, None)
        expected = [[self.dir], 'dayone_export'], 'default.html'
        self.assertEqual(actual, expected)

    def test_yes_template_no_dir_no_format(self):
        actual = doe._determine_inheritance('foo', None, None)
        expected = [['.', self.dir], 'dayone_export'], 'foo'
        self.assertEqual(actual, expected)

    def test_no_template_yes_dir_no_format(self):
        actual = doe._determine_inheritance(None, 'bar', None)
        expected = 'bar', 'default.html'
        self.assertEqual(actual, expected)

    def test_yes_template_yes_dir_no_format(self):
        actual = doe._determine_inheritance('foo', 'bar', None)
        expected = 'bar', 'foo'
        self.assertEqual(actual, expected)

    def test_no_template_no_dir_yes_format(self):
        actual = doe._determine_inheritance(None, None, 'text')
        expected = [[self.dir], 'dayone_export'], 'default.text'
        self.assertEqual(actual, expected)

    def test_yes_template_no_dir_yes_format(self):
        actual = doe._determine_inheritance('foo', None , 'text')
        expected = [['.', self.dir], 'dayone_export'], 'foo'
        self.assertEqual(actual, expected)

    def test_no_template_yes_dir_yes_format(self):
        actual = doe._determine_inheritance(None, 'bar', 'text')
        expected = 'bar', 'default.text'
        self.assertEqual(actual, expected)

    def test_yes_template_yes_dir_yes_format(self):
        actual = doe._determine_inheritance('foo', 'bar', 'text')
        expected = 'bar', 'foo'
        self.assertEqual(actual, expected)

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.silencer = patch('sys.stdout', new_callable=StringIO)
        self.silencer.start()

    def tearDown(self):
        self.silencer.stop()

    @patch('dayone_export.cli.dayone_export', return_value="")
    def test_tag_splitter_protects_any(self, mock_doe):
        dayone_export.cli.run(['--tags', 'any', 'tests/fake_journal'])
        expected = 'any'
        actual = mock_doe.call_args[1]['tags']
        self.assertEqual(expected, actual)

    @patch('dayone_export.cli.dayone_export', return_value="")
    def test_tag_splitter(self, mock_doe):
        dayone_export.cli.run(['--tags', 'a, b', 'tests/fake_journal'])
        expected = ['a', 'b']
        actual = mock_doe.call_args[1]['tags']
        self.assertEqual(expected, actual)

    def test_invalid_package(self):
        actual = dayone_export.cli.run(['tests'])
        expected = 'Not a valid Day One package'
        self.assertTrue(actual.startswith(expected), actual)

    @patch('dayone_export.cli.dayone_export', side_effect=jinja2.TemplateNotFound('msg'))
    def test_template_not_found(self, mock_doe):
        actual = dayone_export.cli.run(['tests/fake_journal'])
        expected = "Template not found"
        self.assertTrue(actual.startswith(expected), actual)

