#!/usr/bin/env python3
"""Build the static notes pages for the hire site.

Reads markdown from _notes/*.md (front matter + body) and renders:
  notes/*.html, notes/index.html, notes/feed.xml, sitemap.xml
plus notes/notes.css (hand-written, only copied).

No third-party dependencies, so the build stays reproducible: python3 tools/build_notes.py
"""

import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_notes"
OUT = ROOT / "notes"
SITE = "https://dax233.github.io/hire"


def parse_front_matter(text):
    if not text.startswith("---"):
        raise ValueError("missing front matter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("unterminated front matter")
    meta = {}
    for line in parts[1].strip().splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, parts[2].lstrip()


def inline(text):
    """Render the small inline subset: code, bold, links."""
    out = html.escape(text)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<a href=\"\2\">\1</a>", out)
    return out


BLOCK_START = re.compile(r"^(#{2,6}\s|[-*]\s|\d+\.\s|>|```|---$|\*\*\*$)")


def render_body(md):
    lines = md.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            lang = line[3:].strip()
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            attr = ' class="lang-%s"' % lang if lang else ""
            out.append("<pre><code%s>%s</code></pre>" % (attr, html.escape("\n".join(buf))))
            continue
        heading = re.match(r"^(#{2,4})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            out.append("<h%d>%s</h%d>" % (level, inline(heading.group(2)), level))
            i += 1
            continue
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip())
                i += 1
            out.append("<blockquote><p>%s</p></blockquote>" % inline(" ".join(buf)))
            continue
        if line.startswith("- ") or line.startswith("* "):
            items = []
            while i < n and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                items.append(inline(lines[i][2:].strip()))
                i += 1
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in items))
            continue
        if re.match(r"^\d+\.\s", line):
            items = []
            while i < n and re.match(r"^\d+\.\s", lines[i]):
                items.append(inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % x for x in items))
            continue
        if line.strip() in ("---", "***"):
            out.append("<hr>")
            i += 1
            continue
        buf = []
        while i < n and lines[i].strip() and not BLOCK_START.match(lines[i]):
            buf.append(lines[i].strip())
            i += 1
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf)))
        else:
            i += 1
    return "\n".join(out)


PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s — Dax233 Notes</title>
<meta name="description" content="%(summary)s">
<link rel="canonical" href="%(url)s">
<link rel="alternate" type="application/rss+xml" title="Dax233 Notes" href="feed.xml">
<link rel="stylesheet" href="notes.css">
<script type="application/ld+json">%(jsonld)s</script>
</head>
<body>
<main class="wrap">
<div class="top"><span class="kicker">NOTES / DAX233</span><span><a href="./">← notes</a> · <a href="../">hire</a></span></div>
<h1>%(title)s</h1>
<div class="meta">%(date)s · %(tags)s</div>
%(body)s
<section class="cta">
<p class="kicker">NEED A HAND</p>
<p>%(cta)s</p>
<p><a href="../">服务范围与报价 →</a> · <a href="mailto:bakadax@qq.com">bakadax@qq.com</a></p>
</section>
<div class="foot"><span>独立开发者 · 远程接单</span><span><a href="https://github.com/Dax233">github.com/Dax233</a></span></div>
</main>
</body>
</html>
"""

INDEX = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Notes — Dax233</title>
<meta name="description" content="AI 工具链排错、文件格式解析与自动化的一些记录。">
<link rel="canonical" href="%(base)s/notes/">
<link rel="alternate" type="application/rss+xml" title="Dax233 Notes" href="feed.xml">
<link rel="stylesheet" href="notes.css">
</head>
<body>
<main class="wrap">
<div class="top"><span class="kicker">NOTES / DAX233</span><a href="../">← work with me</a></div>
<h1>Notes</h1>
<p class="intro">AI 工具链排错、文件格式解析、自动化的一些记录。都是我自己踩过、修过的东西。</p>
<ul class="posts">
%(items)s
</ul>
<div class="foot"><span>独立开发者 · 远程接单</span><span><a href="https://github.com/Dax233">github.com/Dax233</a></span></div>
</main>
</body>
</html>
"""

ITEM = """<li>
<div class="date">%(date)s</div>
<h2><a href="%(slug)s.html">%(title)s</a></h2>
<p>%(summary)s</p>
<div class="tags">%(tags)s</div>
</li>"""


def main():
    OUT.mkdir(exist_ok=True)
    posts = []
    for path in sorted(SRC.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        for key in ("title", "slug", "date", "summary"):
            if key not in meta:
                sys.exit("%s: front matter missing %s" % (path.name, key))
        meta["body"] = render_body(body)
        meta["tags"] = meta.get("tags", "")
        meta["cta"] = meta.get("cta", "有类似的需求？发邮件说说你的情况，我先免费判断是不是能接。")
        meta["url"] = "%s/notes/%s.html" % (SITE, meta["slug"])
        meta["rfc822"] = datetime.strptime(meta["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")
        jsonld = '{"@context":"https://schema.org","@type":"TechArticle","headline":"%s","datePublished":"%s","description":"%s","author":{"@type":"Person","name":"Dax233","url":"https://github.com/Dax233"}}' % (
            meta["title"].replace('"', ""),
            meta["date"],
            meta["summary"].replace('"', ""),
        )
        meta["jsonld"] = jsonld
        page = PAGE % meta
        (OUT / (meta["slug"] + ".html")).write_text(page, encoding="utf-8")
        posts.append(meta)

    posts.sort(key=lambda m: m["date"], reverse=True)
    items = "\n".join(ITEM % m for m in posts)
    (OUT / "index.html").write_text(INDEX % {"base": SITE, "items": items}, encoding="utf-8")

    # RSS: keep it plain so feed readers and aggregators accept it
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    entries = []
    for m in posts:
        entries.append("""<item>
<title>%(title)s</title>
<link>%(url)s</link>
<guid>%(url)s</guid>
<description>%(summary)s</description>
<pubDate>%(rfc822)s</pubDate>
</item>""" % m)
    feed = """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel>
<title>Dax233 Notes</title>
<link>%(base)s/notes/</link>
<description>AI 工具链排错、文件格式解析与自动化记录</description>
<language>zh-cn</language>
<lastBuildDate>%(now)s</lastBuildDate>
%(entries)s
</channel></rss>""" % {"base": SITE, "now": now, "entries": "\n".join(entries)}
    (OUT / "feed.xml").write_text(feed, encoding="utf-8")

    urls = [SITE + "/", SITE + "/notes/"] + ["%s/notes/%s.html" % (SITE, m["slug"]) for m in posts]
    sitemap = """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
%(items)s
</urlset>""" % {"items": "\n".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>" % (u, datetime.now(timezone.utc).strftime("%Y-%m-%d")) for u in urls)}
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print("built %d note(s) -> %s" % (len(posts), OUT))


if __name__ == "__main__":
    main()