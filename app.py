import streamlit as st
from datetime import date
from crud import crud # استيراد مثيل عمليات قاعدة البيانات
from pages import (
    dashboard, 
    patients, 
    appointments, 
    doctors, 
    treatments, 
    payments, 
    expenses, 
    inventory, 
    suppliers
)

# ====================================================================
# تهيئة التطبيق والإعدادات العامة
# ====================================================================

# تعيين إعدادات الصفحة
st.set_page_config(
    page_title="نظام إدارة العيادات (CMS)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ترويسة التطبيق واللغة
# نستخدم CSS مخصص لتعيين اتجاه النص من اليمين لليسار (RTL) لدعم اللغة العربية
st.markdown("""
<style>
    /* تطبيق RTL على جميع النصوص باستثناء أكواد البرمجة */
    body {
        direction: rtl;
        text-align: right;
    }
    .st-emotion-cache-1g8o83 {
        direction: rtl;
        text-align: right;
    }
    /* جعل العنوان في الوسط والمحتوى الرئيسي يبدأ من اليمين */
    .st-emotion-cache-1ky9p07 {
        direction: rtl;
    }
    /* تعديل اتجاه الأزرار والمدخلات */
    .st-emotion-cache-vdn9h4, .st-emotion-cache-1cpxdcf {
        text-align: right !important;
    }
    /* تعديل اتجاه الشريط الجانبي */
    .st-emotion-cache-16niy5c {
        direction: rtl;
        text-align: right;
    }
    .st-emotion-cache-pkj78g {
        direction: rtl;
        text-align: right;
    }
    /* إخفاء شعار Streamlit الافتراضي */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


# ====================================================================
# الشريط الجانبي والتنقل
# ====================================================================

# قائمة الصفحات في الشريط الجانبي
pages = {
    "الرئيسية (لوحة التحكم)": dashboard,
    "إدارة المواعيد": appointments,
    "إدارة المرضى": patients,
    "------------------------": None,
    "المدفوعات والإيرادات": payments,
    "المصروفات والميزانية": expenses,
    "------------------------": None,
    "الخدمات والعلاجات": treatments,
    "الأطباء والموظفين": doctors,
    "------------------------": None,
    "المخزون والمستلزمات": inventory,
    "الموردون": suppliers,
}

# اختيار الصفحة من الشريط الجانبي
st.sidebar.title("قائمة النظام")
selection = st.sidebar.radio("اختر الوحدة:", list(pages.keys()))
st.sidebar.markdown("---")

# عرض ملخص سريع في الشريط الجانبي
with st.sidebar.expander("ملخص اليوم", expanded=True):
    today = date.today().isoformat()
    st.write(f"**تاريخ اليوم:** {today}")
    
    # استخدام دوال الـ CRUD للحصول على إحصائيات فورية
    daily_appointments = crud.get_daily_appointments_count()
    financial_summary = crud.get_financial_summary(start_date=today, end_date=today)
    
    st.info(f"📅 **مواعيد اليوم:** {daily_appointments} موعد")
    st.success(f"💰 **إيرادات اليوم:** {financial_summary['total_revenue']:.2f}")


# ====================================================================
# منطق التوجيه (Routing Logic)
# ====================================================================

# تشغيل وظيفة الصفحة المختارة
if pages[selection] is not None:
    # نقوم بتمرير مثيل الـ CRUD لكل صفحة للوصول لقاعدة البيانات
    pages[selection].main(crud)
else:
    # لمعالجة الفواصل في القائمة
    st.info("اختر وحدة عمل من القائمة الجانبية.")

# ====================================================================
