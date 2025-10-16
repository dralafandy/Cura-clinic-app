import streamlit as stimport streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database.crud import crud
from utils.helpers import show_success_message, show_error_message, format_currency

# استيراد الصفحات مباشرة (بدون مجلد pages)
from appointments import show_appointments
from financial_reports import show_financial_dashboard
from accounting import show_accounting
from doctors import show_doctors_management
from patients import show_patients_management
from inventory import show_inventory_management

def main():
    # إعداد الصفحة
    st.set_page_config(
        page_title="نظام إدارة العيادة",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # تخصيص التصميم
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #2E86AB;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # الرأس الرئيسي
    st.markdown('<h1 class="main-header">🏥 نظام إدارة العيادة</h1>', unsafe_allow_html=True)
    
    # القائمة الجانبية
    with st.sidebar:
        st.markdown("## 🌟 القائمة الرئيسية")
        
        # قسم الإدارة الأساسية
        st.markdown("### 📋 الإدارة الأساسية")
        menu_option = st.radio(
            "اختر القسم:",
            [
                "لوحة التحكم",
                "إدارة الأطباء", 
                "إدارة المرضى",
                "إدارة المواعيد",
                "المحاسبة اليومية",
                "التقارير المالية",
                "إدارة المخزون"
            ]
        )
        
        st.markdown("---")
        
        # معلومات سريعة
        st.markdown("### 📈 إحصائيات سريعة")
        try:
            # عدد المواعيد اليوم
            today_appointments = crud.get_daily_appointments_count()
            st.metric("📅 مواعيد اليوم", today_appointments)
            
            # إيرادات الشهر
            month_start = date.today().replace(day=1)
            financial_summary = crud.get_financial_summary(month_start, date.today())
            st.metric("💰 إيرادات الشهر", f"{financial_summary['total_revenue']:,.0f} ج.م")
            
        except Exception as e:
            st.info("جاري تحميل الإحصائيات...")
        
        st.markdown("---")
        st.markdown("**الإصدار 1.0**")
        st.markdown("© 2024 نظام إدارة العيادة")

    # عرض المحتوى حسب الاختيار
    try:
        if menu_option == "لوحة التحكم":
            show_dashboard()
        elif menu_option == "إدارة الأطباء":
            show_doctors_management()
        elif menu_option == "إدارة المرضى":
            show_patients_management()
        elif menu_option == "إدارة المواعيد":
            show_appointments()
        elif menu_option == "المحاسبة اليومية":
            show_accounting()
        elif menu_option == "التقارير المالية":
            show_financial_dashboard()
        elif menu_option == "إدارة المخزون":
            show_inventory_management()
            
    except Exception as e:
        show_error_message(f"حدث خطأ: {str(e)}")

def show_dashboard():
    """لوحة التحكم الرئيسية"""
    st.subheader("📊 لوحة التحكم الرئيسية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # إحصائيات سريعة
        today = date.today()
        month_start = today.replace(day=1)
        
        with col1:
            today_appointments = crud.get_daily_appointments_count()
            st.metric("📅 مواعيد اليوم", today_appointments)
        
        with col2:
            month_financial = crud.get_financial_summary(month_start, today)
            st.metric("💰 إيرادات الشهر", f"{month_financial['total_revenue']:,.0f} ج.م")
        
        with col3:
            doctors_count = len(crud.get_all_doctors())
            st.metric("👨‍⚕️ عدد الأطباء", doctors_count)
        
        with col4:
            patients_count = len(crud.get_all_patients())
            st.metric("👥 عدد المرضى", patients_count)
        
        # المزيد من الإحصائيات
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            month_expenses = crud.get_financial_summary(month_start, today)
            st.metric("💸 مصروفات الشهر", f"{month_expenses['total_expenses']:,.0f} ج.م")
        
        with col6:
            net_profit = month_financial['net_profit']
            st.metric("📊 صافي الربح", f"{net_profit:,.0f} ج.م")
        
        with col7:
            low_stock = crud.get_low_stock_items()
            st.metric("⚠️ عناصر قليلة", len(low_stock))
        
        with col8:
            total_appointments = month_financial['total_appointments']
            st.metric("🎯 إجمالي الجلسات", total_appointments)
        
        # التنبيهات الهامة
        st.markdown("---")
        st.subheader("🔔 التنبيهات الهامة")
        
        col9, col10 = st.columns(2)
        
        with col9:
            # العناصر قليلة المخزون
            low_stock_items = crud.get_low_stock_items()
            if not low_stock_items.empty:
                st.error("**⚠️ عناصر تحت مستوى المخزون الأدنى:**")
                for _, item in low_stock_items.head(3).iterrows():
                    st.write(f"- {item['item_name']} ({item['quantity']} متبقي)")
        
        with col10:
            # العناصر المنتهية الصلاحية
            expired_items = crud.get_expired_items()
            if not expired_items.empty:
                st.error("**❌ عناصر منتهية الصلاحية:**")
                for _, item in expired_items.head(3).iterrows():
                    st.write(f"- {item['item_name']} (انتهى في {item['expiry_date']})")
        
        # تقارير سريعة
        st.markdown("---")
        st.subheader("📈 تقارير سريعة")
        
        col11, col12 = st.columns(2)
        
        with col11:
            st.write("**أفضل الأطباء أداءً (هذا الشهر)**")
            doctors_performance = crud.get_doctor_performance_report(month_start, today)
            if not doctors_performance.empty:
                for _, doctor in doctors_performance.head(3).iterrows():
                    st.write(f"- {doctor['doctor_name']}: {format_currency(doctor['total_revenue'])}")
        
        with col12:
            st.write("**أعلى العملاء إنفاقاً (هذا الشهر)**")
            patients_report = crud.get_patient_financial_report(month_start, today)
            if not patients_report.empty:
                for _, patient in patients_report.head(3).iterrows():
                    st.write(f"- {patient['patient_name']}: {format_currency(patient['total_spent'])}")
            
    except Exception as e:
        show_error_message(f"خطأ في تحميل لوحة التحكم: {str(e)}")

if __name__ == "__main__":
    main()
from database.crud import crud
from utils.helpers import show_success_message, show_error_message

# استيراد الصفحات
from pages.appointments import show_appointments
from pages.financial_reports import show_financial_dashboard
from pages.accounting import show_accounting
from pages.doctors import show_doctors_management
from pages.patients import show_patients_management
from pages.inventory import show_inventory_management

def main():
    # إعداد الصفحة
    st.set_page_config(
        page_title="نظام إدارة العيادة",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # تخصيص التصميم
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #2E86AB;
            text-align: center;
            margin-bottom: 2rem;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # الرأس الرئيسي
    st.markdown('<h1 class="main-header">🏥 نظام إدارة العيادة</h1>', unsafe_allow_html=True)
    
    # القائمة الجانبية
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2966/2966321.png", width=100)
        st.markdown("## 🌟 القائمة الرئيسية")
        
        # قسم الإدارة الأساسية
        st.markdown("### 📋 الإدارة الأساسية")
        menu_option = st.radio(
            "اختر القسم:",
            [
                "لوحة التحكم",
                "إدارة الأطباء", 
                "إدارة المرضى",
                "إدارة المواعيد",
                "المحاسبة اليومية",
                "التقارير المالية",
                "إدارة المخزون"
            ]
        )
        
        st.markdown("---")
        
        # قسم التقارير والإحصائيات
        st.markdown("### 📊 التقارير والإحصائيات")
        report_option = st.radio(
            "التقارير المتقدمة:",
            [
                "نظرة عامة",
                "تقارير الأطباء", 
                "تقارير المرضى",
                "المخزون والمصروفات",
                "تقارير مفصلة"
            ]
        )
        
        st.markdown("---")
        
        # معلومات سريعة
        st.markdown("### 📈 إحصائيات سريعة")
        try:
            # عدد المواعيد اليوم
            today_appointments = crud.get_daily_appointments_count()
            st.metric("مواعيد اليوم", today_appointments)
            
            # إيرادات الشهر
            month_start = date.today().replace(day=1)
            financial_summary = crud.get_financial_summary(month_start, date.today())
            st.metric("إيرادات الشهر", f"{financial_summary['total_revenue']:,.0f} ج.م")
            
        except Exception as e:
            st.info("جاري تحميل الإحصائيات...")
        
        st.markdown("---")
        st.markdown("**الإصدار 1.0**  ")
        st.markline("© 2024 نظام إدارة العيادة")

    # عرض المحتوى حسب الاختيار
    try:
        if menu_option == "لوحة التحكم":
            show_dashboard()
        elif menu_option == "إدارة الأطباء":
            show_doctors_management()
        elif menu_option == "إدارة المرضى":
            show_patients_management()
        elif menu_option == "إدارة المواعيد":
            show_appointments()
        elif menu_option == "المحاسبة اليومية":
            show_accounting()
        elif menu_option == "التقارير المالية":
            show_financial_dashboard()
        elif menu_option == "إدارة المخزون":
            show_inventory_management()
            
    except Exception as e:
        show_error_message(f"حدث خطأ: {str(e)}")

def show_dashboard():
    """لوحة التحكم الرئيسية"""
    st.subheader("📊 لوحة التحكم الرئيسية")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # إحصائيات سريعة
        today = date.today()
        month_start = today.replace(day=1)
        
        with col1:
            today_appointments = crud.get_daily_appointments_count()
            st.metric("📅 مواعيد اليوم", today_appointments)
        
        with col2:
            month_financial = crud.get_financial_summary(month_start, today)
            st.metric("💰 إيرادات الشهر", f"{month_financial['total_revenue']:,.0f} ج.م")
        
        with col3:
            doctors_count = len(crud.get_all_doctors())
            st.metric("👨‍⚕️ عدد الأطباء", doctors_count)
        
        with col4:
            patients_count = len(crud.get_all_patients())
            st.metric("👥 عدد المرضى", patients_count)
        
        # المزيد من الإحصائيات
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            month_expenses = crud.get_financial_summary(month_start, today)
            st.metric("💸 مصروفات الشهر", f"{month_expenses['total_expenses']:,.0f} ج.م")
        
        with col6:
            net_profit = month_financial['net_profit']
            st.metric("📊 صافي الربح", f"{net_profit:,.0f} ج.م")
        
        with col7:
            low_stock = crud.get_low_stock_items()
            st.metric("⚠️ عناصر قليلة", len(low_stock))
        
        with col8:
            total_appointments = month_financial['total_appointments']
            st.metric("🎯 إجمالي الجلسات", total_appointments)
        
        # مخططات سريعة
        st.markdown("---")
        col9, col10 = st.columns(2)
        
        with col9:
            st.subheader("📈 الإيرادات vs المصروفات")
            # هنا يمكن إضافة مخطط بسيط
            
        with col10:
            st.subheader("👨‍⚕️ توزيع الجلسات")
            # هنا يمكن إضافة مخطط آخر
            
    except Exception as e:
        show_error_message(f"خطأ في تحميل لوحة التحكم: {str(e)}")

if __name__ == "__main__":
    main()
