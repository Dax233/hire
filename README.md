# Work with me

Small, fixed-scope paid work from an independent developer (Dax233).

## What I take on

- **AI tooling** — setup and troubleshooting for MCP servers, agent CLIs, local model runners, and small workflow automations. Small plugins and extensions too.
- **Python automation** — scripts, batch file processing, data cleaning, file parsing, and fixing scripts that stopped working.
- **File-format work** — binary/text format analysis and conversion tools.

## How it works

1. Email **bakadax@qq.com** with: what you need, tool and version, OS, and the exact error or a sample file.
2. I reply with scope and a fixed quote (small jobs typically **$30-$150**).
3. You approve; I build and test it.
4. Delivery: files plus a short usage note, with one revision round.

Async written communication only — no calls needed.

## What I don't take

Account or credential services, bypassing software protections, academic work, or scraping private data.

## Links

- GitHub: https://github.com/Dax233
- Blog: https://blog.bakadax.top

---

# 合作

独立开发者，接小项目：AI 工具链配置与排错、Python 自动化脚本、二进制/文件格式解析。

流程：邮件说明需求，我回复范围和固定报价，然后开工，交付文件和使用说明（含一轮修改）。

小单通常 30-150 美元；全程文字沟通，不需要电话。

邮箱：bakadax@qq.com

## 站点结构 / 构建

- `index.html` — 承接页（静态，直接编辑）
- `_notes/*.md` — 文章源文件（front matter + 少量 markdown 语法）
- `tools/build_notes.py` — 生成 `notes/*.html`、`notes/index.html`、`notes/feed.xml`、`sitemap.xml`；纯标准库，无第三方依赖
- 改完文章后运行 `python3 tools/build_notes.py`，再把生成的 HTML 一起提交
