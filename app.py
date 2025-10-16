import streamlit as st
from dashboard import show_dashboard
from patients import show_patients
from appointments import show_appointments
from treatments import show_treatments
from doctors import show_doctors
from payments import show_payments
from expenses import show_expenses
from inventory import show_inventory
from suppliers import show_suppliers

# إعداد الصفحة الرئيسية
st.set_page_config(
    page_title="نظام إدارة العيادة الطبية",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🏥 نظام إدارة العيادة الطبية")
    st.markdown("---")
    
    # شريط جانبي للتنقل بين الصفحات
    st.sidebar.title("📋 القائمة الرئيسية")
    st.sidebar.markdown("اختر قسماً للإدارة:")
    
    page = st.sidebar.radio(
        "الانتقال إلى:",
        [
            "لوحة التحكم الرئيسية",
            "إدارة المرضى",
            "إدارة المواعيد",
            "إدارة العلاجات",
            "إدارة الأطباء",
            "إدارة المدفوعات",
            "إدارة المصروفات",
            "إدارة المخزون",
            "إدارة الموردين"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("تاريخ اليوم: 16 أكتوبر 2025")
    
    # التنقل بين الصفحات بناءً على الاختيار
    if page == "لوحة التحكم الرئيسية":
        show_dashboard()
    elif page == "إدارة المرضى":
        show_patients()
    elif page == "إدارة المواعيد":
        show_appointments()
    elif page == "إدارة العلاجات":
        show_treatments()
    elif page == "إدارة الأطباء":
        show_doctors()
    elif page == "إدارة المدفوعات":
        show_payments()
    elif page == "إدارة المصروفات":
        show_expenses()
    elif page == "إدارة المخزون":
        show_inventory()
    elif page == "إدارة الموردين":
        show_suppliers()

if __name__ == "__main__":
    main()
