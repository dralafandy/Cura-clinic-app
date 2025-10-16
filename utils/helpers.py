import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime, date, timedelta
from database.crud import CRUDOperations

crud = CRUDOperations()

def create_revenue_chart(payments_df):
    """إنشاء مخطط الإيرادات"""
    if payments_df.empty:
        return None
    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
    daily_revenue = payments_df.groupby(payments_df['payment_date'].dt.date)['amount'].sum().reset_index()
    fig = px.line(daily_revenue, x='payment_date', y='amount', 
                  title='الإيرادات اليومية', 
                  labels={'payment_date': 'التاريخ', 'amount': 'المبلغ (ج.م)'})
    fig.update_layout(
        xaxis_title="التاريخ",
        yaxis_title="المبلغ (ج.م)",
        font=dict(size=12),
        showlegend=False
    )
    return fig

def create_expenses_pie_chart(expenses_df):
    """إنشاء مخطط دائري للمصروفات حسب الفئة"""
    if expenses_df.empty:
        return None
    category_expenses = expenses_df.groupby('category')['amount'].sum().reset_index()
    fig = px.pie(category_expenses, values='amount', names='category', 
                 title='توزيع المصروفات حسب الفئة')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(font=dict(size=12))
    return fig

def create_appointments_status_chart(appointments_df):
    """إنشاء مخطط حالة المواعيد"""
    if appointments_df.empty:
        return None
    status_counts = appointments_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    fig = px.bar(status_counts, x='status', y='count',
                 title='توزيع المواعيد حسب الحالة',
                 labels={'status': 'الحالة', 'count': 'العدد'})
    fig.update_layout(
        xaxis_title="الحالة",
        yaxis_title="العدد",
        font=dict(size=12)
    )
    return fig

def create_inventory_alert_chart(inventory_df):
    """إنشاء مخطط تنبيهات المخزون"""
    if inventory_df.empty:
        return None
    low_stock = inventory_df[inventory_df['quantity'] <= inventory_df['min_stock_level']]
    if low_stock.empty:
        return None
    fig = px.bar(low_stock, x='item_name', y='quantity',
                 title='تنبيهات المخزون - العناصر قليلة المخزون',
                 labels={'item_name': 'اسم الصنف', 'quantity': 'الكمية المتبقية'},
                 color='quantity',
                 color_continuous_scale='Reds')
    fig.update_layout(
        xaxis_title="اسم الصنف",
        yaxis_title="الكمية المتبقية",
        font=dict(size=12),
        xaxis_tickangle=-45
    )
    return fig

def format_currency(amount):
    """تنسيق المبلغ كعملة"""
    return f"{amount:,.2f} ج.م"

def format_date_arabic(date_obj):
    """تنسيق التاريخ بالعربية"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    months_arabic = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    return f"{date_obj.day} {months_arabic[date_obj.month]} {date_obj.year}"

def calculate_age(birth_date):
    """حساب العمر من تاريخ الميلاد"""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def filter_dataframe_by_date(df, date_column, start_date, end_date):
    """فلترة DataFrame حسب نطاق التواريخ"""
    df[date_column] = pd.to_datetime(df[date_column]).dt.date
    return df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]

def show_success_message(message):
    """عرض رسالة نجاح"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """عرض رسالة خطأ"""
    st.error(f"❌ {message}")

def show_warning_message(message):
    """عرض رسالة تحذير"""
    st.warning(f"⚠️ {message}")

def show_info_message(message):
    """عرض رسالة معلومات"""
    st.info(f"ℹ️ {message}")

def export_to_excel(df, filename):
    """تصدير DataFrame إلى Excel"""
    from io import BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='البيانات')
    return buffer.getvalue()

def create_summary_cards(total_revenue, total_expenses, net_profit, appointments_today):
    """إنشاء بطاقات الملخص"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="💰 إجمالي الإيرادات",
            value=format_currency(total_revenue),
            delta=None
        )
    with col2:
        st.metric(
            label="💸 إجمالي المصروفات", 
            value=format_currency(total_expenses),
            delta=None
        )
    with col3:
        delta_color = "normal" if net_profit >= 0 else "inverse"
        st.metric(
            label="📈 صافي الربح",
            value=format_currency(net_profit),
            delta=f"{net_profit:+,.2f} ج.م",
            delta_color=delta_color
        )
    with col4:
        st.metric(
            label="📅 مواعيد اليوم",
            value=f"{appointments_today}",
            delta=None
        )

def get_status_color(status):
    """الحصول على لون حالة الموعد"""
    colors = {
        'مجدول': '#FFA500',      # برتقالي
        'مكتمل': '#28A745',       # أخضر
        'ملغي': '#DC3545',        # أحمر
        'معلق': '#6F42C1',        # بنفسجي
        'متأخر': '#FD7E14'        # برتقالي داكن
    }
    return colors.get(status, '#6C757D')  # رمادي افتراضي

def create_doctor_performance_chart(appointments_df, payments_df):
    """إنشاء مخطط أداء الأطباء"""
    if appointments_df.empty:
        return None
    doctor_stats = appointments_df.groupby('doctor_name').agg({
        'id': 'count',
        'total_cost': 'sum'
    }).reset_index()
    doctor_stats.columns = ['doctor_name', 'appointments_count', 'total_revenue']
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='عدد المواعيد',
        x=doctor_stats['doctor_name'],
        y=doctor_stats['appointments_count'],
        yaxis='y1',
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        name='الإيرادات (ج.م)',
        x=doctor_stats['doctor_name'],
        y=doctor_stats['total_revenue'],
        yaxis='y2',
        marker_color='darkblue'
    ))
    fig.update_layout(
        title='أداء الأطباء - المواعيد والإيرادات',
        xaxis=dict(title='الأطباء'),
        yaxis=dict(title='عدد المواعيد', side='left'),
        yaxis2=dict(title='الإيرادات (ج.م)', side='right', overlaying='y'),
        barmode='group',
        font=dict(size=12)
    )
    return fig

def get_appointment_time_slots(doctor_id, appointment_date):
    """Generate available time slots for a doctor on a specific date"""
    try:
        appointments = crud.get_appointments_by_date(appointment_date)
        doctor_appointments = appointments[appointments['doctor_id'] == doctor_id]['appointment_time'].tolist()
        
        # Define working hours (9:00 AM to 5:00 PM, 30-minute slots)
        start_hour = 9
        end_hour = 17
        time_slots = []
        current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")
        end_time = datetime.strptime(f"{end_hour}:00", "%H:%M")
        
        while current_time < end_time:
            time_str = current_time.strftime("%H:%M")
            if time_str not in doctor_appointments:
                time_slots.append(time_str)
            current_time += timedelta(minutes=30)
        
        return time_slots if time_slots else ["لا توجد مواعيد متاحة"]
    except Exception as e:
        show_error_message(f"خطأ في استرجاع المواعيد المتاحة: {str(e)}")
        return ["لا توجد مواعيد متاحة"]

def validate_phone_number(phone):
    """Validate phone number format"""
    pattern = r"^(?:\+20|0)(?:1[0125]\d{8}|9\d{8})$"
    return bool(re.match(pattern, phone))

def validate_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))
