from doctors import show_doctors
from patients import show_patients
from appointments import show_appointments
from treatments import show_treatments
from payments import show_payments
from inventory import show_inventory
from suppliers import show_suppliers
from expenses import show_expenses
from dashboard import show_dashboard
def main():
    # تهيئة تكوين الصفحة
    st.set_page_config(page_title="نظام إدارة العيادة", layout="wide")
    
    # عنوان الشريط الجانبي
    st.sidebar.title("📋 قائمة الخيارات")
    
    # تعريف قاموس الصفحات
    pages = {
        "لوحة التحكم": show_dashboard,
        "إدارة الأطباء": show_doctors,
        "إدارة المرضى": show_patients,
        "إدارة المواعيد": show_appointments,
        "إدارة العلاجات": show_treatments,
        "إدارة المدفوعات": show_payments,
        "إدارة المخزون": show_inventory,
        "إدارة الموردين": show_suppliers,
        "إدارة المصروفات": show_expenses
    }
    
    # إنشاء قائمة اختيار في الشريط الجانبي باستخدام radio
    selection = st.sidebar.radio("اختر الوحدة", list(pages.keys()))
    
    # عرض الصفحة المختارة
    pages[selection]()  # تنفيذ الدالة المختارة
if __name__ == "__main__":
