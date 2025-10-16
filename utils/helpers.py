from datetime import datetime, date
import pandas as pd

def format_currency(amount):
    """تنسيق المبلغ المالي"""
    return f"{amount:,.2f} ج.م"

def format_date(date_str):
    """تنسيق التاريخ"""
    if isinstance(date_str, str):
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    return date_str

def calculate_age(birth_date):
    """حساب العمر من تاريخ الميلاد"""
    if isinstance(birth_date, str):
        birth_date = datetime.fromisoformat(birth_date).date()
    
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def export_to_excel(dataframe, filename):
    """تصدير بيانات إلى Excel"""
    try:
        dataframe.to_excel(filename, index=False, engine='openpyxl')
        return True
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return False

def validate_phone(phone):
    """التحقق من صحة رقم الهاتف"""
    # إزالة المسافات والرموز
    phone = ''.join(filter(str.isdigit, phone))
    
    # التحقق من الطول (11 رقم للأرقام المصرية)
    if len(phone) == 11 and phone.startswith('01'):
        return True
    return False

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
