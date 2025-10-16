import streamlit as st
import sys
import os

# إضافة المجلد الحالي إلى مسار Python (حل لـ Streamlit Cloud)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    # استخدام session_state للتنقل الديناميكي
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    
    st.title("🏥 نظام إدارة العيادة الطبية")
    st.markdown("---")
    
    # الصفحة الرئيسية الديناميكية
    if st.session_state.current_page == "home":
        show_home_page()
    elif st.session_state.current_page == "dashboard":
        show_dashboard()
    elif st.session_state.current_page == "patients":
        show_patients()
    elif st.session_state.current_page == "appointments":
        show_appointments()
    elif st.session_state.current_page == "treatments":
        show_treatments()
    elif st.session_state.current_page == "doctors":
        show_doctors()
    elif st.session_state.current_page == "payments":
        show_payments()
    elif st.session_state.current_page == "expenses":
        show_expenses()
    elif st.session_state.current_page == "inventory":
        show_inventory()
    elif st.session_state.current_page == "suppliers":
        show_suppliers()
    
    # شريط جانبي للعودة إلى الصفحة الرئيسية
    with st.sidebar:
        st.title("📋 القائمة الرئيسية")
        if st.button("🏠 الصفحة الرئيسية"):
            st.session_state.current_page = "home"
            st.rerun()
        st.markdown("---")
        st.info("تاريخ اليوم: 16 أكتوبر 2025")

def show_home_page():
    """عرض الصفحة الرئيسية الديناميكية مع روابط (أزرار) للصفحات"""
    st.header("مرحباً بك في نظام إدارة العيادة")
    st.markdown("اختر قسماً من الأقسام أدناه للبدء في الإدارة:")
    
    # تصميم ديناميكي باستخدام أعمدة (3 أعمدة في كل صف)
    col1, col2, col3 = st.columns(3)
    
    # الصف الأول: لوحة التحكم، المرضى، المواعيد
    with col1:
        if st.button("📊 لوحة التحكم الرئيسية", key="dashboard_btn", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        st.markdown("**عرض الإحصائيات والتقارير السريعة**")
    
    with col2:
        if st.button("👥 إدارة المرضى", key="patients_btn", use_container_width=True):
            st.session_state.current_page = "patients"
            st.rerun()
        st.markdown("**إضافة، تحرير، وتقارير المرضى**")
    
    with col3:
        if st.button("📅 إدارة المواعيد", key="appointments_btn", use_container_width=True):
            st.session_state.current_page = "appointments"
            st.rerun()
        st.markdown("**حجز وإدارة المواعيد والتقويم**")
    
    # الصف الثاني: العلاجات، الأطباء، المدفوعات
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("💊 إدارة العلاجات", key="treatments_btn", use_container_width=True):
            st.session_state.current_page = "treatments"
            st.rerun()
        st.markdown("**إدارة الخدمات والأسعار**")
    
    with col5:
        if st.button("👨‍⚕️ إدارة الأطباء", key="doctors_btn", use_container_width=True):
            st.session_state.current_page = "doctors"
            st.rerun()
        st.markdown("**بيانات الأطباء وأدائهم**")
    
    with col6:
        if st.button("💳 إدارة المدفوعات", key="payments_btn", use_container_width=True):
            st.session_state.current_page = "payments"
            st.rerun()
        st.markdown("**تسجيل وتقارير المدفوعات**")
    
    # الصف الثالث: المصروفات، المخزون، الموردين
    col7, col8, col9 = st.columns(3)
    
    with col7:
        if st.button("💸 إدارة المصروفات", key="expenses_btn", use_container_width=True):
            st.session_state.current_page = "expenses"
            st.rerun()
        st.markdown("**تتبع المصروفات والميزانية**")
    
    with col8:
        if st.button("📦 إدارة المخزون", key="inventory_btn", use_container_width=True):
            st.session_state.current_page = "inventory"
            st.rerun()
        st.markdown("**إدارة المخزون والتنبيهات**")
    
    with col9:
        if st.button("🏢 إدارة الموردين", key="suppliers_btn", use_container_width=True):
            st.session_state.current_page = "suppliers"
            st.rerun()
        st.markdown("**إدارة الموردين وطلبات الشراء**")
    
    # قسم مميزات البرنامج
    st.divider()
    st.header("✨ مميزات البرنامج")
    st.markdown("**نظام إدارة العيادة الطبية** مصمم لتسهيل عمليات العيادة اليومية مع واجهة عربية سهلة الاستخدام. إليك أبرز المميزات:")
    
    features = [
        "📊 **لوحة تحكم ديناميكية**: إحصائيات فورية، رسوم بيانية تفاعلية باستخدام Plotly، وتنبيهات تلقائية (مثل المخزون المنخفض).",
        "👥 **إدارة المرضى الشاملة**: تسجيل بيانات المرضى، حساب العمر، تاريخ مرضي، وبحث سريع مع تصدير إلى Excel.",
        "📅 **إدارة المواعيد المتقدمة**: حجز سهل، تقويم شهري، فلاتر بالتاريخ والحالة، وحساب التكاليف التلقائي.",
        "💊 **إدارة العلاجات والأسعار**: إضافة خدمات، تحديث أسعار جماعي (بنسبة مئوية أو CSV)، وتحليل الشعبية.",
        "👨‍⚕️ **إدارة الأطباء وأدائهم**: تسجيل الرواتب والعمولات، تقارير أداء، وتصدير كشوف الرواتب.",
        "💳 **إدارة المدفوعات والمصروفات**: تسجيل الدفعات المرتبطة بالمواعيد، تقارير مالية، ميزانية شهرية، ومقارنة الفعلي بالميزانية.",
        "📦 **إدارة المخزون الذكية**: تتبع الكميات، تنبيهات للانخفاض، فلاتر بالفئة والانتهاء، واستيراد/تصدير CSV.",
        "🏢 **إدارة الموردين**: تسجيل الموردين، طلبات شراء مقترحة، وتحليل شروط الدفع.",
        "💡 **مميزات عامة**: دعم قاعدة بيانات SQLite مع بيانات تجريبية، فلاتر متقدمة، رسائل نجاح/خطأ بالعربية، وتصميم متجاوب."
    ]
    
    for feature in features:
        st.markdown(feature)
    
    # إضافة معلومات إضافية في الأسفل
    st.divider()
    st.info("💡 **نصيحة:** استخدم الشريط الجانبي للعودة إلى الصفحة الرئيسية في أي وقت.")

if __name__ == "__main__":
    main()
