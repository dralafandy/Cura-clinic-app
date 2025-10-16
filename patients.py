import streamlit as st
import pandas as pd
from database.crud import CRUDOperations
from utils.helpers import show_success_message, show_error_message, validate_phone_number, validate_email, calculate_age

crud = CRUDOperations()

def show_patients():
    st.title("👤 إدارة المرضى")
    
    st.sidebar.subheader("خيارات المرضى")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المرضى", "إضافة مريض جديد", "تعديل مريض", "حذف مريض"]
    )
    
    if action == "عرض المرضى":
        show_patients_list()
    elif action == "إضافة مريض جديد":
        add_patient()
    elif action == "تعديل مريض":
        edit_patient()
    elif action == "حذف مريض":
        delete_patient()

def show_patients_list():
    """Display list of patients"""
    st.subheader("📋 قائمة المرضى")
    
    try:
        patients_df = crud.get_all_patients()
        
        if patients_df.empty:
            st.info("لا توجد مرضى لعرضهم")
            return
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            gender_filter = st.selectbox(
                "فلترة حسب الجنس",
                ["الكل", "ذكر", "أنثى"]
            )
        with col2:
            search_term = st.text_input("البحث باسم المريض")
        
        # Apply filters
        filtered_df = patients_df
        if gender_filter != "الكل":
            filtered_df = filtered_df[filtered_df['gender'] == gender_filter]
        if search_term:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
        
        if filtered_df.empty:
            st.info("لا توجد مرضى تطابق المعايير المحددة")
            return
        
        # Display summary
        st.metric("👤 إجمالي المرضى", len(filtered_df))
        
        # Display patients table
        filtered_df['age'] = filtered_df['date_of_birth'].apply(calculate_age)
        st.dataframe(
            filtered_df[['name', 'phone', 'email', 'age', 'gender', 'medical_history']],
            column_config={
                'name': 'اسم المريض',
                'phone': 'رقم الهاتف',
                'email': 'البريد الإلكتروني',
                'age': 'العمر',
                'gender': 'الجنس',
                'medical_history': 'التاريخ الطبي'
            },
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        show_error_message(f"خطأ في عرض المرضى: {str(e)}")

def add_patient():
    """Add a new patient"""
    st.subheader("➕ إضافة مريض جديد")
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المريض *", max_chars=100)
            phone = st.text_input("رقم الهاتف")
            email = st.text_input("البريد الإلكتروني")
            address = st.text_input("العنوان")
        with col2:
            date_of_birth = st.date_input("تاريخ الميلاد", max_value=date.today())
            gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
            medical_history = st.text_area("التاريخ الطبي")
            emergency_contact = st.text_input("جهة اتصال الطوارئ")
        
        submitted = st.form_submit_button("💾 إضافة المريض")
        
        if submitted:
            if not name:
                show_error_message("يجب إدخال اسم المريض")
            elif phone and not validate_phone_number(phone):
                show_error_message("رقم الهاتف غير صحيح")
            elif email and not validate_email(email):
                show_error_message("البريد الإلكتروني غير صحيح")
            else:
                try:
                    patient_id = crud.create_patient(
                        name=name,
                        phone=phone,
                        email=email,
                        address=address,
                        date_of_birth=date_of_birth,
                        gender=gender,
                        medical_history=medical_history,
                        emergency_contact=emergency_contact
                    )
                    show_success_message(f"تم إضافة المريض رقم {patient_id} بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في إضافة المريض: {str(e)}")

def edit_patient():
    """Edit an existing patient"""
    st.subheader("✏️ تعديل مريض")
    
    try:
        patients_df = crud.get_all_patients()
        if patients_df.empty:
            st.info("لا توجد مرضى لتعديلهم")
            return
        
        patient_options = {row['id']: f"{row['name']} - {row['phone']}" for _, row in patients_df.iterrows()}
        selected_patient_id = st.selectbox(
            "اختر المريض للتعديل",
            options=list(patient_options.keys()),
            format_func=lambda x: patient_options[x]
        )
        
        if selected_patient_id:
            patient = crud.get_patient_by_id(selected_patient_id)
            if not patient.empty:
                with st.form(f"edit_patient_form_{selected_patient_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("اسم المريض *", value=patient['name'], max_chars=100)
                        phone = st.text_input("رقم الهاتف", value=patient['phone'])
                        email = st.text_input("البريد الإلكتروني", value=patient['email'])
                        address = st.text_input("العنوان", value=patient['address'])
                    with col2:
                        date_of_birth = st.date_input("تاريخ الميلاد", value=pd.to_datetime(patient['date_of_birth']).date(), max_value=date.today())
                        gender = st.selectbox("الجنس", ["ذكر", "أنثى"], index=["ذكر", "أنثى"].index(patient['gender']))
                        medical_history = st.text_area("التاريخ الطبي", value=patient['medical_history'])
                        emergency_contact = st.text_input("جهة اتصال الطوارئ", value=patient['emergency_contact'])
                    
                    submitted = st.form_submit_button("💾 حفظ التعديلات")
                    
                    if submitted:
                        if not name:
                            show_error_message("يجب إدخال اسم المريض")
                        elif phone and not validate_phone_number(phone):
                            show_error_message("رقم الهاتف غير صحيح")
                        elif email and not validate_email(email):
                            show_error_message("البريد الإلكتروني غير صحيح")
                        else:
                            crud.update_patient(
                                patient_id=selected_patient_id,
                                name=name,
                                phone=phone,
                                email=email,
                                address=address,
                                date_of_birth=date_of_birth,
                                gender=gender,
                                medical_history=medical_history,
                                emergency_contact=emergency_contact
                            )
                            show_success_message("تم تعديل المريض بنجاح")
                            st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في تعديل المريض: {str(e)}")

def delete_patient():
    """Delete a patient"""
    st.subheader("🗑️ حذف مريض")
    
    try:
        patients_df = crud.get_all_patients()
        if patients_df.empty:
            st.info("لا توجد مرضى لحذفهم")
            return
        
        patient_options = {row['id']: f"{row['name']} - {row['phone']}" for _, row in patients_df.iterrows()}
        selected_patient_id = st.selectbox(
            "اختر المريض للحذف",
            options=list(patient_options.keys()),
            format_func=lambda x: patient_options[x]
        )
        
        if st.button("🗑️ حذف المريض"):
            try:
                crud.delete_patient(selected_patient_id)
                show_success_message("تم حذف المريض بنجاح")
                st.rerun()
            except Exception as e:
                show_error_message(f"خطأ في حذف المريض: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل المرضى: {str(e)}")

if __name__ == "__main__":
    show_patients()
