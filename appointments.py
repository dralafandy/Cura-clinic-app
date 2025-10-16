import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message,
    format_date_arabic, get_appointment_time_slots, get_status_color
)

def show_appointments():
    st.title("📅 إدارة المواعيد")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات المواعيد")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المواعيد", "حجز موعد جديد", "تقويم المواعيد", "تقارير المواعيد"]
    )
    
    if action == "عرض المواعيد":
        show_appointments_list()
    elif action == "حجز موعد جديد":
        book_new_appointment()
    elif action == "تقويم المواعيد":
        appointments_calendar()
    elif action == "تقارير المواعيد":
        appointments_reports()

def show_appointments_list():
    """عرض قائمة المواعيد"""
    st.subheader("📋 قائمة المواعيد")
    
    try:
        # Retrieve base appointments data
        appointments_df = crud.get_all_appointments()
        
        if appointments_df.empty:
            st.info("لا توجد مواعيد")
            return
        
        # Join with patients, doctors, and treatments for meaningful display
        conn = crud.db.get_connection()
        appointments_df = pd.read_sql_query("""
            SELECT a.*, p.name AS patient_name, d.name AS doctor_name, t.name AS treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
        """, conn)
        conn.close()
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_filter = st.selectbox(
                "فلترة حسب التاريخ",
                ["الكل", "اليوم", "غداً", "هذا الأسبوع", "هذا الشهر"]
            )
        
        with col2:
            doctors = ["الكل"] + list(appointments_df['doctor_name'].dropna().unique())
            selected_doctor = st.selectbox("فلترة حسب الطبيب", doctors)
        
        with col3:
            statuses = ["الكل"] + list(appointments_df['status'].unique())
            selected_status = st.selectbox("فلترة حسب الحالة", statuses)
        
        # Apply filters
        filtered_df = apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status)
        
        if filtered_df.empty:
            st.info("لا توجد مواعيد تطابق المعايير المحددة")
            return
        
        # Display summary
        show_appointments_summary(filtered_df)
        
        # Display appointments as cards or table
        display_appointments_cards(filtered_df)
        st.divider()
        st.subheader("📊 جدول المواعيد التفصيلي")
        display_appointments_table(filtered_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل المواعيد: {str(e)}")

def apply_appointments_filters(df, date_filter, selected_doctor, selected_status):
    """Apply filters to appointments DataFrame"""
    filtered_df = df.copy()
    
    today = date.today()
    if date_filter == "اليوم":
        filtered_df = filtered_df[filtered_df['appointment_date'] == today]
    elif date_filter == "غداً":
        filtered_df = filtered_df[filtered_df['appointment_date'] == today + timedelta(days=1)]
    elif date_filter == "هذا الأسبوع":
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        filtered_df = filtered_df[(filtered_df['appointment_date'] >= start_week) & (filtered_df['appointment_date'] <= end_week)]
    elif date_filter == "هذا الشهر":
        filtered_df = filtered_df[filtered_df['appointment_date'].dt.month == today.month]
    
    if selected_doctor != "الكل":
        filtered_df = filtered_df[filtered_df['doctor_name'] == selected_doctor]
    if selected_status != "الكل":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    return filtered_df

def show_appointments_summary(df):
    """Display quick statistics"""
    total = len(df)
    completed = len(df[df['status'] == 'مكتمل'])
    st.write(f"📊 **إجمالي المواعيد:** {total} | **مكتملة:** {completed} ({(completed/total*100):.1f}%)")

def display_appointments_cards(df):
    """Display appointments as cards"""
    for _, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{row['patient_name']}** - {row['treatment_name']}")
                st.write(f"📅 {format_date_arabic(row['appointment_date'])} {row['appointment_time']}")
                st.write(f"👨‍⚕️ {row['doctor_name']}")
            with col2:
                st.write(f"💰 {format_currency(row['total_cost'] or 0)}")
                st.write(f"🏷️ {row['status']}", unsafe_allow_html=get_status_color(row['status']))

def display_appointments_table(df):
    """Display appointments in a table"""
    st.dataframe(df[['patient_name', 'doctor_name', 'treatment_name', 'appointment_date', 'appointment_time', 'total_cost', 'status']],
                 use_container_width=True, hide_index=True)

def book_new_appointment():
    """حجز موعد جديد"""
    st.subheader("➕ حجز موعد جديد")
    
    try:
        patients_df = crud.get_all_patients()
        doctors_df = crud.get_all_doctors()
        treatments_df = crud.get_all_treatments()
        
        if patients_df.empty or doctors_df.empty or treatments_df.empty:
            st.error("يجب إضافة مرضى وأطباء وعلاجات أولاً")
            return
        
        with st.form("book_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 معلومات المريض")
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox("اختر المريض *", options=list(patient_options.keys()),
                                                 format_func=lambda x: patient_options[x])
                
                doctor_options = {row['id']: row['name'] for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox("اختر الطبيب *", options=list(doctor_options.keys()),
                                                format_func=lambda x: doctor_options[x])
            
            with col2:
                st.subheader("📅 تفاصيل الموعد")
                appointment_date = st.date_input("تاريخ الموعد *", min_value=date.today())
                time_slots = get_appointment_time_slots()
                selected_time = st.selectbox("الوقت *", options=time_slots)
                treatment_options = {row['id']: row['name'] for _, row in treatments_df.iterrows()}
                selected_treatment_id = st.selectbox("اختر العلاج", options=list(treatment_options.keys()),
                                                   format_func=lambda x: treatment_options[x])
                
                notes = st.text_area("ملاحظات", placeholder="أي ملاحظات إضافية")
            
            if st.form_submit_button("📅 حجز الموعد"):
                crud.create_appointment(
                    patient_id=selected_patient_id,
                    doctor_id=selected_doctor_id,
                    treatment_id=selected_treatment_id,
                    appointment_date=appointment_date,
                    appointment_time=selected_time,
                    status='مجدول',
                    notes=notes,
                    total_cost=treatments_df[treatments_df['id'] == selected_treatment_id]['base_price'].iloc[0]
                )
                show_success_message("تم حجز الموعد بنجاح")
                st.rerun()
                
    except Exception as e:
        show_error_message(f"خطأ في حجز الموعد: {str(e)}")

def appointments_calendar():
    """عرض تقويم المواعيد"""
    st.subheader("📅 تقويم المواعيد")
    
    try:
        today = date.today()
        current_month = today.month
        current_year = today.year
        
        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox("الشهر", range(1, 13), index=current_month-1)
        with col2:
            selected_year = st.selectbox("السنة", range(2023, 2027), index=current_year-2023)
        
        import calendar
        cal = calendar.monthcalendar(selected_year, selected_month)
        
        st.write("### " + calendar.month_name[selected_month] + f" {selected_year}")
        days_header = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.write("")  # يوم فارغ
                    else:
                        current_date = date(selected_year, selected_month, day)
                        day_appointments = crud.get_all_appointments()
                        day_appointments = day_appointments[day_appointments['appointment_date'] == current_date.strftime('%Y-%m-%d')]
                        appointments_count = len(day_appointments) if not day_appointments.empty else 0
                        
                        if appointments_count > 0:
                            st.markdown(f"""
                            <div style="background-color: #e3f2fd; padding: 5px; border-radius: 5px; text-align: center;">
                            <strong>{day}</strong><br>
                            <small>{appointments_count} موعد</small>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="padding: 5px; text-align: center;">
                            {day}
                            </div>
                            """, unsafe_allow_html=True)
                            
    except Exception as e:
        show_error_message(f"خطأ في تحميل التقويم: {str(e)}")

def appointments_reports():
    """عرض تقارير المواعيد"""
    st.subheader("📊 تقارير المواعيد")
    # Add report logic here (e.g., statistics, analysis)
    st.info("سيتم إضافة التقارير قريباً")

if __name__ == "__main__":
    show_appointments()
