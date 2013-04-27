import unittest
import dayone_export as doe
import dayone_export.cli
from mock import patch
import os
import jinja2
from datetime import datetime
import pytz

this_path = os.path.split(os.path.abspath(__file__))[0]
fake_journal = os.path.join(this_path, 'fake_journal')

class TestEntryObject(unittest.TestCase):
    def setUp(self):
        self.entry = doe.Entry(fake_journal + '/entries/full.doentry')
        self.entry.set_photo('foo')
        self.no_location = doe.Entry(fake_journal + '/entries/00-first.doentry')
        self.entry.set_time_zone('America/Los_Angeles')
        self.entry.set_localized_date('America/Los_Angeles')

    def test_tags(self):
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

    def test_old_invalid_place_range_argument(self):
        self.assertRaises(TypeError, self.entry.place, 1, 3)

    def test_place_list_argument(self):
        expected = 'Seattle, United States'
        actual = self.entry.place([1, 3])
        self.assertEqual(expected, actual)

    def test_place_no_location(self):
        self.assertEqual(self.no_location.place(), "")

    def test_place_ignore_argument(self):
        expected = 'Washington'
        actual = self.entry.place([2, 3], ignore='United States')
        self.assertEqual(expected, actual)

    def test_getitem_data_key(self):
        self.assertEqual(self.entry['Photo'], 'foo')

    def test_getitem_text(self):
        expected = '2: Full entry with time zone, location, weather and a tag'
        self.assertEqual(self.entry['Text'], expected)

    def test_getitem_date(self):
        date = self.entry['Date']
        naive_date = date.replace(tzinfo = None)
        expected_date = datetime(2012, 1, 1, 16, 0)
        expected_zone = 'America/Los_Angeles'
        self.assertEqual(naive_date, expected_date)
        self.assertEqual(date.tzinfo.zone, expected_zone)

    def test_getitem_raises_keyerror(self):
        self.assertRaises(KeyError, lambda:self.entry['foo'])

    def test_getitem_flattened_dict(self):
        self.assertEqual(self.entry['Country'], self.entry['Location']['Country'])

    def test_get_keys_are_actually_keys(self):
        for key in self.entry.keys():
            self.assertTrue(key in self.entry, key)

class TestJournalParser(unittest.TestCase):
    def setUp(self):
        self.j = doe.parse_journal(fake_journal)

    def test_automatically_set_photos(self):
        expected = 'photos/00F9FA96F29043D09638DF0866EC73B2.jpg'
        actual = self.j[0]['Photo']
        self.assertEqual(expected, actual)

    def test_sort_order(self):
        j = self.j
        k = 'Creation Date'
        result = j[0][k] <= j[1][k] <= j[2][k]
        self.assertTrue(result)

    @patch('jinja2.Template.render')
    def test_dayone_export_run(self, mock_render):
        doe.dayone_export(fake_journal)
        mock_render.assert_called()

    @patch('jinja2.Template.render')
    def test_dayone_export_run_with_naive_after(self, mock_render):
        doe.dayone_export(fake_journal, after=datetime(2012, 9, 1))
        mock_render.assert_called()

    @patch('jinja2.Template.render')
    def test_dayone_export_run_with_localized_after(self, mock_render):
        after = pytz.timezone('America/New_York').localize(datetime(2012, 9, 1))
        doe.dayone_export(fake_journal, after=after)
        mock_render.assert_called()

    def test_after_filter(self):
        filtered = doe._filter_by_after_date(self.j, datetime(2012, 9, 1))
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

    @patch('jinja2.Template.render')
    def test_file_splitter(self, mock_render):
        gen = doe.dayone_export(fake_journal)
        self.assertEqual(len(list(gen)), 1)
        # If doing careful date comparisons, beware of timezones
        gen = doe.dayone_export(fake_journal, filename_template="%Y")
        fnames = sorted(fn for fn, _ in gen)
        self.assertEqual(fnames, ["2011", "2012"])
        gen = doe.dayone_export(fake_journal, filename_template="%Y%m%d")
        fnames = sorted(fn for fn, _ in gen)
        self.assertEqual(fnames, ["20111231", "20120101", "20120902"])



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
        self.silencer = patch('sys.stdout')
        self.silencer.start()

    def tearDown(self):
        self.silencer.stop()

    @patch('dayone_export.cli.dayone_export', return_value="")
    def test_tag_splitter_protects_any(self, mock_doe):
        dayone_export.cli.run(['--tags', 'any', fake_journal])
        expected = 'any'
        actual = mock_doe.call_args[1]['tags']
        self.assertEqual(expected, actual)

    @patch('dayone_export.cli.dayone_export', return_value="")
    def test_tag_splitter(self, mock_doe):
        dayone_export.cli.run(['--tags', 'a, b', fake_journal])
        expected = ['a', 'b']
        actual = mock_doe.call_args[1]['tags']
        self.assertEqual(expected, actual)

    def test_invalid_package(self):
        actual = dayone_export.cli.run(['.'])
        expected = 'Not a valid Day One package'
        self.assertTrue(actual.startswith(expected), actual)

    @patch('dayone_export.jinja2.Template.render', side_effect=jinja2.TemplateNotFound('msg'))
    def test_template_not_found(self, mock_doe):
        actual = dayone_export.cli.run([fake_journal])
        expected = "Template not found"
        self.assertTrue(actual.startswith(expected), actual)


class TestMarkdown(unittest.TestCase):
    """Test the markdown formatter"""
    def setUp(self):
        self.md = doe.filters.markdown_filter()
        self.autobold = doe.filters.markdown_filter(autobold=True)
        self.nl2br = doe.filters.markdown_filter(nl2br=True)

    def test_basic_markdown(self):
        expected = '<p>This <em>is</em> a <strong>test</strong>.</p>'
        actual = self.md('This *is* a **test**.')
        self.assertEqual(expected, actual)

    def test_urlize_http(self):
        expected = '<p>xx (<a href="http://url.com">http://url.com</a>) xx</p>'
        actual = self.md('xx (http://url.com) xx')
        self.assertEqual(expected, actual)

    def test_urlize_www(self):
        expected = '<p>xx <a href="http://www.google.com">www.google.com</a> xx</p>'
        actual = self.md('xx www.google.com xx')
        self.assertEqual(expected, actual)

    def test_urlize_no_www(self):
        expected = '<p>xx <a href="http://bit.ly/blah">bit.ly/blah</a> xx</p>'
        actual = self.md('xx bit.ly/blah xx')
        self.assertEqual(expected, actual)

    def test_urlize_quotes(self):
        expected = '<p>"<a href="http://www.url.com">www.url.com</a>"</p>'
        actual = self.md('"www.url.com"')
        self.assertEqual(expected, actual)

    def test_urlize_period(self):
        expected = '<p>See <a href="http://url.com">http://url.com</a>.</p>'
        actual = self.md('See http://url.com.')
        self.assertEqual(expected, actual)

    def test_two_footnotes(self):
        """Make sure the footnote counter is working"""
        text = "Footnote[^1]\n\n[^1]: Footnote text"
        self.assertNotEqual(self.md(text), self.md(text))

    def test_hashtag_does_not_become_h1(self):
        expected = '<p>#tag and #tag</p>'
        actual = self.md('#tag and #tag')
        self.assertEqual(expected, actual)

    def test_h1_becomes_h1(self):
        expected = '<h1>tag and #tag</h1>'
        actual = self.md('# tag and #tag')
        self.assertEqual(expected, actual)

    def test_autobold(self):
        expected = '<h1>This is a title</h1>\n<p>This is the next line</p>'
        actual = self.autobold('This is a title\nThis is the next line')
        self.assertEqual(expected, actual)

    def test_autobold_doesnt_happen_on_long_line(self):
        expected = '<p>AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA</p>'
        actual = self.autobold('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
        self.assertEqual(expected, actual)

    def test_nl2br(self):
        expected = '<p>a<br>\nb</p>'
        actual = self.nl2br('a\nb')
        self.assertEqual(expected, actual)

class TestLatex(unittest.TestCase):
    def test_latex_escape_backslash(self):
        actual = doe.filters.escape_tex(r'bl\ah')
        expected = r'bl\textbackslash{}ah'
        self.assertEqual(expected, actual)

    def test_latex_escape_dollar(self):
        actual = doe.filters.escape_tex(r'bl$ah')
        expected = r'bl\$ah'
        self.assertEqual(expected, actual)

    def test_latex_escape_symbols(self):
        actual = doe.filters.escape_tex(r'${}#^&~')
        expected = r'\$\{\}\#\textasciicircum{}\&\textasciitilde{}'
        self.assertEqual(expected, actual)

    def test_latex_sanity(self):
        _, actual = next(doe.dayone_export(fake_journal, format='tex'))
        expected = r'\documentclass'
        self.assertEqual(actual[:14], expected)
