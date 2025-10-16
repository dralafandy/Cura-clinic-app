import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit as st

def create_revenue_chart(payments_df):
    """إنشاء مخطط الإيرادات"""
    if payments_df.empty:
        return None
    
    # تجميع الإيرادات حسب التاريخ
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
    
    # فلترة العناصر قليلة المخزون
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

def get_date_range_options():
    """الحصول على خيارات نطاقات التواريخ"""
    today = date.today()
    
    return {
        'اليوم': (today, today),
        'آخر 7 أيام': (today - timedelta(days=7), today),
        'آخر 30 يوم': (today - timedelta(days=30), today),
        'هذا الشهر': (date(today.year, today.month, 1), today),
        'الشهر الماضي': (date(today.year, today.month-1, 1) if today.month > 1 else date(today.year-1, 12, 1),
                        date(today.year, today.month, 1) - timedelta(days=1)),
        'هذا العام': (date(today.year, 1, 1), today)
    }

def validate_phone_number(phone):
    """التحقق من صحة رقم الهاتف"""
    # إزالة المسافات والرموز
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # التحقق من أن الرقم يحتوي على أرقام فقط ويبدأ بـ 01
    if phone.isdigit() and len(phone) == 11 and phone.startswith('01'):
        return True
    return False

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_appointment_time_slots():
    """الحصول على مواعيد العمل المتاحة"""
    slots = []
    start_hour = 9  # 9 صباحاً
    end_hour = 17   # 5 مساءً
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:  # كل نصف ساعة
            time_str = f"{hour:02d}:{minute:02d}"
            slots.append(time_str)
    
    return slots

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
        'في الانتظار': '#6F42C1', # بنفسجي
        'متأخر': '#FD7E14'        # برتقالي داكن
    }
    return colors.get(status, '#6C757D')  # رمادي افتراضي

def create_doctor_performance_chart(appointments_df, payments_df):
    """إنشاء مخطط أداء الأطباء"""
    if appointments_df.empty:
        return None
    
    # تجميع المواعيد والإيرادات حسب الطبيب
    doctor_stats = appointments_df.groupby('doctor_name').agg({
        'id': 'count',
        'total_cost': 'sum'
    }).reset_index()
    
    doctor_stats.columns = ['doctor_name', 'appointments_count', 'total_revenue']
    
    fig = go.Figure()
    
    # إضافة عدد المواعيد
    fig.add_trace(go.Bar(
        name='عدد المواعيد',
        x=doctor_stats['doctor_name'],
        y=doctor_stats['appointments_count'],
        yaxis='y1',
        marker_color='lightblue'
    ))
    
    # إضافة الإيرادات
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