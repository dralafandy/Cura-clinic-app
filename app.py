import streamlit as st
from dashboard import show_dashboard
from appointments import show_appointments
from patients import show_patients
from doctors import show_doctors
from treatments import show_treatments
from inventory import show_inventory
from suppliers import show_suppliers
from expenses import show_expenses
from payments import show_payments

def main():
    st.set_page_config(
        page_title="نظام إدارة العيادة",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # الشريط الجانبي
    st.sidebar.title("🏥 نظام إدارة العيادة")
    
    # قائمة التنقل
    page = st.sidebar.radio(
        "اختر الصفحة",
        [
            "لوحة التحكم",
            "المواعيد",
            "المرضى",
            "الأطباء",
            "العلاجات والخدمات",
            "المخزون",
            "الموردين",
            "المصروفات",
            "المدفوعات"
        ]
    )
    
    # عرض الصفحة المختارة
    if page == "لوحة التحكم":
        show_dashboard()
    elif page == "المواعيد":
        show_appointments()
    elif page == "المرضى":
        show_patients()
    elif page == "الأطباء":
        show_doctors()
    elif page == "العلاجات والخدمات":
        show_treatments()
    elif page == "المخزون":
        show_inventory()
    elif page == "الموردين":
        show_suppliers()
    elif page == "المصروفات":
        show_expenses()
    elif page == "المدفوعات":
        show_payments()

if __name__ == "__main__":
    main()
