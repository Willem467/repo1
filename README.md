# Python dictionary web app

A home page links to Products, People, and Projects. Each page includes a text
input that searches all columns and a table generated from Python dictionaries.
Search is case-insensitive; clearing it shows all records.

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
