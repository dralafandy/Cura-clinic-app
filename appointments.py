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
        ["عرض المواعيد", "حجز موعد جديد", "تقويم المواعيد", "تقارير المواعيد", "حسابات المواعيد"]
    )
    
    if action == "عرض المواعيد":
        show_appointments_list()
    elif action == "حجز موعد جديد":
        book_new_appointment()
    elif action == "تقويم المواعيد":
        appointments_calendar()
    elif action == "تقارير المواعيد":
        appointments_reports()
    elif action == "حسابات المواعيد":
        appointment_accounts()

def show_appointments_list():
    """عرض قائمة المواعيد"""
    st.subheader("📋 قائمة المواعيد")
    
    try:
        appointments_df = crud.get_all_appointments()
        
        if appointments_df.empty:
            st.info("لا توجد مواعيد")
            return
        
        # فلاتر البحث والتصفية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # فلترة حسب التاريخ
            date_filter = st.selectbox(
                "فلترة حسب التاريخ",
                ["الكل", "اليوم", "غداً", "هذا الأسبوع", "هذا الشهر"]
            )
        
        with col2:
            # فلترة حسب الطبيب
            doctors = ["الكل"] + list(appointments_df['doctor_name'].unique())
            selected_doctor = st.selectbox("فلترة حسب الطبيب", doctors)
        
        with col3:
            # فلترة حسب الحالة
            statuses = ["الكل"] + list(appointments_df['status'].unique())
            selected_status = st.selectbox("فلترة حسب الحالة", statuses)
        
        # تطبيق الفلاتر
        filtered_df = apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status)
        
        if filtered_df.empty:
            st.info("لا توجد مواعيد تطابق المعايير المحددة")
            return
        
        # عرض الإحصائيات السريعة
        show_appointments_summary(filtered_df)
        
        # عرض المواعيد في بطاقات
        display_appointments_cards(filtered_df)
        
        # جدول المواعيد التفصيلي
        st.divider()
        st.subheader("📊 جدول المواعيد التفصيلي")
        
        display_appointments_table(filtered_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل المواعيد: {str(e)}")

def apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status):
    filtered_df = appointments_df.copy()
    filtered_df['appointment_date'] = pd.to_datetime(filtered_df['appointment_date']).dt.date
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
        start_month = today.replace(day=1)
        end_month = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
        filtered_df = filtered_df[(filtered_df['appointment_date'] >= start_month) & (filtered_df['appointment_date'] <= end_month)]
    if selected_doctor != "الكل":
        filtered_df = filtered_df[filtered_df['doctor_name'] == selected_doctor]
    if selected_status != "الكل":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    return filtered_df

def show_appointments_summary(filtered_df):
    col1, col2, col3 = st.columns(3)
    with col1:
        total_appointments = len(filtered_df)
        st.metric("📅 إجمالي المواعيد", total_appointments)
    with col2:
        completed = len(filtered_df[filtered_df['status'] == 'مكتمل'])
        st.metric("✅ المواعيد المكتملة", completed)
    with col3:
        total_revenue = filtered_df['total_cost'].sum()
        st.metric("💰 إجمالي الإيرادات", format_currency(total_revenue))

def display_appointments_cards(filtered_df):
    """عرض المواعيد كبطاقات"""
    for _, appt in filtered_df.iterrows():
        with st.expander(f"موعد {appt['appointment_date']} - {appt['appointment_time']} مع {appt['patient_name']}"):
            st.info(f"""
            **تفاصيل الموعد:**
            - **الطبيب:** {appt['doctor_name']}
            - **العلاج:** {appt['treatment_name']}
            - **التكلفة:** {format_currency(appt['total_cost'])}
            - **الحالة:** {appt['status']}
            - **ملاحظات:** {appt['notes'] or 'لا يوجد'}
            """)
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✏️ تعديل", key=f"edit_{appt['id']}"):
                    edit_appointment(appt['id'])
            with col_b:
                if st.button("🗑️ حذف", key=f"delete_{appt['id']}"):
                    delete_appointment(appt['id'])

def display_appointments_table(filtered_df):
    """عرض جدول المواعيد"""
    st.dataframe(
        filtered_df[['patient_name', 'doctor_name', 'treatment_name', 'appointment_date', 'appointment_time', 'status', 'total_cost', 'notes']],
        column_config={
            'patient_name': 'اسم المريض',
            'doctor_name': 'اسم الطبيب',
            'treatment_name': 'العلاج',
            'appointment_date': st.column_config.DateColumn('التاريخ'),
            'appointment_time': 'الوقت',
            'status': 'الحالة',
            'total_cost': st.column_config.NumberColumn('التكلفة', format="%.2f ج.م"),
            'notes': 'ملاحظات'
        },
        use_container_width=True,
        hide_index=True
    )

def book_new_appointment():
    """حجز موعد جديد"""
    st.subheader("➕ حجز موعد جديد")
    
    try:
        patients_df = crud.get_all_patients()
        doctors_df = crud.get_all_doctors()
        treatments_df = crud.get_all_treatments()
        
        if patients_df.empty:
            st.error("يجب إضافة مرضى أولاً")
            return
        
        if doctors_df.empty:
            st.error("يجب إضافة أطباء أولاً")
            return
        
        if treatments_df.empty:
            st.error("يجب إضافة علاجات أولاً")
            return
        
        with st.form("book_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 معلومات المريض")
                
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" 
                                 for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox(
                    "اختر المريض *",
                    options=list(patient_options.keys()),
                    format_func=lambda x: patient_options[x]
                )
                
                if selected_patient_id:
                    patient_info = patients_df[patients_df['id'] == selected_patient_id].iloc[0]
                    st.info(f"""
                    **📋 معلومات المريض:**
                    - **الاسم:** {patient_info['name']}
                    - **الهاتف:** {patient_info['phone'] or 'غير محدد'}
                    - **العمر:** {calculate_age(patient_info['date_of_birth'])} سنة
                    - **التاريخ الطبي:** {patient_info['medical_history'] or 'لا يوجد'}
                    """)
            
            with col2:
                st.subheader("👨‍⚕️ معلومات الطبيب والموعد")
                
                doctor_options = {row['id']: f"{row['name']} - {row['specialization']}" 
                                 for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox(
                    "اختر الطبيب *",
                    options=list(doctor_options.keys()),
                    format_func=lambda x: doctor_options[x]
                )
                
                if selected_doctor_id:
                    st.info(f"نسبة العمولة للطبيب: {doctors_df[doctors_df['id'] == selected_doctor_id]['commission_rate'].iloc[0]}%")
                
                appointment_date = st.date_input("تاريخ الموعد *", min_value=date.today())
                
                if selected_doctor_id and appointment_date:
                    time_slots = get_appointment_time_slots(selected_doctor_id, appointment_date)
                    appointment_time = st.selectbox("اختر الوقت *", time_slots)
            
            st.subheader("💊 اختيار العلاج")
            treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])} (عمولة: {row['commission_rate']}%)" 
                                 for _, row in treatments_df.iterrows()}
            selected_treatment_id = st.selectbox(
                "اختر العلاج *",
                options=list(treatment_options.keys()),
                format_func=lambda x: treatment_options[x]
            )
            
            notes = st.text_area("ملاحظات")
            submitted = st.form_submit_button("📅 حجز الموعد")
            
            if submitted:
                if not (selected_patient_id and selected_doctor_id and appointment_date and appointment_time and selected_treatment_id):
                    show_error_message("يجب ملء جميع الحقول المطلوبة")
                else:
                    treatment_info = treatments_df[treatments_df['id'] == selected_treatment_id].iloc[0]
                    total_cost = treatment_info['base_price']
                    commission_rate = treatment_info['commission_rate']
                    appointment_id = crud.create_appointment(
                        patient_id=selected_patient_id,
                        doctor_id=selected_doctor_id,
                        treatment_id=selected_treatment_id,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        notes=notes,
                        total_cost=total_cost
                    )
                    show_success_message(f"تم حجز الموعد رقم {appointment_id} بنجاح. التكلفة: {format_currency(total_cost)}")
                    st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في حجز الموعد: {str(e)}")

def appointments_calendar():
    """تقويم المواعيد"""
    st.subheader("🗓️ تقويم المواعيد")
    # Implementation as in previous code (use calendar.monthcalendar or streamlit_calendar if installed)
    # For simplicity, use basic calendar view
    year = st.number_input("السنة", value=date.today().year)
    month = st.number_input("الشهر", value=date.today().month, min_value=1, max_value=12)
    # Code for calendar display...

def appointments_reports():
    """تقارير المواعيد"""
    st.subheader("📊 تقارير المواعيد")
    # Implementation as in previous code...

def appointment_accounts():
    """حسابات المواعيد"""
    st.subheader("💳 حسابات المواعيد")
    # Implementation as in previous code...

def edit_appointment(appointment_id):
    """تعديل موعد"""
    st.subheader(f"✏️ تعديل الموعد رقم {appointment_id}")
    # Implementation as in previous code...

def delete_appointment(appointment_id):
    """حذف موعد"""
    crud.delete_appointment(appointment_id)
    show_success_message("تم حذف الموعد بنجاح")
    st.rerun()

if __name__ == "__main__":
    show_appointments()
