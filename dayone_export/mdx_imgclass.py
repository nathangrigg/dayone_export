import markdown

def _set_image_class(element):
    for child in element:
        if child.tag == 'img':
            child.set('class', 'entry-photo')
        _set_image_class(child)


class ImgClassProcessor(markdown.treeprocessors.Treeprocessor):
    def run(self, root):
        _set_image_class(root)


class ImgClassExtension(markdown.Extension):
    "Urlize Extension for Python-Markdown."

    def extendMarkdown(self, md, md_globals):
        md.treeprocessors['imgclass'] = ImgClassProcessor()


def makeExtension(**kwargs):
    return ImgClassExtension(**kwargs)
