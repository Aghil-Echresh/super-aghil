# سیستم حساب دفتری مشتریان

## توضیحات
یک برنامه وب برای مدیریت حساب دفتری مشتریان به صورت آنلاین.

## ویژگی‌ها
- ✅ ثبت و مدیریت اطلاعات مشتریان
- ✅ ثبت تراکنش‌ها (فروش و پرداخت)
- ✅ محاسبه خودکار بدهی و طلب
- ✅ گزارش‌های تفصیلی
- ✅ رابط کاربری ساده و سریع

## تکنولوژی
- **Backend:** Python (Flask)
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap

## نصب و اجرا

### الزامات
- Python 3.8+
- pip

### مراحل نصب

```bash
# 1. کلون کردن مخزن
git clone https://github.com/Aghil-Echresh/super-aghil.git
cd super-aghil

# 2. ایجاد محیط مجازی
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا برای Windows:
# venv\Scripts\activate

# 3. نصب وابستگی‌ها
pip install -r requirements.txt

# 4. ایجاد پایگاه داده
python create_db.py

# 5. اجرای برنامه
python app.py
```

سپس مرورگر خود را باز کنید و به `http://localhost:5000` بروید.

## مجوز
MIT
