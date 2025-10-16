import streamlit as st
import pandas as pd
from database.crud import CRUDOperations
from utils.helpers import show_success_message, show_error_message, validate_phone_number, validate_email

crud = CRUDOperations()

def show_doctors():
    st.title("👨‍⚕️ إدارة الأطباء")
    
    st.sidebar.subheader("خيارات الأطباء")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض الأطباء", "إضافة طبيب جديد", "تعديل طبيب", "حذف طبيب"]
    )
    
    if action == "عرض الأطباء":
        show_doctors_list()
    elif action == "إضافة طبيب جديد":
        add_doctor()
    elif action == "تعديل طبيب":
        edit_doctor()
    elif action == "حذف طبيب":
        delete_doctor()

def show_doctors_list():
    """Display list of doctors"""
    st.subheader("📋 قائمة الأطباء")
    
    try:
        doctors_df = crud.get_all_doctors()
        
        if doctors_df.empty:
            st.info("لا توجد أطباء لعرضهم")
            return
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            specialization_filter = st.selectbox(
                "فلترة حسب التخصص",
                ["الكل"] + list(doctors_df['specialization'].unique())
            )
        with col2:
            search_term = st.text_input("البحث باسم الطبيب")
        
        # Apply filters
        filtered_df = doctors_df
        if specialization_filter != "الكل":
            filtered_df = filtered_df[filtered_df['specialization'] == specialization_filter]
        if search_term:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
        
        if filtered_df.empty:
            st.info("لا توجد أطباء تطابق المعايير المحددة")
            return
        
        # Display summary
        st.metric("👨‍⚕️ إجمالي الأطباء", len(filtered_df))
        
        # Display doctors table
        st.dataframe(
            filtered_df[['name', 'specialization', 'phone', 'email', 'commission_rate']],
            column_config={
                'name': 'اسم الطبيب',
                'specialization': 'التخصص',
                'phone': 'رقم الهاتف',
                'email': 'البريد الإلكتروني',
                'commission_rate': st.column_config.NumberColumn('نسبة العمولة', format="%.2f%%")
            },
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        show_error_message(f"خطأ في عرض الأطباء: {str(e)}")

def add_doctor():
    """Add a new doctor"""
    st.subheader("➕ إضافة طبيب جديد")
    
    with st.form("add_doctor_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم الطبيب *", max_chars=100)
            specialization = st.text_input("التخصص *", max_chars=100)
            phone = st.text_input("رقم الهاتف")
        with col2:
            email = st.text_input("البريد الإلكتروني")
            commission_rate = st.number_input("نسبة العمولة (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
        
        submitted = st.form_submit_button("💾 إضافة الطبيب")
        
        if submitted:
            if not name or not specialization:
                show_error_message("يجب ملء الحقول المطلوبة (الاسم والتخصص)")
            elif phone and not validate_phone_number(phone):
                show_error_message("رقم الهاتف غير صحيح")
            elif email and not validate_email(email):
                show_error_message("البريد الإلكتروني غير صحيح")
            else:
                try:
                    doctor_id = crud.create_doctor(
                        name=name,
                        specialization=specialization,
                        phone=phone,
                        email=email,
                        commission_rate=commission_rate
                    )
                    show_success_message(f"تم إضافة الطبيب رقم {doctor_id} بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في إضافة الطبيب: {str(e)}")

def edit_doctor():
    """Edit an existing doctor"""
    st.subheader("✏️ تعديل طبيب")
    
    try:
        doctors_df = crud.get_all_doctors()
        if doctors_df.empty:
            st.info("لا توجد أطباء لتعديلهم")
            return
        
        doctor_options = {row['id']: f"{row['name']} - {row['specialization']}" for _, row in doctors_df.iterrows()}
        selected_doctor_id = st.selectbox(
            "اختر الطبيب للتعديل",
            options=list(doctor_options.keys()),
            format_func=lambda x: doctor_options[x]
        )
        
        if selected_doctor_id:
            doctor = crud.get_doctor_by_id(selected_doctor_id)
            if not doctor.empty:
                with st.form(f"edit_doctor_form_{selected_doctor_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("اسم الطبيب *", value=doctor['name'], max_chars=100)
                        specialization = st.text_input("التخصص *", value=doctor['specialization'], max_chars=100)
                        phone = st.text_input("رقم الهاتف", value=doctor['phone'])
                    with col2:
                        email = st.text_input("البريد الإلكتروني", value=doctor['email'])
                        commission_rate = st.number_input("نسبة العمولة (%)", min_value=0.0, max_value=100.0, value=doctor['commission_rate'], step=0.1)
                    
                    submitted = st.form_submit_button("💾 حفظ التعديلات")
                    
                    if submitted:
                        if not name or not specialization:
                            show_error_message("يجب ملء الحقول المطلوبة (الاسم والتخصص)")
                        elif phone and not validate_phone_number(phone):
                            show_error_message("رقم الهاتف غير صحيح")
                        elif email and not validate_email(email):
                            show_error_message("البريد الإلكتروني غير صحيح")
                        else:
                            crud.update_doctor(
                                doctor_id=selected_doctor_id,
                                name=name,
                                specialization=specialization,
                                phone=phone,
                                email=email,
                                commission_rate=commission_rate
                            )
                            show_success_message("تم تعديل الطبيب بنجاح")
                            st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في تعديل الطبيب: {str(e)}")

def delete_doctor():
    """Delete a doctor"""
    st.subheader("🗑️ حذف طبيب")
    
    try:
        doctors_df = crud.get_all_doctors()
        if doctors_df.empty:
            st.info("لا توجد أطباء لحذفهم")
            return
        
        doctor_options = {row['id']: f"{row['name']} - {row['specialization']}" for _, row in doctors_df.iterrows()}
        selected_doctor_id = st.selectbox(
            "اختر الطبيب للحذف",
            options=list(doctor_options.keys()),
            format_func=lambda x: doctor_options[x]
        )
        
        if st.button("🗑️ حذف الطبيب"):
            try:
                crud.delete_doctor(selected_doctor_id)
                show_success_message("تم حذف الطبيب بنجاح")
                st.rerun()
            except Exception as e:
                show_error_message(f"خطأ في حذف الطبيب: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل الأطباء: {str(e)}")

if __name__ == "__main__":
    show_doctors()
