import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import pandas as pd
from database.crud import crud
from utils.helpers import (
create_revenue_chart, create_expenses_pie_chart,
create_appointments_status_chart, create_summary_cards,
create_doctor_performance_chart, format_currency,
get_date_range_options, filter_dataframe_by_date
)

def show_dashboard():
st.title(“🏥 لوحة التحكم الرئيسية”)

```
# فلترة التواريخ
st.sidebar.subheader("📊 فلترة التقارير")
date_ranges = get_date_range_options()
selected_range = st.sidebar.selectbox("اختر النطاق الزمني", options=list(date_ranges.keys()))
start_date, end_date = date_ranges[selected_range]

# عرض النطاق المحدد
st.sidebar.write(f"من: {start_date}")
st.sidebar.write(f"إلى: {end_date}")

# الحصول على البيانات
try:
    # البيانات المالية
    financial_summary = crud.get_financial_summary(start_date, end_date)
    
    # عدد المواعيد اليوم - تصحيح الخطأ هنا
    try:
        appointments_today_df = crud.get_appointments_by_date(date.today())
        appointments_today = len(appointments_today_df) if not appointments_today_df.empty else 0
    except:
        # إذا فشلت الدالة، نحاول طريقة بديلة
        all_appointments = crud.get_all_appointments()
        if not all_appointments.empty:
            all_appointments['appointment_date'] = pd.to_datetime(all_appointments['appointment_date']).dt.date
            appointments_today = len(all_appointments[all_appointments['appointment_date'] == date.today()])
        else:
            appointments_today = 0
    
    # عرض بطاقات الملخص
    create_summary_cards(
        financial_summary['total_revenue'],
        financial_summary['total_expenses'], 
        financial_summary['net_profit'],
        appointments_today
    )
    
    st.divider()
    
    # الرسوم البيانية
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 الإيرادات")
        payments_df = crud.get_all_payments()
        if not payments_df.empty:
            filtered_payments = filter_dataframe_by_date(payments_df, 'payment_date', start_date, end_date)
            revenue_chart = create_revenue_chart(filtered_payments)
            if revenue_chart:
                st.plotly_chart(revenue_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات إيرادات في هذه الفترة")
        else:
            st.info("لا توجد بيانات إيرادات")
    
    with col2:
        st.subheader("💸 المصروفات")
        expenses_df = crud.get_all_expenses()
        if not expenses_df.empty:
            filtered_expenses = filter_dataframe_by_date(expenses_df, 'expense_date', start_date, end_date)
            expenses_chart = create_expenses_pie_chart(filtered_expenses)
            if expenses_chart:
                st.plotly_chart(expenses_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات مصروفات في هذه الفترة")
        else:
            st.info("لا توجد بيانات مصروفات")
    
    st.divider()
    
    # المواعيد والأداء
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📅 حالة المواعيد")
        appointments_df = crud.get_all_appointments()
        if not appointments_df.empty:
            appointments_chart = create_appointments_status_chart(appointments_df)
            if appointments_chart:
                st.plotly_chart(appointments_chart, use_container_width=True)
        else:
            st.info("لا توجد مواعيد")
    
    with col4:
        st.subheader("👨‍⚕️ أداء الأطباء")
        if not appointments_df.empty:
            payments_df = crud.get_all_payments()
            doctor_chart = create_doctor_performance_chart(appointments_df, payments_df)
            if doctor_chart:
                st.plotly_chart(doctor_chart, use_container_width=True)
        else:
            st.info("لا توجد بيانات أداء")
    
    st.divider()
    
    # إحصائيات سريعة
    st.subheader("📊 إحصائيات سريعة")
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        total_patients = len(crud.get_all_patients())
        st.metric("👥 إجمالي المرضى", total_patients)
    
    with col6:
        total_doctors = len(crud.get_all_doctors())
        st.metric("👨‍⚕️ إجمالي الأطباء", total_doctors)
    
    with col7:
        total_treatments = len(crud.get_all_treatments())
        st.metric("💊 إجمالي العلاجات", total_treatments)
    
    with col8:
        inventory_df = crud.get_all_inventory()
        low_stock_count = len(crud.get_low_stock_items())
        st.metric("⚠️ تنبيهات المخزون", low_stock_count)
    
    # تنبيهات المخزون
    if low_stock_count > 0:
        st.divider()
        st.subheader("⚠️ تنبيهات المخزون")
        low_stock_items = crud.get_low_stock_items()
        
        for _, item in low_stock_items.iterrows():
            st.warning(f"🔔 **{item['item_name']}** - الكمية المتبقية: {item['quantity']} (الحد الأدنى: {item['min_stock_level']})")
    
    # المواعيد القادمة
    st.divider()
    st.subheader("📅 مواعيد اليوم")
    
    try:
        today_appointments = crud.get_appointments_by_date(date.today())
    except:
        # إذا فشلت، نستخدم طريقة بديلة
        all_appointments = crud.get_all_appointments()
        if not all_appointments.empty:
            all_appointments['appointment_date'] = pd.to_datetime(all_appointments['appointment_date']).dt.date
            today_appointments = all_appointments[all_appointments['appointment_date'] == date.today()].copy()
        else:
            today_appointments = pd.DataFrame()
    
    if not today_appointments.empty:
        st.dataframe(
            today_appointments[['patient_name', 'doctor_name', 'treatment_name', 'appointment_time', 'status']],
            column_config={
                'patient_name': 'اسم المريض',
                'doctor_name': 'اسم الطبيب', 
                'treatment_name': 'العلاج',
                'appointment_time': 'الوقت',
                'status': 'الحالة'
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا توجد مواعيد اليوم")
    
    # تحديث تلقائي
    if st.button("🔄 تحديث البيانات"):
        st.rerun()
        
except Exception as e:
    st.error(f"حدث خطأ في تحميل البيانات: {str(e)}")
    st.info("يرجى التأكد من إعداد قاعدة البيانات بشكل صحيح")
    
    # عرض تفاصيل الخطأ للمطور
    with st.expander("تفاصيل الخطأ (للمطور)"):
        import traceback
        st.code(traceback.format_exc())
```

def show_analytics():
“”“عرض التحليلات المتقدمة”””
st.title(“📊 التحليلات المتقدمة”)

```
try:
    # تحليل الإيرادات الشهرية
    st.subheader("📈 تحليل الإيرادات الشهرية")
    
    payments_df = crud.get_all_payments()
    if not payments_df.empty:
        payments_df_copy = payments_df.copy()
        payments_df_copy['payment_date'] = pd.to_datetime(payments_df_copy['payment_date'])
        payments_df_copy['month_year'] = payments_df_copy['payment_date'].dt.to_period('M')
        
        monthly_revenue = payments_df_copy.groupby('month_year')['amount'].sum().reset_index()
        monthly_revenue['month_year'] = monthly_revenue['month_year'].astype(str)
        
        fig = px.bar(monthly_revenue, x='month_year', y='amount',
                     title='الإيرادات الشهرية',
                     labels={'month_year': 'الشهر', 'amount': 'المبلغ (ج.م)'})
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات مدفوعات")
    
    # تحليل العلاجات الأكثر طلباً
    st.subheader("💊 العلاجات الأكثر طلباً")
    
    appointments_df = crud.get_all_appointments()
    if not appointments_df.empty:
        treatment_counts = appointments_df['treatment_name'].value_counts().head(10)
        
        fig = px.pie(values=treatment_counts.values, names=treatment_counts.index,
                     title='العلاجات الأكثر طلباً')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات مواعيد")
    
    # تحليل أوقات المواعيد المفضلة
    st.subheader("⏰ أوقات المواعيد المفضلة")
    
    if not appointments_df.empty:
        appointments_copy = appointments_df.copy()
        # التعامل مع أوقات المواعيد بشكل آمن
        try:
            appointments_copy['hour'] = pd.to_datetime(appointments_copy['appointment_time'], format='%H:%M', errors='coerce').dt.hour
            appointments_copy = appointments_copy.dropna(subset=['hour'])
            
            if not appointments_copy.empty:
                hourly_appointments = appointments_copy['hour'].value_counts().sort_index()
                
                fig = px.bar(x=hourly_appointments.index, y=hourly_appointments.values,
                             title='توزيع المواعيد حسب الساعة',
                             labels={'x': 'الساعة', 'y': 'عدد المواعيد'})
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد بيانات أوقات صالحة")
        except Exception as e:
            st.warning(f"لا يمكن تحليل أوقات المواعيد: {str(e)}")

except Exception as e:
    st.error(f"حدث خطأ في التحليلات: {str(e)}")
    with st.expander("تفاصيل الخطأ"):
        import traceback
        st.code(traceback.format_exc())
```

if **name** == “**main**”:
show_dashboard()
