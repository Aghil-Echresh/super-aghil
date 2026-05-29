import sqlite3

# اتصال به دیتابیس (اگر وجود نداشته باشد ساخته می‌شود)
conn = sqlite3.connect("inventory.db")
cursor = conn.cursor()

# ایجاد جدول کالاها
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
""")

# افزودن کالا
def add_product(name, price, quantity):
    cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", 
                   (name, price, quantity))
    conn.commit()
    print(f"✅ {name} اضافه شد.")

# حذف کالا
def delete_product(product_id):
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    print(f"❌ کالا با شناسه {product_id} حذف شد.")

# بروزرسانی موجودی
def update_quantity(product_id, new_quantity):
    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
    conn.commit()
    print(f"🔄 موجودی کالا {product_id} بروزرسانی شد.")

# نمایش موجودی
def show_inventory():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    print("\n📦 موجودی کالاها:")
    for row in products:
        print(f"ID:{row[0]} | نام:{row[1]} | قیمت:{row[2]} | تعداد:{row[3]}")

# هشدار موجودی کم
def check_low_stock(threshold=5):
    cursor.execute("SELECT name, quantity FROM products WHERE quantity <= ?", (threshold,))
    low_stock = cursor.fetchall()
    for row in low_stock:
        print(f"⚠️ هشدار: موجودی {row[0]} کم است ({row[1]} عدد باقی مانده).")

# نمونه استفاده
if __name__ == "__main__":
    add_product("شیر", 20000, 10)
    add_product("نان", 5000, 3)
    show_inventory()
    check_low_stock()
    update_quantity(2, 8)
    show_inventory()        return max(0, balance)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)

# Routes
@app.route('/')
def index():
    customers = Customer.query.all()
    total_debt = sum(c.debt() for c in customers)
    total_credit = sum(c.credit() for c in customers)
    transaction_count = Transaction.query.count()
    
    return render_template('index.html', 
                         customers_count=len(customers),
                         total_debt=total_debt,
                         total_credit=total_credit,
                         transaction_count=transaction_count)

@app.route('/customers')
def customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/customer/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        customer = Customer(
            name=request.form['name'],
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            address=request.form.get('address', '')
        )
        db.session.add(customer)
        db.session.commit()
        return redirect(url_for('customers'))
    return render_template('add_customer.html')

@app.route('/customer/<int:id>')
def customer_detail(id):
    customer = Customer.query.get_or_404(id)
    transactions = Transaction.query.filter_by(customer_id=id).order_by(Transaction.created_at.desc()).all()
    return render_template('customer_detail.html', customer=customer, transactions=transactions)

@app.route('/customer/<int:id>/edit', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.phone = request.form.get('phone', '')
        customer.email = request.form.get('email', '')
        customer.address = request.form.get('address', '')
        db.session.commit()
        return redirect(url_for('customer_detail', id=id))
    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/<int:id>/delete', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('customers'))

@app.route('/transactions')
def transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('transactions.html', transactions=transactions)

@app.route('/transaction/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transaction = Transaction(
            customer_id=request.form['customer_id'],
            type=request.form['type'],
            amount=float(request.form['amount']),
            description=request.form.get('description', '')
        )
        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('transactions'))
    customers = Customer.query.all()
    return render_template('add_transaction.html', customers=customers)

@app.route('/reports')
def reports():
    customers = Customer.query.all()
    report_data = []
    
    for customer in customers:
        report_data.append({
            'name': customer.name,
            'phone': customer.phone,
            'debt': customer.debt(),
            'credit': customer.credit(),
            'balance': customer.balance(),
            'transaction_count': len(customer.transactions)
        })
    
    total_debt = sum(c['debt'] for c in report_data)
    total_credit = sum(c['credit'] for c in report_data)
    
    return render_template('reports.html', 
                         report_data=report_data,
                         total_debt=total_debt,
                         total_credit=total_credit)

@app.route('/api/customer/<int:id>/balance')
def get_customer_balance(id):
    customer = Customer.query.get_or_404(id)
    return jsonify({
        'id': id,
        'name': customer.name,
        'balance': customer.balance(),
        'debt': customer.debt(),
        'credit': customer.credit()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
