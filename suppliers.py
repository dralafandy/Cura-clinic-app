import streamlit as st
from database.crud import crud

def render():
    """صفحة إدارة الموردين"""
    st.markdown("### 🏪 إدارة الموردين")
    
    tab1, tab2 = st.tabs(["📋 جميع الموردين", "➕ مورد جديد"])
    
    with tab1:
        render_all_suppliers()
    
    with tab2:
        render_add_supplier()

def render_all_suppliers():
    """عرض جميع الموردين"""
    suppliers = crud.get_all_suppliers()
    if not suppliers.empty:
        st.dataframe(
            suppliers[['id', 'name', 'contact_person', 'phone', 'email', 'payment_terms']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا يوجد موردين")

def render_add_supplier():
    """نموذج إضافة مورد جديد"""
    st.markdown("#### إضافة مورد جديد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("اسم الشركة*")
        contact_person = st.text_input("الشخص المسؤول")
        phone = st.text_input("رقم الهاتف")
    
    with col2:
        email = st.text_input("البريد الإلكتروني")
        address = st.text_area("العنوان")
        payment_terms = st.text_input("شروط الدفع", placeholder="مثال: آجل 30 يوم")
    
    if st.button("إضافة المورد", type="primary", use_container_width=True):
        if name:
            try:
                crud.create_supplier(name, contact_person, phone, email, address, payment_terms)
                st.success("✅ تم إضافة المورد بنجاح!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
        else:
            st.warning("الرجاء إدخال اسم الشركة")
