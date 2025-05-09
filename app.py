from pathlib import Path
import json
from flask import Flask, render_template, url_for, redirect
from flask import request, jsonify
from markdown import markdown
from markupsafe import Markup
import re

import os
from dotenv import load_dotenv
import cohere

# load .env
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
print(COHERE_API_KEY)
co = cohere.Client(COHERE_API_KEY)

app = Flask(__name__)
CHAPTER_DIR = Path(__file__).parent / "chapters"
POEM_PATH   = Path(__file__).parent / "poem.md"

# ------------- helpers --------------------------------------------------

def load_chapters():
    chapters = []
    for p in sorted(CHAPTER_DIR.glob("*.md")):
        raw = p.read_text(encoding="utf-8")
        title = raw.splitlines()[0].lstrip("# ").strip() if raw.startswith("#") else p.stem
        title = re.sub(r'([A-Za-z]+)(\d+)', r'\1 \2', title)
        title = title.replace('-', ', ')
        title = title.title()
        html  = Markup(markdown(raw, extensions=["fenced_code", "toc"]))
        chapters.append({"slug": p.stem, "title": title, "html": html})
    return chapters

# Build node/edge JSON for graph (chronological + hard‑coded story links)
CHAPTERS   = load_chapters()
SLUG_INDEX = {c["slug"]: idx+1 for idx, c in enumerate(CHAPTERS)}  # node ids start at 1

chron_edges = [
    {"from": i, "to": i+1} for i in range(1, len(CHAPTERS))
]
# -------- hard‑coded story links --------
SPECIAL_LINKS = [
    ("part2_chapter7", "part3_chapter6"),  # example slugs, adjust to your filenames
]
special_edges = [
    {"from": SLUG_INDEX[a], "to": SLUG_INDEX[b], "dashes": True, "color": "#d62728"}
    for a, b in SPECIAL_LINKS if a in SLUG_INDEX and b in SLUG_INDEX
]

GRAPH_DATA = {
    "nodes": [
        {"id": idx, "label": c["title"], "slug": c["slug"]}
        for idx, c in enumerate(CHAPTERS, start=1)
    ],
    "edges": chron_edges + special_edges,
}

# ------------- routes ---------------------------------------------------

@app.route("/")
def default():
    return redirect(url_for("post_graph"))

# Post‑Gutenberg graph front page
@app.route("/post")
def post_graph():
    return render_template(
        "graph.html",
        graph_json=json.dumps(GRAPH_DATA),
        mode="post",
    )

# Post‑Gutenberg chapter view (dictionary enabled)
@app.route("/post/<slug>")
def post_read(slug):
    chap = next((c for c in CHAPTERS if c["slug"] == slug), None)
    if not chap:
        return "Chapter not found", 404
    return render_template(
        "read.html",
        chapters=[chap],
        dictionary_enabled=True,
        mode="post",
    )

# Gutenberg view (all chapters, links stripped)
@app.route("/gutenberg")
def gutenberg():
    return render_template(
        "read.html",
        chapters=CHAPTERS,
        dictionary_enabled=False,
        mode="gutenberg",
    )

# Pre‑Gutenberg poem
@app.route("/pre")
def pre():
    poem_html = Markup(markdown(POEM_PATH.read_text(encoding="utf-8")))
    return render_template(
        "poem.html",
        poem=poem_html,
        dictionary_enabled=False,
        mode="pre",
    )

# -------------------- utilities ----------------------------------------
import re
@app.template_filter('strip_links')
def strip_links(html):
    return Markup(re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html, flags=re.DOTALL))

@app.route("/post/<slug>/summarize", methods=["POST"])
def summarize(slug):
    # find the markdown file
    md_path = CHAPTER_DIR / f"{slug}.md"
    if not md_path.exists():
        return jsonify(error="Not found"), 404

    text = md_path.read_text(encoding="utf-8")
    # send to Cohere’s summarization endpoint
    # adjust model & parameters as you like
    response = co.summarize(
      model="summarize-xlarge",  # free-trial supported model
      length="short",
      text=text
    )
    summary = response.summary
    return jsonify(summary=summary)

@app.template_filter("strip_extras")
def strip_extras(html: str):
    """
    • Keep plain anchor text from <div class="note-wrapper"> … </div>
    • Keep slogan text from <div class="highlight-block"> … </div>
    • Drop highlight-badge + note-card completely
    """
    # note-wrapper  ➜  inner <span class="note-anchor">TEXT</span>
    html = re.sub(
        r'<div class="note-wrapper">.*?<span[^>]*class="note-anchor"[^>]*>(.*?)</span>.*?</div>',
        r'\1',
        html,
        flags=re.DOTALL,
    )

    # highlight-badge: just delete it
    html = re.sub(
        r'<span[^>]*class="highlight-badge"[^>]*>.*?</span>', '', html, flags=re.DOTALL
    )

    # highlight-block  ➜  plain inner text (strip any leftover tags)
    def _strip_block(m):
        inner = re.sub(r'<[^>]+>', '', m.group(1))
        return inner.strip()

    html = re.sub(
        r'<div[^>]*class="highlight-block"[^>]*>(.*?)</div>',
        _strip_block,
        html,
        flags=re.DOTALL,
    )

    return Markup(html)

if __name__ == "__main__":
    app.run(debug=True)