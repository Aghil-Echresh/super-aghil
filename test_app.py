import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class LedgerTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "test.db"

    def cli(self, *args, status=0):
        result = subprocess.run(
            [sys.executable, "app.py", "--db", str(self.path), *args],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, status, result.stderr)
        return result.stdout

    def test_stock_roundtrip(self):
        self.cli("product-add", "شیر", "20000", "3")
        self.assertIn("شیر", self.cli("products", "--low", "5"))
        self.cli("stock-set", "1", "10")
        self.assertEqual(self.cli("products", "--low", "5"), "")
        self.cli("stock-set", "1", "-1", status=2)

    def test_sales_payments_and_invalid_data(self):
        self.cli("customer-add", "نمونه")
        self.cli("entry-add", "1", "sale", "125.20")
        self.cli("entry-add", "1", "payment", "25.10")
        self.assertIn("100.10", self.cli("balances"))
        self.cli("entry-add", "99", "sale", "35", status=1)
        self.cli("entry-add", "1", "sale", "NaN", status=2)
        self.assertEqual(len(self.cli("entries", "1").splitlines()), 2)

    def test_old_inventory_table_is_preserved(self):
        with sqlite3.connect(self.path) as db:
            db.executescript("""
                CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, price REAL NOT NULL, quantity INTEGER NOT NULL);
                INSERT INTO products (name, price, quantity) VALUES ('old item', 100, 2);
            """)
        self.assertIn("old item", self.cli("products"))


if __name__ == "__main__":
    unittest.main()
