import unittest
import dayone_export as doe
import dayone_export.cli
from mock import patch
import os
import jinja2
from datetime import datetime
import pytz
import locale

THIS_PATH = os.path.split(os.path.abspath(__file__))[0]
FAKE_JOURNAL = os.path.join(THIS_PATH, 'fake_journal')
REGRESSION_JOURNAL = os.path.join(THIS_PATH, 'regression')

def reset_locale():
    locale.setlocale(locale.LC_ALL, "C")

def has_locale(loc):
    try:
        locale.setlocale(locale.LC_ALL, loc)
    except locale.Error:
        return False
    reset_locale()
    return True


LOCALE = {"en": "en_US.UTF-8", "fr": "fr_CH.UTF-8"}
MISSING_LOCALES = {x for x in LOCALE.values() if not has_locale(x)}
SkipIfMissingLocale = lambda loc: unittest.skipIf(
        loc in MISSING_LOCALES, "System lacks locale {}".format(loc))


class TestEntryObject(unittest.TestCase):
    def setUp(self):
        j = doe.parse_journal(FAKE_JOURNAL)
        self.entry = j[1]
        self.no_location = j[0]
        self.last_entry = j[3]

    def test_tags(self):
        self.assertEqual(self.entry.tags, ['tag'])

    def test_place_no_arguments(self):
        expected = 'Zoo, Seattle, Washington, United States'
        actual = doe.format_place(self.entry)
        self.assertEqual(expected, actual)

    def test_place_int_argument(self):
        expected = 'Zoo, Seattle, Washington'
        actual = doe.format_place(self.entry, 3)
        self.assertEqual(expected, actual)

    def test_place_list_argument(self):
        expected = 'Seattle, United States'
        actual = doe.format_place(self.entry, [1, 3])
        self.assertEqual(expected, actual)

    def test_place_no_location(self):
        self.assertEqual(doe.format_place(self.no_location), "")

    def test_place_ignore_argument(self):
        expected = 'Washington'
        actual = doe.format_place(self.entry, [2, 3], ignore='United States')
        self.assertEqual(expected, actual)

    def test_getitem_text(self):
        expected = '2: Full entry with time zone, location, weather and a tag'
        self.assertEqual(self.entry.text, expected)

    def test_getitem_date(self):
        date = self.entry.localDate
        naive_date = date.replace(tzinfo = None)
        expected_date = datetime(2012, 1, 1, 16, 0)
        expected_zone = 'America/Los_Angeles'
        self.assertEqual(naive_date, expected_date)
        self.assertEqual(date.tzinfo.zone, expected_zone)

    def test_getitem_raises_keyerror(self):
        self.assertRaises(KeyError, lambda:self.entry['foo'])

    def test_get_keys_are_actually_keys(self):
        for key in self.entry.keys():
            self.assertTrue(key in self.entry, key)

class TestJournalParser(unittest.TestCase):
    def setUp(self):
        self.j = doe.parse_journal(FAKE_JOURNAL)

    @patch('jinja2.Template.render')
    def test_dayone_export_run(self, mock_render):
        list(doe.dayone_export(FAKE_JOURNAL))
        mock_render.assert_called()

    @patch('jinja2.Template.render')
    def test_dayone_export_run_with_naive_after(self, mock_render):
        list(doe.dayone_export(FAKE_JOURNAL, after=datetime(2012, 9, 1)))
        mock_render.assert_called()

    @patch('jinja2.Template.render')
    def test_dayone_export_run_with_localized_after(self, mock_render):
        after = pytz.timezone('America/New_York').localize(datetime(2012, 9, 1))
        list(doe.dayone_export(FAKE_JOURNAL, after=after))
        mock_render.assert_called()

    def test_after_filter(self):
        filtered = doe._filter_by_date(self.j, datetime(2013, 11, 14), None)
        self.assertEqual(len(filtered), 2)
        filtered = doe._filter_by_date(self.j, datetime(2013, 11, 15), None)
        self.assertEqual(len(filtered), 1)

    def test_before_filter(self):
        filtered = doe._filter_by_date(self.j, None, datetime(2013, 11, 14))
        self.assertEqual(len(filtered), 2)
        filtered = doe._filter_by_date(self.j, None, datetime(2013, 11, 15))
        self.assertEqual(len(filtered), 3)

    def test_two_sided_date_filter(self):
        filtered = doe._filter_by_date(
                self.j, datetime(2013, 11, 14), datetime(2013, 11, 15))
        self.assertEqual(len(filtered), 1)

    def test_tags_any_tag(self):
        filtered = doe._filter_by_tag(self.j, 'any')
        self.assertEqual(len(list(filtered)), 2)

    def test_tags_one_tag(self):
        filtered = doe._filter_by_tag(self.j, ['tag'])
        self.assertEqual(len(list(filtered)), 1)

    def test_tags_no_matches(self):
        filtered = doe._filter_by_tag(self.j, ['porcupine'])
        self.assertEqual(len(list(filtered)), 0)

    def test_exclude_nonexistent_tag(self):
        actual_size = len(self.j)
        after_exlusion = doe._exclude_tags(self.j, ['porcupine'])
        self.assertEqual(actual_size, len(list(after_exlusion)))

    def test_exclude_multiple_nonexistent_tags(self):
        actual_size = len(self.j)
        after_exlusion = doe._exclude_tags(self.j, ['porcupine', 'nosuchtag'])
        self.assertEqual(actual_size, len(list(after_exlusion)))

    def test_exclude_tag(self):
        actual_size = len(self.j)
        after_exlusion = doe._exclude_tags(self.j, ['absolutelyuniqtag22'])
        self.assertEqual(len(list(after_exlusion)), actual_size-1)

    def test_tags_and_exclude_combined(self):
        actual_size = len(self.j)
        filtered = doe._filter_by_tag(self.j, 'any')
        after_exlusion = doe._exclude_tags(filtered, ['absolutelyuniqtag22'])
        self.assertEqual(len(list(after_exlusion)), 1)

    @patch('jinja2.Template.render')
    def test_file_splitter(self, mock_render):
        gen = doe.dayone_export(FAKE_JOURNAL)
        self.assertEqual(len(list(gen)), 1)
        # If doing careful date comparisons, beware of timezones
        gen = doe.dayone_export(FAKE_JOURNAL, filename_template="%Y")
        fnames = sorted(fn for fn, _ in gen)
        self.assertEqual(fnames, ["2011", "2012", "2013"])
        gen = doe.dayone_export(FAKE_JOURNAL, filename_template="%Y%m%d")
        fnames = sorted(fn for fn, _ in gen)
        self.assertEqual(fnames, ["20111231", "20120101", "20131113", "20131207"])



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
        dayone_export.cli.run(['--tags', 'any', FAKE_JOURNAL])
        expected = 'any'
        actual = mock_doe.call_args[1]['tags']
        self.assertEqual(expected, actual)

    @patch('dayone_export.cli.dayone_export', return_value="")
    def test_tag_splitter(self, mock_doe):
        dayone_export.cli.run(['--tags', 'a, b', FAKE_JOURNAL])
        expected = ['a', 'b']
        actual = mock_doe.call_args[1]['tags']
        self.assertEqual(expected, actual)

    def test_invalid_package(self):
        actual = dayone_export.cli.run(['.'])
        expected = 'Not a valid Day One JSON export'
        self.assertTrue(actual.startswith(expected), actual)

    @patch('dayone_export.jinja2.Template.render', side_effect=jinja2.TemplateNotFound('msg'))
    def test_template_not_found(self, mock_doe):
        actual = dayone_export.cli.run([FAKE_JOURNAL])
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
    def setUp(self):
        reset_locale()

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
        _, actual = next(doe.dayone_export(FAKE_JOURNAL, format='tex'))
        expected = r'\documentclass'
        self.assertEqual(actual[:14], expected)


class TestDateFormat(unittest.TestCase):
    def setUp(self):
        reset_locale()
        self.date = datetime(2014, 2, 3)

    def test_default_format(self):
        expected = 'Monday, Feb 3, 2014'
        self.assertEqual(expected, doe.filters.format(self.date))
        self.assertEqual(expected, doe.filters._strftime_portable(self.date))

    def test_format_leave_zero(self):
        expected = '2014-02-03'
        self.assertEqual(expected, doe.filters.format(self.date, '%Y-%m-%d'))
        self.assertEqual(
            expected, doe.filters._strftime_portable(self.date, '%Y-%m-%d'))

    def test_format_remove_zero(self):
        expected = '2/3/2014'
        self.assertEqual(
            expected, doe.filters.format(self.date, '%-m/%-d/%Y'))
        self.assertEqual(
            expected, doe.filters._strftime_portable(self.date, '%-m/%-d/%Y'))

class TestDefaultTemplates(unittest.TestCase):
    def setUp(self):
        self.silencer = patch('sys.stdout')
        self.silencer.start()

    def tearDown(self):
        self.silencer.stop()

    @SkipIfMissingLocale(LOCALE["en"])
    def test_default_html_template_english(self):
        code = dayone_export.cli.run(["--locale", LOCALE["en"], FAKE_JOURNAL])
        self.assertFalse(code)

    @SkipIfMissingLocale(LOCALE["fr"])
    def test_default_html_template_french(self):
        code = dayone_export.cli.run(["--locale", LOCALE["fr"], FAKE_JOURNAL])
        self.assertFalse(code)
