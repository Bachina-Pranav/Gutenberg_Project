from pathlib import Path

from flask import Flask, render_template, Markup, url_for
from markdown import markdown

app = Flask(__name__, static_folder="static", template_folder="templates")

CHAPTER_DIR = Path(__file__).parent / "chapters"


def load_chapters():
    """Read every *.md file in *natural* (numerical) order and convert to HTML."""
    chapters = []
    for md_path in sorted(CHAPTER_DIR.glob("*.md")):
        raw = md_path.read_text(encoding="utf-8")
        # First heading becomes the label in the navigation bar
        heading = raw.splitlines()[0].lstrip("# ").strip() if raw.startswith("#") else md_path.stem
        html = Markup(markdown(raw, extensions=["fenced_code", "toc"]))
        chapters.append({"title": heading, "html": html, "slug": md_path.stem})
    return chapters


@app.route("/")
def reader():
    chapters = load_chapters()
    return render_template("read.html", chapters=chapters)


if __name__ == "__main__":
    app.run(debug=True)  # remove debug=True in production