import streamlit as st
import pandas as pd
from database.crud import CRUDOperations
from utils.helpers import show_success_message, show_error_message, format_currency

crud = CRUDOperations()

def show_treatments():
    st.title("💊 إدارة العلاجات")
    
    st.sidebar.subheader("خيارات العلاجات")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض العلاجات", "إضافة علاج جديد", "تعديل علاج", "حذف علاج"]
    )
    
    if action == "عرض العلاجات":
        show_treatments_list()
    elif action == "إضافة علاج جديد":
        add_treatment()
    elif action == "تعديل علاج":
        edit_treatment()
    elif action == "حذف علاج":
        delete_treatment()

def show_treatments_list():
    """Display list of treatments"""
    st.subheader("📋 قائمة العلاجات")
    
    try:
        treatments_df = crud.get_all_treatments()
        
        if treatments_df.empty:
            st.info("لا توجد علاجات لعرضها")
            return
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("البحث باسم العلاج")
        with col2:
            price_filter = st.selectbox(
                "فلترة حسب السعر",
                ["الكل", "أقل من 500 ج.م", "500-1000 ج.م", "أكثر من 1000 ج.م"]
            )
        
        # Apply filters
        filtered_df = treatments_df
        if search_term:
            filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
        if price_filter != "الكل":
            if price_filter == "أقل من 500 ج.م":
                filtered_df = filtered_df[filtered_df['base_price'] < 500]
            elif price_filter == "500-1000 ج.م":
                filtered_df = filtered_df[(filtered_df['base_price'] >= 500) & (filtered_df['base_price'] <= 1000)]
            elif price_filter == "أكثر من 1000 ج.م":
                filtered_df = filtered_df[filtered_df['base_price'] > 1000]
        
        if filtered_df.empty:
            st.info("لا توجد علاجات تطابق المعايير المحددة")
            return
        
        # Display summary
        st.metric("💊 إجمالي العلاجات", len(filtered_df))
        
        # Display treatments table
        st.dataframe(
            filtered_df[['name', 'base_price', 'commission_rate', 'notes']],
            column_config={
                'name': 'اسم العلاج',
                'base_price': st.column_config.NumberColumn('السعر الأساسي', format="%.2f ج.م"),
                'commission_rate': st.column_config.NumberColumn('نسبة العمولة', format="%.2f%%"),
                'notes': 'ملاحظات'
            },
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        show_error_message(f"خطأ في عرض العلاجات: {str(e)}")

def add_treatment():
    """Add a new treatment"""
    st.subheader("➕ إضافة علاج جديد")
    
    with st.form("add_treatment_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم العلاج *", max_chars=100)
            base_price = st.number_input("السعر الأساسي (ج.م) *", min_value=0.0, step=10.0)
        with col2:
            commission_rate = st.number_input("نسبة العمولة (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.1)
            notes = st.text_area("ملاحظات")
        
        submitted = st.form_submit_button("💾 إضافة العلاج")
        
        if submitted:
            if not name or not base_price:
                show_error_message("يجب ملء الحقول المطلوبة (الاسم والسعر الأساسي)")
            else:
                try:
                    treatment_id = crud.create_treatment(
                        name=name,
                        base_price=base_price,
                        commission_rate=commission_rate,
                        notes=notes
                    )
                    show_success_message(f"تم إضافة العلاج رقم {treatment_id} بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في إضافة العلاج: {str(e)}")

def edit_treatment():
    """Edit an existing treatment"""
    st.subheader("✏️ تعديل علاج")
    
    try:
        treatments_df = crud.get_all_treatments()
        if treatments_df.empty:
            st.info("لا توجد علاجات لتعديلها")
            return
        
        treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])}" for _, row in treatments_df.iterrows()}
        selected_treatment_id = st.selectbox(
            "اختر العلاج للتعديل",
            options=list(treatment_options.keys()),
            format_func=lambda x: treatment_options[x]
        )
        
        if selected_treatment_id:
            treatment = crud.get_treatment_by_id(selected_treatment_id)
            if not treatment.empty:
                with st.form(f"edit_treatment_form_{selected_treatment_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("اسم العلاج *", value=treatment['name'], max_chars=100)
                        base_price = st.number_input("السعر الأساسي (ج.م) *", min_value=0.0, value=float(treatment['base_price']), step=10.0)
                    with col2:
                        commission_rate = st.number_input("نسبة العمولة (%)", min_value=0.0, max_value=100.0, value=float(treatment['commission_rate']), step=0.1)
                        notes = st.text_area("ملاحظات", value=treatment['notes'] or "")
                    
                    submitted = st.form_submit_button("💾 حفظ التعديلات")
                    
                    if submitted:
                        if not name or not base_price:
                            show_error_message("يجب ملء الحقول المطلوبة (الاسم والسعر الأساسي)")
                        else:
                            crud.update_treatment(
                                treatment_id=selected_treatment_id,
                                name=name,
                                base_price=base_price,
                                commission_rate=commission_rate,
                                notes=notes
                            )
                            show_success_message("تم تعديل العلاج بنجاح")
                            st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في تعديل العلاج: {str(e)}")

def delete_treatment():
    """Delete a treatment"""
    st.subheader("🗑️ حذف علاج")
    
    try:
        treatments_df = crud.get_all_treatments()
        if treatments_df.empty:
            st.info("لا توجد علاجات لحذفها")
            return
        
        treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])}" for _, row in treatments_df.iterrows()}
        selected_treatment_id = st.selectbox(
            "اختر العلاج للحذف",
            options=list(treatment_options.keys()),
            format_func=lambda x: treatment_options[x]
        )
        
        if st.button("🗑️ حذف العلاج"):
            try:
                crud.delete_treatment(selected_treatment_id)
                show_success_message("تم حذف العلاج بنجاح")
                st.rerun()
            except Exception as e:
                show_error_message(f"خطأ في حذف العلاج: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل العلاجات: {str(e)}")

if __name__ == "__main__":
    show_treatments()
