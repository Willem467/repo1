# Python dictionary web app

A home page links to Products, People, and Projects. Each page includes a text
input that searches all columns and a table generated from Python dictionaries.
Search is case-insensitive; clearing it shows all records.
Tables fetch the latest Python data every 2 seconds without refreshing the page.

## Run on your PC

Install Python 3.9 or newer. No extra packages are needed.
In a terminal in this repository, run:

```sh
python app.py
```

On Windows you can also use `py app.py`; on macOS/Linux use `python3 app.py`
if `python` is unavailable. Open `http://localhost:8000` in your browser.
Stop the app with Ctrl+C.

To let other devices on your home network connect:

```sh
python app.py --host 0.0.0.0
```

On another device, open `http://YOUR_PC_LAN_IP:8000` using your PC's local IP
address. Both devices must be on the same network, and your firewall must allow
inbound TCP port 8000 on the private network. Your PC must stay on and the app
must remain running. You can select another port with `--port 8080`.

This simple server is intended for local or trusted home-network use. Public
internet hosting needs a production server and HTTPS; do not expose this server
directly through router port forwarding.

## Change the pages and tables

Edit `PAGES` near the top of `app.py`. Each page has a URL key, a `title`, and
`rows`: a list of dictionaries. Dictionary keys become column headings and
values become table cells. Add another entry to create a new page and home-page
link automatically. Use simple URL keys such as `inventory` or `my-projects`.
Restart the server after editing the data.

For example:

```python
"inventory": {
    "title": "Inventory",
    "rows": [
        {"Item": "Notebook", "Quantity": 12},
        {"Item": "Pen", "Quantity": 30},
    ],
},
```

The text input filters the displayed data; it does not change the dictionaries.

## Live data updates

Every table request reads the current `PAGES` dictionaries in the running Python
process. Your Python data collection code can update these dictionaries, and
open pages will display the new values on the next poll (normally within 2 seconds).
The active search stays applied. If the connection fails, the last table stays
visible and the page retries automatically.

For example, code running in the same process can change a project status:

```python
PAGES["projects"]["rows"][0]["Status"] = {
    "value": "Complete", "background": "#bbf7d0"
}
```

For a background collector, build a fresh list of row dictionaries, then assign
it to `PAGES["projects"]["rows"]` in one operation. This avoids displaying
partially updated rows. A separate Python process does not share these dictionaries.
Editing `app.py` on disk still requires restarting the server; polling reads
live in-memory values rather than reloading Python source files.

## Cell background colors

Store a cell's value and background together in its row dictionary. Plain values
still work for cells that do not need a color. Use six-digit hex colors:

```python
{
    "Project": "Customer survey",
    "Status": {"value": "Complete", "background": "#bbf7d0"},
    "Owner": {"value": "Alex", "background": "#fecaca"},
},
```

Each cell controls its own color: Alex is green on the People page and red on
the Projects page in the example data. Even two Alex cells on the same page can
have different colors. Searching uses only displayed values, not color metadata.

To change a colored cell in the running process:

```python
PAGES["projects"]["rows"][1]["Owner"]["value"] = "Alex"
PAGES["projects"]["rows"][1]["Owner"]["background"] = "#bbf7d0"
```

Values and colors update automatically on the next poll. Omit `background` (or
use a plain value) to use the default background.
