""" rst2gem.py for convering my blog from rst to gmi """
from collections import namedtuple
import os
from pathlib import Path
from datetime import datetime
from operator import attrgetter
import docutils
from docutils.core import publish_doctree

Entry = namedtuple("Entry", ["filename", "title", "date", "summary"])


def walk_docstring(document):
    """ walk over the rst nodes the fields """
    doctree = publish_doctree(document)

    class Walker:
        """ Walker class to iterate over nodes """

        def __init__(self, document):
            self.document = document
            self.fields = {}
            self.title = ""
            self.summary = ""
            self.date = ""

        def dispatch_visit(self, x):
            """ Check all the fields for title, date and summary """
            if isinstance(x, docutils.nodes.title) and not self.title:
                self.title = x.pop()
            if isinstance(x, docutils.nodes.date):
                self.date = x.pop()
            if isinstance(x, docutils.nodes.field):
                field_name = x.children[0].rawsource
                field_value = x.children[1].rawsource
                self.fields[field_name] = field_value

    walk = Walker(doctree)
    doctree.walk(walk)
    return (
            walk.title.rawsource,
            walk.date.rawsource,
            walk.fields.get("summary")
            )


if __name__ == "__main__":

    p = Path(".")
    file_list = p.glob("*.rst")
    title, date, summary = "", "", ""
    results = []

    for filename in file_list:
        doc = open(filename.resolve()).read()
        title, date, summary = walk_docstring(doc)

        datetime_object = datetime.strptime(date, "%Y-%m-%d %H:%M")
        filename_gem = os.path.splitext(filename)[0]

        results.append(
            Entry(
                filename=filename_gem,
                title=title,
                date=datetime_object.strftime("%Y-%m-%d"),
                summary=summary,
            )
        )

    sorted_results = sorted(results, key=attrgetter("date"))
    sorted_results.reverse()

    HEADER = """
    ```
    ▓█████▄ ▓█████  ██▒   █▓ ▒█████   ▒█████   ██▓███    ██████
    ▒██▀ ██▌▓█   ▀ ▓██░   █▒▒██▒  ██▒▒██▒  ██▒▓██░  ██▒▒██    ▒
    ░██   █▌▒███    ▓██  █▒░▒██░  ██▒▒██░  ██▒▓██░ ██▓▒░ ▓██▄
    ░▓█▄   ▌▒▓█  ▄   ▒██ █░░▒██   ██░▒██   ██░▒██▄█▓▒ ▒  ▒   ██▒
    ░▒████▓ ░▒████▒   ▒▀█░  ░ ████▓▒░░ ████▓▒░▒██▒ ░  ░▒██████▒▒
     ▒▒▓  ▒ ░░ ▒░ ░   ░ ▐░  ░ ▒░▒░▒░ ░ ▒░▒░▒░ ▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░
     ░ ▒  ▒  ░ ░  ░   ░ ░░    ░ ▒ ▒░   ░ ▒ ▒░ ░▒ ░     ░ ░▒  ░ ░
     ░ ░  ░    ░        ░░  ░ ░ ░ ▒  ░ ░ ░ ▒  ░░       ░  ░  ░
       ░       ░  ░      ░      ░ ░      ░ ░                 ░
     ░                  ░
    ```
    """

    FOOTER = """
    => /atom.xml Atom/RSS to subscribe
    """

    BODY = ""
    for j in sorted_results:
        BODY += f"""
    => /{j.filename}.gmi {j.date} - {j.title}
    {j.summary}
    """

    print(f"{HEADER}\n\n{BODY}\n\n{FOOTER}")
