"""Local supermarket inventory and customer ledger. No network access."""

import argparse
import sqlite3
from contextlib import closing
from decimal import Decimal, InvalidOperation
from pathlib import Path


def open_db(filename):
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(filename)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL,
            price REAL NOT NULL CHECK (price >= 0),
            quantity INTEGER NOT NULL CHECK (quantity >= 0)
        );
        CREATE TABLE IF NOT EXISTS customer (
            id INTEGER PRIMARY KEY, name VARCHAR(100) NOT NULL,
            phone VARCHAR(20), email VARCHAR(100), address VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS "transaction" (
            id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer(id),
            type VARCHAR(10) NOT NULL CHECK (type IN ('sale', 'payment')),
            amount FLOAT NOT NULL CHECK (amount > 0), description VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    return db


def money(raw):
    try:
        value = Decimal(raw)
        if not value.is_finite() or not 0 <= value <= 10**12 or value != value.quantize(Decimal("0.01")):
            raise ValueError
        return float(value)
    except (InvalidOperation, ValueError):
        raise argparse.ArgumentTypeError("مبلغ باید عددی معتبر و غیرمنفی با حداکثر دو رقم اعشار باشد.")


def quantity(raw):
    try:
        value = int(raw)
        if 0 <= value <= 10**9:
            return value
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("تعداد باید یک عدد صحیح غیرمنفی باشد.")


def name(raw):
    value = raw.strip()
    if not value or len(value) > 100:
        raise argparse.ArgumentTypeError("نام باید بین ۱ تا ۱۰۰ نویسه باشد.")
    return value


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--db", default="instance/database.db")
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    add = commands.add_parser("product-add")
    add.add_argument("name", type=name)
    add.add_argument("price", type=money)
    add.add_argument("quantity", type=quantity)
    stock = commands.add_parser("stock-set")
    stock.add_argument("id", type=int)
    stock.add_argument("quantity", type=quantity)
    products = commands.add_parser("products")
    products.add_argument("--low", type=quantity)
    customer = commands.add_parser("customer-add")
    customer.add_argument("name", type=name)
    customer.add_argument("--phone", default="")
    entry = commands.add_parser("entry-add")
    entry.add_argument("id", type=int, help="شناسهٔ مشتری")
    entry.add_argument("type", choices=("sale", "payment"))
    entry.add_argument("amount", type=money)
    entry.add_argument("--description", default="")
    commands.add_parser("balances")
    entries = commands.add_parser("entries")
    entries.add_argument("id", type=int)
    return root


def execute(db, args):
    action = args.command
    if action == "init":
        return ["پایگاه داده آماده است."]
    if action == "product-add":
        row = db.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                         (args.name, args.price, args.quantity))
        return [f"کالای ثبت‌شده: {row.lastrowid}"]
    if action == "stock-set":
        row = db.execute("UPDATE products SET quantity = ? WHERE id = ?", (args.quantity, args.id))
        if not row.rowcount:
            raise ValueError("کالا پیدا نشد.")
        return ["موجودی به‌روزرسانی شد."]
    if action == "products":
        rows = db.execute(
            "SELECT * FROM products WHERE (? IS NULL OR quantity <= ?) ORDER BY id", (args.low, args.low)
        )
        return [f"{row['id']}\t{row['name']}\t{row['price']:.2f}\t{row['quantity']}" for row in rows]
    if action == "customer-add":
        if len(args.phone) > 20:
            raise ValueError("شماره تماس بیش از حد طولانی است.")
        row = db.execute("INSERT INTO customer (name, phone, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                         (args.name, args.phone))
        return [f"مشتری ثبت‌شده: {row.lastrowid}"]
    if action == "entry-add":
        if args.amount <= 0 or len(args.description) > 200:
            raise ValueError("مبلغ باید مثبت و شرح حداکثر ۲۰۰ نویسه باشد.")
        if not db.execute("SELECT 1 FROM customer WHERE id = ?", (args.id,)).fetchone():
            raise ValueError("مشتری پیدا نشد.")
        row = db.execute(
            """INSERT INTO "transaction" (customer_id, type, amount, description, created_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (args.id, args.type, args.amount, args.description),
        )
        return [f"تراکنش ثبت‌شده: {row.lastrowid}"]
    if action == "entries":
        rows = db.execute(
            'SELECT * FROM "transaction" WHERE customer_id = ? ORDER BY id', (args.id,)
        )
        return [f"{row['id']}\t{row['type']}\t{row['amount']:.2f}\t{row['description'] or ''}" for row in rows]
    rows = db.execute("""
        SELECT customer.id, customer.name,
               ROUND(COALESCE(SUM(CASE t.type
                   WHEN 'sale' THEN t.amount WHEN 'payment' THEN -t.amount ELSE 0 END), 0), 2) AS balance
        FROM customer LEFT JOIN "transaction" AS t ON t.customer_id = customer.id
        GROUP BY customer.id ORDER BY customer.id
    """)
    return [f"{row['id']}\t{row['name']}\t{row['balance']:.2f}" for row in rows]


def main(argv=None):
    root = parser()
    args = root.parse_args(argv)
    try:
        with closing(open_db(args.db)) as db, db:
            rows = execute(db, args)
    except (OSError, sqlite3.Error, ValueError) as err:
        root.exit(1, f"{err}\n")
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
