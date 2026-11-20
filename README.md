# حساب دفتری و موجودی سوپرمارکت

این نسخه یک ابزار محلی Python و SQLite است و هیچ اطلاعاتی را به شبکه نمی‌فرستد. **رابط وب قدیمی قابل اجرا نبود و قالب‌های آن در مخزن نبودند**؛ این نسخه رابط خط فرمان دارد و بدون نصب بستهٔ خارجی کار می‌کند.

## راه‌اندازی

با Python 3.10 یا جدیدتر، در پوشهٔ مخزن:

```sh
python app.py init
python app.py product-add "شیر" 20000 3
python app.py products --low 5
python app.py stock-set 1 10
python app.py customer-add "مشتری نمونه"
python app.py entry-add 1 sale 125000
python app.py entry-add 1 payment 50000
python app.py balances
python app.py entries 1
python -m unittest -v
```

مبالغ را در یک واحد ثابت (مثلاً همه به تومان) وارد کنید. ماندهٔ مثبت بدهی مشتری و ماندهٔ منفی اعتبار مشتری نزد فروشگاه است. داده‌های واقعی یا فایل پشتیبان را در GitHub قرار ندهید.

فایل پیش‌فرض `instance/database.db` است. پیش از کار با دادهٔ قدیمی، یک کپی بگیرید و مسیر آن را با `python app.py --db /path/to/backup.db balances` یا برای موجودی با `python app.py --db /path/to/inventory-copy.db products` بدهید. برنامه هیچ جدولی را حذف نمی‌کند، اما پایگاه‌های دادهٔ جداگانه را هم خودکار ادغام نمی‌کند.
