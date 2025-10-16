import streamlit as st
from dashboard import show_dashboard
from appointments import show_appointments
from doctors import show_doctors
from patients import show_patients
from treatments import show_treatments
from inventory import show_inventory
from suppliers import show_suppliers
from expenses import show_expenses
from payments import show_payments

def main():
    st.set_page_config(page_title="نظام إدارة عيادة كورا", page_icon="🏥", layout="wide")
    
    menu = [
        "الرئيسية",
        "إدارة المواعيد",
        "إدارة الأطباء",
        "إدارة المرضى",
        "إدارة العلاجات",
        "إدارة المخزون",
        "إدارة الموردين",
        "إدارة المصروفات",
        "إدارة المدفوعات"
    ]
    choice = st.sidebar.selectbox("📋 القائمة الرئيسية", menu)
    
    if choice == "الرئيسية":
        show_dashboard()
    elif choice == "إدارة المواعيد":
        show_appointments()
    elif choice == "إدارة الأطباء":
        show_doctors()
    elif choice == "إدارة المرضى":
        show_patients()
    elif choice == "إدارة العلاجات":
        show_treatments()
    elif choice == "إدارة المخزون":
        show_inventory()
    elif choice == "إدارة الموردين":
        show_suppliers()
    elif choice == "إدارة المصروفات":
        show_expenses()
    elif choice == "إدارة المدفوعات":
        show_payments()

if __name__ == "__main__":
    main()
