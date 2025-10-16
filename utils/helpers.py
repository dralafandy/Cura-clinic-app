import streamlit as st
from datetime import time, timedelta
from babel.dates import format_date
import locale

def format_currency(amount):
    """تنسيق العملة"""
    try:
        return f"ج.م {amount:,.2f}"
    except:
        return f"ج.م {amount}"

def show_success_message(message):
    """عرض رسالة نجاح"""
    st.success(message)

def show_error_message(message):
    """عرض رسالة خطأ"""
    st.error(message)

def show_warning_message(message):
    """عرض رسالة تحذير"""
    st.warning(message)

def show_info_message(message):
    """عرض رسالة معلومات"""
    st.info(message)

def format_date_arabic(date_obj):
    """تنسيق التاريخ باللغة العربية"""
    try:
        # تحويل إلى تنسيق عربي
        months = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"
    except:
        return str(date_obj)

def get_appointment_time_slots():
    """إنشاء قائمة بأوقات المواعيد المتاحة"""
    time_slots = []
    start_time = time(9, 0)  # 9:00 AM
    end_time = time(17, 0)   # 5:00 PM
    
    current_time = start_time
    while current_time <= end_time:
        time_slots.append(current_time.strftime('%H:%M'))
        # إضافة 30 دقيقة
        current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
    
    return time_slots

def get_status_color(status):
    """إرجاع لون الحالة"""
    colors = {
        'مجدول': '#2196F3',      # أزرق
        'مؤكد': '#4CAF50',       # أخضر
        'في الانتظار': '#FF9800', # برتقالي
        'مكتمل': '#9C27B0',      # بنفسجي
        'ملغي': '#F44336'        # أحمر
    }
    return colors.get(status, '#757575')  # رمادي افتراضي

def get_status_badge(status):
    """إرجاع badge ملون للحالة"""
    color = get_status_color(status)
    return f"<span style='background-color: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;'>{status}</span>"

def validate_appointment_time(doctor_id, appointment_date, appointment_time):
    """التحقق من صلاحية وقت الموعد"""
    from database.crud import crud
    
    # التحقق من أن الوقت خلال ساعات العمل
    work_hours_start = time(9, 0)  # 9 AM
    work_hours_end = time(17, 0)   # 5 PM
    
    if not (work_hours_start <= appointment_time <= work_hours_end):
        return False, "الموعد خارج ساعات العمل"
    
    # التحقق من عدم وجود تضارب
    if crud.check_appointment_conflict(doctor_id, appointment_date, appointment_time):
        return False, "هذا الوقت محجوز مسبقاً"
    
    return True, "الوقت متاح"

def calculate_duration(start_time, end_time):
    """حساب المدة بين وقتين"""
    start_dt = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)
    duration = end_dt - start_dt
    return duration.total_seconds() / 60  # بالمدة بالدقائق
