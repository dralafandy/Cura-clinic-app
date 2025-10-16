import streamlit as st
import pandas as pd
from database.crud import CRUDOperations
from utils.helpers import show_success_message, show_error_message, validate_phone_number, validate_email

crud = CRUDOperations()

def show_suppliers():
    st.title("🏭 إدارة الموردين")
    
    st.sidebar.subheader("خيارات الموردين")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض الموردين", "إضافة مورد جديد", "تعديل مورد", "حذف مورد"]
    )
    
    if action == "عرض الموردين":
        show_suppliers_list()
    elif action == "إضافة مورد جديد":
        add_supplier()
    elif action == "تعديل مورد":
        edit_supplier()
    elif action == "حذف مورد":
        delete_supplier()

def show_suppliers_list():
    """Display list of suppliers"""
    st.subheader("📋 قائمة الموردين")
    
    try:
        suppliers_df = crud.get_all_suppliers()
        
        if suppliers_df.empty:
            st.info("لا توجد موردين لعرضهم")
            return
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("البحث باسم المورد")
        with col2:
            contact_filter = st.text_input("البحث باسم جهة الاتصال")
        
        # Apply filters
        filtered_df = suppliers_df
        if search_term:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
        if contact_filter:
            filtered_df = filtered_df[filtered_df['contact_person'].str.contains(contact_filter, case=False, na=False)]
        
        if filtered_df.empty:
            st.info("لا توجد موردين تطابق المعايير المحددة")
            return
        
        # Display summary
        st.metric("🏭 إجمالي الموردين", len(filtered_df))
        
        # Display suppliers table
        st.dataframe(
            filtered_df[['name', 'contact_person', 'phone', 'email', 'address']],
            column_config={
                'name': 'اسم المورد',
                'contact_person': 'جهة الاتصال',
                'phone': 'رقم الهاتف',
                'email': 'البريد الإلكتروني',
                'address': 'العنوان'
            },
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        show_error_message(f"خطأ في عرض الموردين: {str(e)}")

def add_supplier():
    """Add a new supplier"""
    st.subheader("➕ إضافة مورد جديد")
    
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم المورد *", max_chars=100)
            contact_person = st.text_input("جهة الاتصال", max_chars=100)
            phone = st.text_input("رقم الهاتف")
        with col2:
            email = st.text_input("البريد الإلكتروني")
            address = st.text_area("العنوان")
            notes = st.text_area("ملاحظات")
        
        submitted = st.form_submit_button("💾 إضافة المورد")
        
        if submitted:
            if not name:
                show_error_message("يجب إدخال اسم المورد")
            elif phone and not validate_phone_number(phone):
                show_error_message("رقم الهاتف غير صحيح")
            elif email and not validate_email(email):
                show_error_message("البريد الإلكتروني غير صحيح")
            else:
                try:
                    supplier_id = crud.create_supplier(
                        name=name,
                        contact_person=contact_person,
                        phone=phone,
                        email=email,
                        address=address,
                        notes=notes
                    )
                    show_success_message(f"تم إضافة المورد رقم {supplier_id} بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في إضافة المورد: {str(e)}")

def edit_supplier():
    """Edit an existing supplier"""
    st.subheader("✏️ تعديل مورد")
    
    try:
        suppliers_df = crud.get_all_suppliers()
        if suppliers_df.empty:
            st.info("لا توجد موردين لتعديلهم")
            return
        
        supplier_options = {row['id']: f"{row['name']} - {row['contact_person']}" for _, row in suppliers_df.iterrows()}
        selected_supplier_id = st.selectbox(
            "اختر المورد للتعديل",
            options=list(supplier_options.keys()),
            format_func=lambda x: supplier_options[x]
        )
        
        if selected_supplier_id:
            supplier = crud.get_supplier_by_id(selected_supplier_id)
            if not supplier.empty:
                with st.form(f"edit_supplier_form_{selected_supplier_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("اسم المورد *", value=supplier['name'], max_chars=100)
                        contact_person = st.text_input("جهة الاتصال", value=supplier['contact_person'], max_chars=100)
                        phone = st.text_input("رقم الهاتف", value=supplier['phone'])
                    with col2:
                        email = st.text_input("البريد الإلكتروني", value=supplier['email'])
                        address = st.text_area("العنوان", value=supplier['address'])
                        notes = st.text_area("ملاحظات", value=supplier['notes'] or "")
                    
                    submitted = st.form_submit_button("💾 حفظ التعديلات")
                    
                    if submitted:
                        if not name:
                            show_error_message("يجب إدخال اسم المورد")
                        elif phone and not validate_phone_number(phone):
                            show_error_message("رقم الهاتف غير صحيح")
                        elif email and not validate_email(email):
                            show_error_message("البريد الإلكتروني غير صحيح")
                        else:
                            crud.update_supplier(
                                supplier_id=selected_supplier_id,
                                name=name,
                                contact_person=contact_person,
                                phone=phone,
                                email=email,
                                address=address,
                                notes=notes
                            )
                            show_success_message("تم تعديل المورد بنجاح")
                            st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في تعديل المورد: {str(e)}")

def delete_supplier():
    """Delete a supplier"""
    st.subheader("🗑️ حذف مورد")
    
    try:
        suppliers_df = crud.get_all_suppliers()
        if suppliers_df.empty:
            st.info("لا توجد موردين لحذفهم")
            return
        
        supplier_options = {row['id']: f"{row['name']} - {row['contact_person']}" for _, row in suppliers_df.iterrows()}
        selected_supplier_id = st.selectbox(
            "اختر المورد للحذف",
            options=list(supplier_options.keys()),
            format_func=lambda x: supplier_options[x]
        )
        
        if st.button("🗑️ حذف المورد"):
            try:
                crud.delete_supplier(selected_supplier_id)
                show_success_message("تم حذف المورد بنجاح")
                st.rerun()
            except Exception as e:
                show_error_message(f"خطأ في حذف المورد: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل الموردين: {str(e)}")

if __name__ == "__main__":
    show_suppliers()
