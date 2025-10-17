import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud

def render():
    """صفحة إدارة المواعيد"""
    st.markdown("### 📅 إدارة المواعيد")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 جميع المواعيد", "➕ موعد جديد", "🔍 بحث", "📊 جدول الأطباء"])
    
    with tab1:
        render_all_appointments()
    
    with tab2:
        render_add_appointment()
    
    with tab3:
        render_search_appointments()
    
    with tab4:
        render_doctor_schedule()

def render_all_appointments():
    """عرض جميع المواعيد"""
    appointments = crud.get_all_appointments()
    if not appointments.empty:
        # فلترة حسب الحالة
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.selectbox("فلترة حسب الحالة", ["الكل"] + appointments['status'].unique().tolist())
        
        with col2:
            if not appointments.empty:
                doctors = appointments['doctor_name'].unique().tolist()
                doctor_filter = st.selectbox("فلترة حسب الطبيب", ["الكل"] + doctors)
        
        with col3:
            date_filter = st.date_input("التاريخ (اختياري)", value=None)
        
        # تطبيق الفلاتر
        filtered_appointments = appointments.copy()
        
        if status_filter != "الكل":
            filtered_appointments = filtered_appointments[filtered_appointments['status'] == status_filter]
        
        if doctor_filter != "الكل":
            filtered_appointments = filtered_appointments[filtered_appointments['doctor_name'] == doctor_filter]
        
        if date_filter:
            filtered_appointments = filtered_appointments[
                filtered_appointments['appointment_date'] == date_filter.isoformat()
            ]
        
        st.dataframe(
            filtered_appointments[['id', 'patient_name', 'doctor_name', 'treatment_name', 
                                  'appointment_date', 'appointment_time', 'status', 'total_cost']],
            use_container_width=True,
            hide_index=True
        )
        
        # تحديث حالة الموعد
        st.markdown("#### تحديث حالة موعد")
        col1, col2, col3 = st.columns(3)
        with col1:
            appointment_id = st.number_input("رقم الموعد", min_value=1, step=1)
        with col2:
            new_status = st.selectbox("الحالة الجديدة", ["مجدول", "مؤكد", "مكتمل", "ملغي"])
        with col3:
            if st.button("تحديث الحالة"):
                try:
                    crud.update_appointment_status(appointment_id, new_status)
                    st.success("✅ تم تحديث الحالة بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
    else:
        st.info("لا توجد مواعيد")

def render_add_appointment():
    """نموذج إضافة موعد جديد"""
    st.markdown("#### إضافة موعد جديد")
    
    patients = crud.get_all_patients()
    doctors = crud.get_all_doctors()
    treatments = crud.get_all_treatments()
    
    if patients.empty or doctors.empty:
        st.warning("يجب إضافة مرضى وأطباء أولاً")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.selectbox(
                "المريض*",
                patients['id'].tolist(),
                format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
            )
            
            treatment_id = st.selectbox(
                "العلاج*",
                treatments['id'].tolist(),
                format_func=lambda x: treatments[treatments['id'] == x]['name'].iloc[0]
            ) if not treatments.empty else None
            
            appointment_date = st.date_input("تاريخ الموعد*", min_value=date.today())
        
        with col2:
            doctor_id = st.selectbox(
                "الطبيب*",
                doctors['id'].tolist(),
                format_func=lambda x: doctors[doctors['id'] == x]['name'].iloc[0]
            )
            
            appointment_time = st.time_input("وقت الموعد*")
            
            if treatment_id:
                total_cost = treatments[treatments['id'] == treatment_id]['base_price'].iloc[0]
                total_cost = st.number_input("التكلفة الإجمالية*", value=float(total_cost), min_value=0.0, step=10.0)
            else:
                total_cost = st.number_input("التكلفة الإجمالية*", min_value=0.0, step=10.0)
        
        notes = st.text_area("ملاحظات")
        
        if st.button("حجز الموعد", type="primary", use_container_width=True):
            try:
                crud.create_appointment(
                    patient_id,
                    doctor_id,
                    treatment_id,
                    appointment_date.isoformat(),
                    appointment_time.strftime("%H:%M"),
                    notes,
                    total_cost
                )
                st.success("✅ تم حجز الموعد بنجاح!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")

def render_search_appointments():
    """البحث عن مواعيد"""
    st.markdown("#### البحث عن مواعيد")
    
    col1, col2 = st.columns(2)
    with col1:
        search_date = st.date_input("البحث بالتاريخ")
    with col2:
        st.write("")
    
    if st.button("بحث"):
        results = crud.get_appointments_by_date(search_date.isoformat())
        if not results.empty:
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد مواعيد في هذا التاريخ")

def render_doctor_schedule():
    """جدول مواعيد الأطباء"""
    st.markdown("#### جدول مواعيد الأطباء")
    
    doctors = crud.get_all_doctors()
    if not doctors.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_doctor = st.selectbox(
                "اختر الطبيب",
                doctors['id'].tolist(),
                format_func=lambda x: doctors[doctors['id'] == x]['name'].iloc[0]
            )
        
        with col2:
            schedule_date = st.date_input("التاريخ", value=date.today())
        
        if st.button("عرض الجدول"):
            schedule = crud.get_doctor_schedule(selected_doctor, schedule_date.isoformat())
            if not schedule.empty:
                st.dataframe(schedule, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد مواعيد لهذا الطبيب في هذا التاريخ")
