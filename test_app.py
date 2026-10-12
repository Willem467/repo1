"""Run with: python -B -m unittest -v"""

from copy import deepcopy
from threading import Thread
import unittest
from urllib.request import urlopen

import app


class LiveTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.original = deepcopy(app.PAGES["projects"])

    def tearDown(self):
        app.PAGES["projects"] = self.original

    def get(self, path):
        with urlopen(self.base + path) as response:
            self.assertEqual(response.headers["Cache-Control"], "no-store")
            return response.read().decode()

    def test_live_changes_and_filter(self):
        path = "/api/table/projects?q=Complete"
        before = self.get(path)
        self.assertIn("1 of 3 records", before)
        self.assertNotIn("<td>Website</td>", before)
        app.PAGES["projects"]["rows"][0]["Status"] = "Complete"
        after = self.get(path)
        self.assertIn("2 of 3 records", after)
        self.assertIn("<td>Website</td>", after)
        app.PAGES["projects"]["rows"][0]["Status"] = "Planned"
        self.assertNotIn("<td>Website</td>", self.get(path))

    def test_colors_update_with_values(self):
        html = self.get("/api/table/projects")
        self.assertIn('<td style="background-color: #bbf7d0">Complete</td>', html)
        self.assertIn('<td style="background-color: #fecaca">Alex</td>', html)
        owner = app.PAGES["projects"]["rows"][1]["Owner"]
        owner["background"] = "#bbf7d0"
        html = self.get("/api/table/projects")
        self.assertNotIn("#fecaca", html)
        self.assertIn('<td style="background-color: #bbf7d0">Alex</td>', html)
        owner["value"] = "Sam"
        self.assertIn('<td style="background-color: #bbf7d0">Sam</td>', self.get("/api/table/projects"))

    def test_independent_cell_colors_and_search(self):
        self.assertIn('<td style="background-color: #bbf7d0">Alex</td>', self.get("/api/table/people?q=Alex"))
        self.assertIn('<td style="background-color: #fecaca">Alex</td>', self.get("/api/table/projects?q=Alex"))
        app.PAGES["projects"]["rows"].append({"Owner": {"value": "Alex", "background": "#bbf7d0"}})
        html = self.get("/api/table/projects?q=Alex")
        self.assertIn("2 of 4 records", html)
        self.assertIn('<td style="background-color: #bbf7d0">Alex</td>', html)
        self.assertIn("No matching records.", self.get("/api/table/projects?q=fecaca"))

    def test_escaping_and_empty_results(self):
        app.PAGES["projects"]["rows"] = [{"Owner": {"value": "<script>", "background": 'red;" onclick="bad'}}]
        html = self.get("/api/table/projects")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("onclick", html)
        self.assertIn("No matching records.", self.get("/api/table/projects?q=absent"))

    def test_page_loads_polling_script(self):
        html = self.get("/page/projects?q=Alex")
        self.assertIn('data-endpoint="/api/table/projects"', html)
        self.assertIn('src="/live.js"', html)
        self.assertIn('value="Alex"', html)
        self.assertIn("async function refreshTable", self.get("/live.js"))


if __name__ == "__main__":
    unittest.main()
