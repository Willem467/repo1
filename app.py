"""A small dictionary-backed web app using only Python's standard library."""

import argparse
from copy import deepcopy
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import parse_qs, quote, urlsplit


# Add or edit pages here. Each record is a dictionary representing one table row.
PAGES = {
    "products": {
        "title": "Products",
        "rows": [
            {"Name": "Laptop", "Category": "Electronics", "Price": 899.00},
            {"Name": "Desk", "Category": "Furniture", "Price": 249.00},
            {"Name": "Mouse", "Category": "Electronics", "Price": 29.00},
        ],
    },
    "people": {
        "title": "People",
        "rows": [
            {"Name": {"value": "Alex", "background": "#bbf7d0"}, "Team": "Sales", "Location": "Auckland"},
            {"Name": "Sam", "Team": "Support", "Location": "Wellington"},
            {"Name": "Jordan", "Team": "Engineering", "Location": "Christchurch"},
        ],
    },
    "projects": {
        "title": "Projects",
        "rows": [
            {"Project": "Website", "Status": "In progress", "Owner": "Jordan"},
            {
                "Project": "Customer survey",
                "Status": {"value": "Complete", "background": "#bbf7d0"},
                "Owner": {"value": "Alex", "background": "#fecaca"},
            },
            {"Project": "Help centre", "Status": "Planned", "Owner": "Sam"},
        ],
    },
}


def document(title, content):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | Dictionary browser</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #f4f6fa; color: #17243a;
            font: 16px/1.6 system-ui, sans-serif; }}
    main {{ max-width: 1000px; margin: 48px auto; padding: 0 24px; }}
    a {{ color: #245bc2; }}
    h1 {{ line-height: 1.2; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 18px; }}
    .card {{ display: block; background: white; padding: 24px; border: 1px solid #dbe1ec;
             border-radius: 12px; text-decoration: none; }}
    .card:hover {{ border-color: #245bc2; }}
    .card strong {{ display: block; font-size: 22px; }}
    .card span {{ color: #536279; }}
    form {{ background: white; padding: 20px; border-radius: 12px; margin: 24px 0; }}
    label {{ display: block; font-weight: 600; margin-bottom: 8px; }}
    .controls {{ display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }}
    input {{ flex: 1; min-width: 160px; padding: 12px; border: 1px solid #aab7cc;
             border-radius: 6px; font: inherit; }}
    button {{ padding: 12px 20px; background: #245bc2; color: white; border: 0;
              border-radius: 6px; font: inherit; cursor: pointer; }}
    .table-wrap {{ overflow-x: auto; background: white; border: 1px solid #dbe1ec; border-radius: 12px; }}
    table {{ width: 100%; border-collapse: collapse; text-align: left; }}
    caption {{ text-align: left; padding: 16px; color: #536279; }}
    th, td {{ padding: 14px 16px; border-top: 1px solid #e5eaf2; }}
    th {{ background: #edf2fb; }}
  </style>
</head>
<body><main>{content}</main></body>
</html>"""


def home_page():
    cards = "".join(
        f'<a class="card" href="/page/{quote(slug, safe="")}">'
        f'<strong>{escape(page["title"])}</strong>'
        f'<span>{len(page["rows"])} records · Open table →</span></a>'
        for slug, page in PAGES.items()
    )
    return document("Home", f'<h1>Dictionary browser</h1><p>Choose a page to explore and search its records.</p><div class="cards">{cards}</div>')


def cell_value(cell):
    """Cells may be plain values or dictionaries with value/background fields."""
    return str(cell.get("value", "")) if isinstance(cell, dict) else str(cell)


def table_fragment(slug, query):
    # Render a snapshot of the current data on every request.
    page = deepcopy(PAGES[slug])
    # Collect all keys so records with different fields still display correctly.
    columns = list(dict.fromkeys(key for row in page["rows"] for key in row))
    rows = [row for row in page["rows"]
            if query.casefold() in " ".join(cell_value(value) for value in row.values()).casefold()]
    headings = "".join(f'<th scope="col">{escape(str(key))}</th>' for key in columns)
    def cell(row, key):
        data = row.get(key, "")
        value = cell_value(data)
        color = data.get("background", "") if isinstance(data, dict) else ""
        # Only accept hex colors; never insert arbitrary CSS from data.
        style = f' style="background-color: {color}"' if isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color) else ""
        return f'<td{style}>{escape(value)}</td>'

    body = "".join(
        "<tr>" + "".join(cell(row, key) for key in columns) + "</tr>"
        for row in rows
    )
    if not rows:
        body = f'<tr><td colspan="{max(1, len(columns))}">No matching records.</td></tr>'
    return f"""<table>
      <caption>{len(rows)} of {len(page['rows'])} records</caption>
      <thead><tr>{headings}</tr></thead><tbody>{body}</tbody>
    </table>"""


def table_page(slug, query):
    page = PAGES[slug]
    content = f"""<a href="/">← All pages</a>
    <h1>{escape(page['title'])}</h1>
    <form method="get">
      <label for="query">Search records</label>
      <div class="controls">
        <input id="query" name="q" type="text" value="{escape(query, quote=True)}" placeholder="Search any column">
        <button type="submit">Search</button>
        <a href="/page/{quote(slug, safe='')}">Clear</a>
      </div>
    </form>
    <p id="update-status" role="status">Updates automatically every 2 seconds.</p>
    <div id="live-table" class="table-wrap" data-endpoint="/api/table/{quote(slug, safe='')}">{table_fragment(slug, query)}</div>
    <script src="/live.js" defer></script>"""
    return document(page["title"], content)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlsplit(self.path)
        status = 200
        content_type = "text/html; charset=utf-8"
        if request.path == "/":
            html = home_page()
        elif request.path == "/live.js":
            html = Path(__file__).with_name("live.js").read_text(encoding="utf-8")
            content_type = "text/javascript; charset=utf-8"
        elif request.path.startswith("/api/table/") and request.path[11:] in PAGES:
            query = parse_qs(request.query).get("q", [""])[0]
            html = table_fragment(request.path[11:], query)
        elif request.path.startswith("/page/") and request.path[6:] in PAGES:
            query = parse_qs(request.query).get("q", [""])[0]
            html = table_page(request.path[6:], query)
        else:
            status = 404
            html = document("Page not found", '<h1>Page not found</h1><a href="/">Return home</a>')
        payload = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Address to listen on (default: this PC only)")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Dictionary browser listening on {args.host}:{args.port}. Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
