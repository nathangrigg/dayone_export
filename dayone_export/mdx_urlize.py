# encoding: utf-8
# Adapted from https://github.com/bruth/marky, by Byron Ruth

import re
import markdown
import logging
import time


PROTOCOL_MATCH = re.compile(r'^(news|telnet|nttp|file|http|ftp|https)')
# from John Gruber
URLIZE_RE = '(?!%s)' % markdown.util.INLINE_PLACEHOLDER_PREFIX[1:] + \
    r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?''' + u"«»“”‘’]))"

class UrlizePattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        url = text = m.group(2)

        if not PROTOCOL_MATCH.match(url):
            url = 'http://' + url

        el = markdown.util.etree.Element("a")
        el.set('href', url)
        el.text = markdown.util.AtomicString(text)
        return el

class UrlizeExtension(markdown.Extension):
    "Urlize Extension for Python-Markdown."

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['urlize'] = UrlizePattern(URLIZE_RE, md)

def makeExtension(**kwargs):
    return UrlizeExtension(**kwargs)
