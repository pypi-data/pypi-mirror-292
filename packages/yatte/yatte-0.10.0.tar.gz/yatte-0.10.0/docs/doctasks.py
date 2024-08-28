import xml.etree.ElementTree as xml
from datetime import date
from logging import error
from pathlib import Path
from sys import exit

import yatte
from yatte import task
from yatte.utils import is_newer, mkdir, run, stderr

man = Path("man")
docs = Path("docs")
pages = docs / "pages"
static = docs / "static"
page_template = docs / "templates" / "page.html"
outdir = docs / "_built"
tarball = outdir / "site.tar.gz"

version_file = Path(yatte.__file__)


@task("docs")
def render_docs_site():
    """Generate documentation site."""
    mkdir(outdir)
    cp(static / "style.css", outdir / "style.css")

    template = page_template.read_text()

    for page in pages.glob("*.html"):
        out_html = outdir / page.name
        if not uptodate(out_html, deps={page, page_template}):
            render_page(page, template, out_html)


@task("publish")
def upload_docs():
    """Upload documentation site."""
    render_docs_site()
    cp(man / "yatte.1", outdir / "yatte.1")
    tar_docs()
    run(f"hut pages publish -d yatte.javiljoen.net {tarball}")


# Helper functions


def cp(src, dest):
    if not dest.is_file() or is_newer(src, than=dest):
        run(f"cp -p {src} {dest}")


def uptodate(f, deps):
    # like is_newer() but takes multiple files as 2nd arg.
    return f.is_file() and all(f.stat().st_mtime > d.stat().st_mtime for d in deps)


def render_page(page, template, out_html):
    """Inject page into template and write to HTML file."""
    content = page.read_text()

    try:
        title = get_title(content)
    except (ValueError, xml.ParseError) as e:
        error(f"{e} in {page}")
        exit(1)

    if not title.startswith("Yatte"):
        title = f"{title} | yatte"

    stderr(f"$ compile {page_template} {page} > {out_html}")
    rendered = template.format(title=title, content=content, date=date.today())
    out_html.write_text(rendered)


def get_title(doc):
    """Return body of first h1 element in an HTML document.

    The doc must be a well-formed XML snippet:
    self-closing tags; all content wrapped in an outer element.
    """
    h1 = xml.fromstring(doc).find("h1")

    if h1 is None or h1.text is None:
        raise ValueError("Missing <h1> as child of document root")

    return h1.text


def tar_docs():
    """Create a tarball from the contents of `outdir`."""
    # Prevent an old tarball from being included in the new one:
    tarball.unlink(missing_ok=True)
    # Write the tarball to a separate folder first,
    # to prevent it including a partial version of itself:
    run(f"f=$(mktemp); tar -C {outdir} -czv . > $f && mv $f {tarball}")
