"""Autobold preprocessor for Markdown.

Makes the first line of text into a heading.
"""

import markdown

MAX_LEN = 99

class AutoboldPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        """Makes the first line a heading"""
        line = lines[0]
        if line.startswith('# ') or len(line) > MAX_LEN:
            return lines
        else:
            return ["# " + line] + lines[1:]

class AutoboldExtension(markdown.Extension):
    """The extension to be installed"""
    def extendMarkdown(self, md, md_globals):
        md.preprocessors['autobold'] = AutoboldPreprocessor(md)

def makeExtension(**kwargs) :
    return AutoboldExtension(**kwargs)
