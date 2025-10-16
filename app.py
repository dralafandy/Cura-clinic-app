import streamlit as st
from datetime import date
# تغيير: الاستيراد الآن يتم من الحزمة 'database.crud'
from database.crud import CRUDOperations 
# ملاحظة: يجب أن تكون ملفات الصفحات في نفس المستوى مع app.py
import dashboard
import patients 
import appointments 
import doctors 
import treatments 
import payments 
import expenses 
import inventory 
import suppliers

# ====================================================================
# تهيئة التطبيق وإنشاء مثيل قاعدة البيانات
# ====================================================================

# إنشاء مثيل (Instance) لكلاس CRUDOperations
# هذا هو الكائن الذي سيتم تمريره لجميع الصفحات
crud = CRUDOperations()

# ... (بقية إعدادات الصفحة والـ CSS كما هي) ...

st.set_page_config(
    page_title="نظام إدارة العيادات (CMS)",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* تطبيق RTL على جميع النصوص باستثناء أكواد البرمجة */
    body { direction: rtl; text-align: right; }
    .st-emotion-cache-1g8o83 { direction: rtl; text-align: right; }
    .st-emotion-cache-1ky9p07 { direction: rtl; }
    .st-emotion-cache-vdn9h4, .st-emotion-cache-1cpxdcf { text-align: right !important; }
    .st-emotion-cache-16niy5c { direction: rtl; text-align: right; }
    .st-emotion-cache-pkj78g { direction: rtl; text-align: right; }
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
    
    daily_appointments = crud.get_daily_appointments_count()
    financial_summary = crud.get_financial_summary(start_date=today, end_date=today)
    
    st.info(f"📅 **مواعيد اليوم:** {daily_appointments} موعد")
    st.success(f"💰 **إيرادات اليوم:** {financial_summary['total_revenue']:.2f} ج.م")


# ====================================================================
# منطق التوجيه (Routing Logic)
# ====================================================================

# تشغيل وظيفة الصفحة المختارة
if pages[selection] is not None:
    module = pages[selection]
    
    # بناءً على أسماء الدوال التي تم تحديدها سابقاً (show_dashboard، show_patients، إلخ)
    function_map = {
        "الرئيسية (لوحة التحكم)": "show_dashboard",
        "إدارة المواعيد": "show_appointments",
        "إدارة المرضى": "show_patients",
        "المدفوعات والإيرادات": "show_payments",
        "المصروفات والميزانية": "show_expenses",
        "الخدمات والعلاجات": "show_treatments",
        "الأطباء والموظفين": "show_doctors",
        "المخزون والمستلزمات": "show_inventory",
        "الموردون": "show_suppliers",
    }
    
    func_name = function_map.get(selection)
    if func_name and hasattr(module, func_name):
        # استدعاء الدالة الصحيحة وتمرير مثيل الـ crud
        getattr(module, func_name)(crud)
    else:
        st.error(f"خطأ: لم يتم العثور على الدالة {func_name} في ملف {module.__name__}.py")
        
else:
    st.info("اختر وحدة عمل من القائمة الجانبية.")
