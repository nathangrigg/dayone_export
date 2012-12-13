"""Hashtag preprocessor for Markdown.

Changes lines beginning with #tag to \#tag to prevent #tag from
becoming <h1>tag</h1>.
"""

import markdown
import re

# Global Vars
HASHTAG_RE = re.compile('#\w')

class HashtagPreprocessor(markdown.preprocessors.Preprocessor):
    def run(self, lines):
        """Add a backslash before #\w at the beginning of each line"""
        transformed = []
        for line in lines:
            if HASHTAG_RE.match(line): # matches beginning of lines only
                line = '\\' + line
            transformed.append(line)

        return transformed

class HashtagExtension(markdown.Extension):
    """The extension to be installed"""
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('hashtag', HashtagPreprocessor(md), '>reference')

def makeExtension(configs=None) :
    return HashtagExtension(configs=configs)
