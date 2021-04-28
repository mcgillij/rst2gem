""" rst2gem.py for convering my blog from rst to gmi """
from collections import namedtuple
import os
from pathlib import Path
from datetime import datetime, date
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


def write_out_xml(rss):
    with open('../gem_capsule/atom.xml', 'w') as opened_file:
        opened_file.write(rss)


def generate_atom_feed(sorted_results):
    today = date.today()
    date_string = today.strftime("%Y-%m-%d")
    xml_top = f"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>gemini://gemini.mcgillij.dev/</id>
  <title>DevOops</title>
  <updated>{date_string}T00:00:00Z</updated>
  <link href="gemini://gemini.mcgillij.dev/atom.xml" rel="self"/>
  <link href="gemini://gemini.mcgillij.dev/" rel="alternate"/>
  <generator uri="https://github.com/mcgillij/rst2gem" version="0.1.0">
  rst2gen
  </generator>
  <subtitle>@mcgillij's blog</subtitle>
"""

    xml_footer = "</feed>"

    xml_body = ""
    for item in sorted_results:
        xml_body += f"""<entry>
    <id>gemini://gemini.mcgillij.dev/{item.filename}.gmi</id>
    <title>{item.title}</title>
    <updated>{item.date}T00:00:00Z</updated>
    <link href="gemini://gemini.mcgillij.dev/{item.filename}.gmi"
    rel="alternate"/>
  </entry>
"""

    return f"{xml_top}{xml_body}{xml_footer}"


if __name__ == "__main__":

    p = Path(".")
    file_list = p.glob("*.rst")
    title, date_obj, summary = "", "", ""
    results = []

    for filename in file_list:
        doc = open(filename.resolve()).read()
        title, date_obj, summary = walk_docstring(doc)

        datetime_object = datetime.strptime(date_obj, "%Y-%m-%d %H:%M")
        filename_part = os.path.splitext(filename)[0]

        results.append(
            Entry(
                filename=filename_part,
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

    TOP_MENU = """
=> /about.gmi About
=> /projects.gmi Projects
=> /misc.gmi Misc
=> /atom.xml Atom/RSS
    """

    FOOTER = """
Thanks for visiting my capsule!
    """

    BODY = ""
    for j in sorted_results:
        BODY += f"""
=> /{j.filename}.gmi {j.date} - {j.title}
{j.summary}
    """

    print(f"{HEADER}\n{TOP_MENU}\n{BODY}\n\n{FOOTER}")

    top_x = 25  # number of results to push to rss
    rss_feed = generate_atom_feed(sorted_results[0:top_x])
    write_out_xml(rss_feed)
