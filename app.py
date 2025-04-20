from pathlib import Path

from flask import Flask, render_template, redirect, url_for
from markdown import markdown
from markupsafe import Markup
import re


app = Flask(__name__)
CHAPTER_DIR = Path(__file__).parent / "chapters"
POEM_PATH   = Path(__file__).parent / "poem.md"


def load_chapters():
    chapters = []
    for p in sorted(CHAPTER_DIR.glob("*.md")):
        raw = p.read_text(encoding="utf-8")
        heading = raw.splitlines()[0].lstrip("# ").strip() if raw.startswith("#") else p.stem
        html = Markup(markdown(raw, extensions=["fenced_code", "toc"]))
        chapters.append({"title": heading, "html": html, "slug": p.stem})
    return chapters


@app.route("/")
def index():
    return redirect(url_for("post"))


@app.route("/post")
def post():
    return render_template(
        "read.html",
        chapters=load_chapters(),
        dictionary_enabled=True,
        mode="post",
    )


@app.route("/gutenberg")
def gutenberg():
    return render_template(
        "read.html",
        chapters=load_chapters(),
        dictionary_enabled=False,
        mode="gutenberg",
    )


@app.route("/pre")
def pre():
    poem_html = Markup(markdown(POEM_PATH.read_text(encoding="utf-8")))
    return render_template(
        "poem.html",
        poem=poem_html,
        dictionary_enabled=False,
        mode="pre",
    )

@app.template_filter('strip_links')
def strip_links(html: str) -> Markup:
    """
    Remove every <a>…</a> wrapper, leaving only the link text.
    """
    # regex: replace <a ...>inner</a> with inner
    stripped = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL)
    return Markup(stripped)

if __name__ == "__main__":
    app.run(debug=True)