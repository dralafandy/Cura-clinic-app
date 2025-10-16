"""
Helper functions for the medical clinic management system
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, datetime, timedelta
import re

def validate_phone_number(phone):
    """Validate Egyptian phone number"""
    if not phone:
        return False
    
    # Remove spaces and dashes
    clean_phone = re.sub(r'[-\s]', '', phone)
    
    # Egyptian phone number patterns
    patterns = [
        r'^01[0125]\d{8}$',  # Mobile numbers
        r'^0[2-9]\d{7,8}$',  # Landline numbers
        r'^20\d{9,10}$',     # International format
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def validate_email(email):
    """Validate email format"""
    if not email:
        return True  # Email is optional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def calculate_age(birth_date):
    """Calculate age from birth date"""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
    elif isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def format_currency(amount):
    """Format currency in Egyptian pounds"""
    return f"{amount:,.2f} ج.م"

def format_date_arabic(date_obj):
    """Format date in Arabic"""
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
    
    months_arabic = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    
    return f"{date_obj.day} {months_arabic[date_obj.month]} {date_obj.year}"

def show_success_message(message):
    """Show success message"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """Show error message"""
    st.error(f"❌ {message}")

def show_warning_message(message):
    """Show warning message"""
    st.warning(f"⚠️ {message}")

def show_info_message(message):
    """Show info message"""
    st.info(f"ℹ️ {message}")

def get_appointment_time_slots():
    """Get available time slots for appointments"""
    slots = []
    start_hour = 9  # 9 AM
    end_hour = 17   # 5 PM
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:  # Every 30 minutes
            time_str = f"{hour:02d}:{minute:02d}"
            slots.append(time_str)
    
    return slots

def get_status_color(status):
    """Get color for appointment status"""
    colors = {
        'مجدول': '#FFA500',      # Orange
        'مكتمل': '#008000',       # Green
        'ملغي': '#FF0000',        # Red
        'لم يحضر': '#808080',     # Gray
        'مؤجل': '#0000FF'        # Blue
    }
    return colors.get(status, '#000000')

def get_date_range_options():
    """Get predefined date range options"""
    today = date.today()
    
    return {
        'اليوم': (today, today),
        'أمس': (today - timedelta(days=1), today - timedelta(days=1)),
        'آخر 7 أيام': (today - timedelta(days=7), today),
        'آخر 30 يوم': (today - timedelta(days=30), today),
        'هذا الشهر': (today.replace(day=1), today),
        'الشهر الماضي': (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1) - timedelta(days=1)
        ),
        'آخر 3 شهور': (today - timedelta(days=90), today),
        'هذا العام': (today.replace(month=1, day=1), today),
        'العام الماضي': (
            date(today.year - 1, 1, 1),
            date(today.year - 1, 12, 31)
        ),
        'كل الفترة': (date(2020, 1, 1), today)
    }

def filter_dataframe_by_date(df, date_column, start_date, end_date):
    """Filter dataframe by date range"""
    if df.empty:
        return df
    
    df[date_column] = pd.to_datetime(df[date_column]).dt.date
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    return df.loc[mask]

def create_summary_cards(revenue, expenses, profit, appointments_count):
    """Create summary cards for dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 إجمالي الإيرادات",
            value=format_currency(revenue),
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 إجمالي المصروفات", 
            value=format_currency(expenses),
            delta=None
        )
    
    with col3:
        profit_color = "normal" if profit >= 0 else "inverse"
        st.metric(
            label="📊 صافي الربح",
            value=format_currency(profit),
            delta=None
        )
    
    with col4:
        st.metric(
            label="📅 مواعيد اليوم",
            value=appointments_count,
            delta=None
        )

def create_revenue_chart(payments_df):
    """Create revenue chart"""
    if payments_df.empty:
        return None
    
    # Group by date
    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
    daily_revenue = payments_df.groupby(payments_df['payment_date'].dt.date)['amount'].sum().reset_index()
    
    if daily_revenue.empty:
        return None
    
    fig = px.line(
        daily_revenue, 
        x='payment_date', 
        y='amount',
        title='الإيرادات اليومية',
        labels={'payment_date': 'التاريخ', 'amount': 'المبلغ (ج.م)'}
    )
    
    fig.update_layout(
        xaxis_title="التاريخ",
        yaxis_title="المبلغ (ج.م)",
        font=dict(size=12)
    )
    
    return fig

def create_expenses_pie_chart(expenses_df):
    """Create expenses pie chart"""
    if expenses_df.empty:
        return None
    
    category_expenses = expenses_df.groupby('category')['amount'].sum().reset_index()
    
    if category_expenses.empty:
        return None
    
    fig = px.pie(
        category_expenses,
        values='amount',
        names='category',
        title='توزيع المصروفات حسب الفئة'
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_appointments_status_chart(appointments_df):
    """Create appointments status chart"""
    if appointments_df.empty:
        return None
    
    status_counts = appointments_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']
    
    colors = [get_status_color(status) for status in status_counts['status']]
    
    fig = px.pie(
        status_counts,
        values='count',
        names='status',
        title='توزيع المواعيد حسب الحالة',
        color_discrete_sequence=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig

def create_doctor_performance_chart(appointments_df, payments_df):
    """Create doctor performance chart"""
    if appointments_df.empty:
        return None
    
    # Count appointments per doctor
    doctor_appointments = appointments_df.groupby('doctor_name').size().reset_index(name='appointments_count')
    
    # Calculate revenue per doctor if payments data available
    if not payments_df.empty:
        doctor_revenue = payments_df.groupby('doctor_name')['amount'].sum().reset_index()
        doctor_performance = pd.merge(doctor_appointments, doctor_revenue, on='doctor_name', how='left')
        doctor_performance['amount'] = doctor_performance['amount'].fillna(0)
    else:
        doctor_performance = doctor_appointments
        doctor_performance['amount'] = 0
    
    fig = px.bar(
        doctor_performance,
        x='doctor_name',
        y='appointments_count',
        title='عدد المواعيد لكل طبيب',
        labels={'doctor_name': 'اسم الطبيب', 'appointments_count': 'عدد المواعيد'}
    )
    
    fig.update_layout(
        xaxis_title="اسم الطبيب",
        yaxis_title="عدد المواعيد",
        xaxis_tickangle=-45,
        font=dict(size=12)
    )
    
    return fig

def export_dataframe_to_excel(df, filename):
    """Export dataframe to Excel file"""
    try:
        import io
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='البيانات')
        
        output.seek(0)
        
        return output.getvalue()
    
    except ImportError:
        st.error("مكتبة openpyxl غير متوفرة لتصدير ملفات Excel")
        return None

def create_pdf_report(data, title="تقرير"):
    """Create PDF report (placeholder - requires reportlab)"""
    st.info("ميزة تصدير PDF ستكون متاحة قريباً")
    return None

def get_gender_options():
    """Get gender options in Arabic"""
    return ['ذكر', 'أنثى']

def get_appointment_status_options():
    """Get appointment status options"""
    return ['مجدول', 'مكتمل', 'ملغي', 'لم يحضر', 'مؤجل']

def get_payment_method_options():
    """Get payment method options"""
    return ['نقدي', 'بطاقة ائتمان', 'بطاقة خصم', 'تحويل بنكي', 'فيزا', 'ماستركارد']

def get_expense_categories():
    """Get expense categories"""
    return [
        'رواتب ومكافآت',
        'إيجار ومرافق',
        'أدوية ومستلزمات طبية',
        'معدات وأجهزة',
        'صيانة وإصلاحات',
        'مواصلات وانتقالات',
        'إعلان وتسويق',
        'رسوم ومصاريف إدارية',
        'تأمين',
        'ضرائب ورسوم',
        'أخرى'
    ]

def get_inventory_categories():
    """Get inventory categories"""
    return [
        'أدوية',
        'مستلزمات طبية',
        'معدات طبية',
        'مواد تنظيف',
        'قرطاسية ومكتبية',
        'أخرى'
    ]

def get_medical_specializations():
    """Get medical specializations in Arabic"""
    return [
        'طب عام',
        'طب أطفال',
        'طب نساء وتوليد', 
        'طب أسنان',
        'طب عيون',
        'طب أنف وأذن وحنجرة',
        'طب جلدية',
        'طب قلب وأوعية دموية',
        'طب عظام',
        'طب نفسي',
        'طب باطنة',
        'جراحة عامة',
        'طب مخ وأعصاب',
        'طب مسالك بولية',
        'طب تخدير',
        'أشعة وتصوير طبي',
        'تحاليل طبية',
        'علاج طبيعي',
        'تغذية علاجية',
        'أخرى'
    ]

def validate_license_number(license_number):
    """Validate medical license number"""
    if not license_number:
        return False
    
    # Basic validation - adjust according to your requirements
    return len(license_number.strip()) >= 3

def format_phone_number(phone):
    """Format phone number for display"""
    if not phone:
        return ""
    
    # Remove spaces and dashes
    clean_phone = re.sub(r'[-\s]', '', phone)
    
    # Format Egyptian mobile numbers
    if clean_phone.startswith('01') and len(clean_phone) == 11:
        return f"{clean_phone[:3]}-{clean_phone[3:6]}-{clean_phone[6:]}"
    
    return phone

def calculate_treatment_duration(start_time, end_time):
    """Calculate treatment duration in minutes"""
    try:
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        duration = (end - start).seconds // 60
        return duration
    except:
        return 0

def get_working_hours():
    """Get clinic working hours"""
    return {
        'start': '09:00',
        'end': '17:00',
        'break_start': '13:00',
        'break_end': '14:00'
    }

def is_working_time(time_str):
    """Check if given time is within working hours"""
    working_hours = get_working_hours()
    
    try:
        appointment_time = datetime.strptime(time_str, '%H:%M').time()
        start_time = datetime.strptime(working_hours['start'], '%H:%M').time()
        end_time = datetime.strptime(working_hours['end'], '%H:%M').time()
        break_start = datetime.strptime(working_hours['break_start'], '%H:%M').time()
        break_end = datetime.strptime(working_hours['break_end'], '%H:%M').time()
        
        # Check if within working hours but not during break
        is_working = (start_time <= appointment_time <= end_time)
        is_break = (break_start <= appointment_time <= break_end)
        
        return is_working and not is_break
    
    except:
        return False

def generate_patient_id():
    """Generate unique patient ID"""
    from datetime import datetime
    import random
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(100, 999)
    return f"P{timestamp}{random_num}"

def search_dataframe(df, search_term, search_columns):
    """Search dataframe in multiple columns"""
    if df.empty or not search_term:
        return df
    
    mask = pd.Series([False] * len(df))
    
    for column in search_columns:
        if column in df.columns:
            mask |= df[column].astype(str).str.contains(search_term, case=False, na=False)
    
    return df[mask]

def calculate_monthly_revenue(payments_df, year, month):
    """Calculate revenue for specific month"""
    if payments_df.empty:
        return 0
    
    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
    monthly_payments = payments_df[
        (payments_df['payment_date'].dt.year == year) & 
        (payments_df['payment_date'].dt.month == month)
    ]
    
    return monthly_payments['amount'].sum()

def get_top_treatments(appointments_df, limit=10):
    """Get most popular treatments"""
    if appointments_df.empty:
        return pd.DataFrame()
    
    treatment_counts = appointments_df['treatment_name'].value_counts().head(limit)
    return treatment_counts.reset_index()

def calculate_doctor_revenue(appointments_df, payments_df, doctor_name):
    """Calculate revenue for specific doctor"""
    if payments_df.empty:
        return 0
    
    doctor_payments = payments_df[payments_df['doctor_name'] == doctor_name]
    return doctor_payments['amount'].sum()

def get_patient_history(appointments_df, payments_df, patient_name):
    """Get patient's appointment and payment history"""
    patient_appointments = appointments_df[appointments_df['patient_name'] == patient_name].copy()
    patient_payments = payments_df[payments_df['patient_name'] == patient_name].copy()
    
    return {
        'appointments': patient_appointments,
        'payments': patient_payments,
        'total_visits': len(patient_appointments),
        'total_paid': patient_payments['amount'].sum() if not patient_payments.empty else 0
    }