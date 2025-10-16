import streamlit as st
from datetime import time, timedelta

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
    start_time = time(9, 0)
    end_time = time(17, 0)
    
    current_time = start_time
    while current_time <= end_time:
        time_slots.append(current_time.strftime('%H:%M'))
        current_time = (datetime.combine(date.today(), current_time) + timedelta(minutes=30)).time()
    
    return time_slots

def get_status_color(status):
    """إرجاع لون الحالة"""
    colors = {
        'مجدول': '#2196F3',
        'مؤكد': '#4CAF50', 
        'في الانتظار': '#FF9800',
        'مكتمل': '#9C27B0',
        'ملغي': '#F44336'
    }
    return colors.get(status, '#757575')
