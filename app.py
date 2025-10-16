import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from database.crud import crud
from database.models import db

# ========================
# صفحة التهيئة الأساسية
# ========================
st.set_page_config(
    page_title="نظام إدارة العيادة - Cura Clinic",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# تهيئة قاعدة البيانات
# ========================
@st.cache_resource
def init_database():
    """تهيئة قاعدة البيانات"""
    db.initialize()
    return True

init_database()

# ========================
# الأنماط المخصصة (CSS)
# ========================
def load_custom_css():
    st.markdown("""
    <style>
        /* تحسين الخط العربي */
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
        }
        
        /* البطاقات */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            margin: 10px 0;
        }
        
        .metric-card.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .metric-card.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .metric-card.info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        /* الشريط الجانبي */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        }
        
        [data-testid="stSidebar"] .css-1d391kg, [data-testid="stSidebar"] .css-1v0mbdj {
            color: white;
        }
        
        /* الأزرار */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* الجداول */
        .dataframe {
            border-radius: 10px;
            overflow: hidden;
        }
        
        /* العنوان الرئيسي */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        /* بطاقة إحصائية */
        .stat-box {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-right: 4px solid #667eea;
        }
        
        /* دعم RTL للعربية */
        .rtl {
            direction: rtl;
            text-align: right;
        }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

# ========================
# الشريط الجانبي - التنقل
# ========================
def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <h1 style='color: white; margin: 0;'>🏥 Cura Clinic</h1>
                <p style='color: #bdc3c7; margin: 5px 0;'>نظام إدارة العيادة المتكامل</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # القائمة الرئيسية
        menu_items = {
            "🏠 الرئيسية": "dashboard",
            "📅 المواعيد": "appointments",
            "👥 المرضى": "patients",
            "👨‍⚕️ الأطباء": "doctors",
            "💉 العلاجات": "treatments",
            "💰 المدفوعات": "payments",
            "📦 المخزون": "inventory",
            "🏪 الموردين": "suppliers",
            "💸 المصروفات": "expenses",
            "📊 التقارير": "reports"
        }
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
        
        st.markdown("### 📋 القائمة الرئيسية")
        
        for label, page_id in menu_items.items():
            if st.button(label, key=f"nav_{page_id}", use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # معلومات سريعة
        st.markdown("### ℹ️ معلومات سريعة")
        today = date.today()
        st.info(f"📅 {today.strftime('%Y-%m-%d')}")
        
        # عدد المواعيد اليوم
        daily_appointments = crud.get_daily_appointments_count()
        st.success(f"📌 المواعيد اليوم: {daily_appointments}")
        
        # عناصر قليلة المخزون
        low_stock = crud.get_low_stock_items()
        if not low_stock.empty:
            st.warning(f"⚠️ مخزون منخفض: {len(low_stock)} عنصر")

render_sidebar()

# ========================
# الصفحة الرئيسية - لوحة المعلومات
# ========================
def render_dashboard():
    st.markdown("""
        <div class='main-header'>
            <h1>🏥 لوحة معلومات العيادة</h1>
            <p>مرحباً بك في نظام إدارة العيادة المتكامل</p>
        </div>
    """, unsafe_allow_html=True)
    
    # البطاقات الإحصائية
    col1, col2, col3, col4 = st.columns(4)
    
    # إجمالي المرضى
    patients_df = crud.get_all_patients()
    total_patients = len(patients_df)
    
    # إجمالي الأطباء
    doctors_df = crud.get_all_doctors()
    total_doctors = len(doctors_df)
    
    # المواعيد اليوم
    today = date.today()
    today_appointments = crud.get_appointments_by_date(today.isoformat())
    
    # الملخص المالي
    financial_summary = crud.get_financial_summary()
    
    with col1:
        st.markdown(f"""
            <div class='metric-card success'>
                <div class='metric-label'>👥 إجمالي المرضى</div>
                <div class='metric-value'>{total_patients}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card info'>
                <div class='metric-label'>👨‍⚕️ عدد الأطباء</div>
                <div class='metric-value'>{total_doctors}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card warning'>
                <div class='metric-label'>📅 مواعيد اليوم</div>
                <div class='metric-value'>{len(today_appointments)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>💰 صافي الربح</div>
                <div class='metric-value'>{financial_summary['net_profit']:,.0f} ج.م</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # الصف الثاني - رسوم بيانية
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 الإيرادات والمصروفات")
        
        financial_data = pd.DataFrame({
            'الفئة': ['الإيرادات', 'المصروفات', 'صافي الربح'],
            'المبلغ': [
                financial_summary['total_revenue'],
                financial_summary['total_expenses'],
                financial_summary['net_profit']
            ]
        })
        
        fig = px.bar(
            financial_data,
            x='الفئة',
            y='المبلغ',
            color='الفئة',
            color_discrete_map={
                'الإيرادات': '#38ef7d',
                'المصروفات': '#f5576c',
                'صافي الربح': '#4facfe'
            }
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 حالة المواعيد")
        
        all_appointments = crud.get_all_appointments()
        if not all_appointments.empty:
            status_counts = all_appointments['status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد مواعيد لعرضها")
    
    # مواعيد اليوم
    st.markdown("### 📅 مواعيد اليوم")
    if not today_appointments.empty:
        st.dataframe(
            today_appointments[['patient_name', 'doctor_name', 'treatment_name', 'appointment_time', 'status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا توجد مواعيد اليوم")
    
    # تنبيهات المخزون
    low_stock = crud.get_low_stock_items()
    if not low_stock.empty:
        st.markdown("### ⚠️ تنبيهات المخزون")
        st.warning(f"يوجد {len(low_stock)} عنصر بمخزون منخفض")
        st.dataframe(
            low_stock[['item_name', 'quantity', 'min_stock_level']],
            use_container_width=True,
            hide_index=True
        )

# ========================
# صفحة المواعيد
# ========================
def render_appointments():
    st.markdown("### 📅 إدارة المواعيد")
    
    tab1, tab2, tab3 = st.tabs(["📋 جميع المواعيد", "➕ موعد جديد", "🔍 بحث"])
    
    with tab1:
        appointments = crud.get_all_appointments()
        if not appointments.empty:
            # فلترة حسب الحالة
            status_filter = st.selectbox("فلترة حسب الحالة", ["الكل"] + appointments['status'].unique().tolist())
            
            if status_filter != "الكل":
                appointments = appointments[appointments['status'] == status_filter]
            
            st.dataframe(appointments, use_container_width=True, hide_index=True)
            
            # تحديث حالة الموعد
            st.markdown("#### تحديث حالة موعد")
            col1, col2, col3 = st.columns(3)
            with col1:
                appointment_id = st.number_input("رقم الموعد", min_value=1, step=1)
            with col2:
                new_status = st.selectbox("الحالة الجديدة", ["مجدول", "مؤكد", "مكتمل", "ملغي"])
            with col3:
                if st.button("تحديث"):
                    crud.update_appointment_status(appointment_id, new_status)
                    st.success("تم تحديث الحالة بنجاح!")
                    st.rerun()
        else:
            st.info("لا توجد مواعيد")
    
    with tab2:
        st.markdown("#### إضافة موعد جديد")
        
        patients = crud.get_all_patients()
        doctors = crud.get_all_doctors()
        treatments = crud.get_all_treatments()
        
        if patients.empty or doctors.empty:
            st.warning("يجب إضافة مرضى وأطباء أولاً")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                patient_id = st.selectbox(
                    "المريض",
                    patients['id'].tolist(),
                    format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
                )
                
                treatment_id = st.selectbox(
                    "العلاج",
                    treatments['id'].tolist(),
                    format_func=lambda x: treatments[treatments['id'] == x]['name'].iloc[0]
                ) if not treatments.empty else None
                
                appointment_date = st.date_input("تاريخ الموعد", min_value=date.today())
            
            with col2:
                doctor_id = st.selectbox(
                    "الطبيب",
                    doctors['id'].tolist(),
                    format_func=lambda x: doctors[doctors['id'] == x]['name'].iloc[0]
                )
                
                appointment_time = st.time_input("وقت الموعد")
                
                if treatment_id:
                    total_cost = treatments[treatments['id'] == treatment_id]['base_price'].iloc[0]
                    st.number_input("التكلفة الإجمالية", value=float(total_cost), key="total_cost")
            
            notes = st.text_area("ملاحظات")
            
            if st.button("حجز الموعد", type="primary", use_container_width=True):
                try:
                    crud.create_appointment(
                        patient_id,
                        doctor_id,
                        treatment_id,
                        appointment_date.isoformat(),
                        appointment_time.strftime("%H:%M"),
                        notes,
                        st.session_state.get('total_cost', 0)
                    )
                    st.success("✅ تم حجز الموعد بنجاح!")
                    st.balloons()
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
    
    with tab3:
        search_date = st.date_input("البحث بالتاريخ")
        if st.button("بحث"):
            results = crud.get_appointments_by_date(search_date.isoformat())
            if not results.empty:
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد مواعيد في هذا التاريخ")

# ========================
# صفحة المرضى
# ========================
def render_patients():
    st.markdown("### 👥 إدارة المرضى")
    
    tab1, tab2 = st.tabs(["📋 جميع المرضى", "➕ مريض جديد"])
    
    with tab1:
        patients = crud.get_all_patients()
        if not patients.empty:
            # بحث
            search = st.text_input("🔍 بحث عن مريض", placeholder="اسم، هاتف، بريد إلكتروني...")
            if search:
                patients = patients[
                    patients['name'].str.contains(search, case=False, na=False) |
                    patients['phone'].str.contains(search, case=False, na=False) |
                    patients['email'].str.contains(search, case=False, na=False)
                ]
            
            st.dataframe(patients, use_container_width=True, hide_index=True)
            st.info(f"إجمالي المرضى: {len(patients)}")
        else:
            st.info("لا يوجد مرضى")
    
    with tab2:
        st.markdown("#### إضافة مريض جديد")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("الاسم الكامل*")
            phone = st.text_input("رقم الهاتف*")
            email = st.text_input("البريد الإلكتروني")
            date_of_birth = st.date_input("تاريخ الميلاد", max_value=date.today())
        
        with col2:
            address = st.text_area("العنوان")
            gender = st.selectbox("النوع", ["ذكر", "أنثى"])
            emergency_contact = st.text_input("جهة الاتصال للطوارئ")
        
        medical_history = st.text_area("التاريخ الطبي")
        
        if st.button("إضافة المريض", type="primary", use_container_width=True):
            if name and phone:
                try:
                    crud.create_patient(
                        name, phone, email, address,
                        date_of_birth.isoformat(), gender,
                        medical_history, emergency_contact
                    )
                    st.success("✅ تم إضافة المريض بنجاح!")
                    st.balloons()
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
            else:
                st.warning("الرجاء ملء الحقول المطلوبة")

# ========================
# صفحة الأطباء
# ========================
def render_doctors():
    st.markdown("### 👨‍⚕️ إدارة الأطباء")
    
    tab1, tab2 = st.tabs(["📋 جميع الأطباء", "➕ طبيب جديد"])
    
    with tab1:
        doctors = crud.get_all_doctors()
        if not doctors.empty:
            st.dataframe(doctors, use_container_width=True, hide_index=True)
        else:
            st.info("لا يوجد أطباء")
    
    with tab2:
        st.markdown("#### إضافة طبيب جديد")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("الاسم الكامل*")
            specialization = st.text_input("التخصص*")
            phone = st.text_input("رقم الهاتف")
            email = st.text_input("البريد الإلكتروني")
        
        with col2:
            address = st.text_area("العنوان")
            hire_date = st.date_input("تاريخ التعيين", value=date.today())
            salary = st.number_input("الراتب (ج.م)", min_value=0.0, step=100.0)
            commission_rate = st.number_input("نسبة العمولة (%)", min_value=0.0, max_value=100.0, value=0.0)
        
        if st.button("إضافة الطبيب", type="primary", use_container_width=True):
            if name and specialization:
                try:
                    crud.create_doctor(
                        name, specialization, phone, email, address,
                        hire_date.isoformat(), salary, commission_rate
                    )
                    st.success("✅ تم إضافة الطبيب بنجاح!")
                    st.balloons()
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
            else:
                st.warning("الرجاء ملء الحقول المطلوبة")

# ========================
# صفحة العلاجات
# ========================
def render_treatments():
    st.markdown("### 💉 إدارة العلاجات")
    
    tab1, tab2 = st.tabs(["📋 جميع العلاجات", "➕ علاج جديد"])
    
    with tab1:
        treatments = crud.get_all_treatments()
        if not treatments.empty:
            st.dataframe(treatments, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد علاجات")
    
    with tab2:
        st.markdown("#### إضافة علاج جديد")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("اسم العلاج*")
            category = st.selectbox("التصنيف", ["وقائي", "علاجي", "تجميلي", "جراحي"])
            base_price = st.number_input("السعر الأساسي (ج.م)*", min_value=0.0, step=10.0)
        
        with col2:
            description = st.text_area("الوصف")
            duration_minutes = st.number_input("المدة (دقيقة)", min_value=0, step=15)
        
        if st.button("إضافة العلاج", type="primary", use_container_width=True):
            if name and base_price > 0:
                try:
                    crud.create_treatment(name, description, base_price, duration_minutes, category)
                    st.success("✅ تم إضافة العلاج بنجاح!")
                    st.balloons()
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
            else:
                st.warning("الرجاء ملء الحقول المطلوبة")

# ========================
# صفحة المدفوعات
# ========================
def render_payments():
    st.markdown("### 💰 إدارة المدفوعات")
    
    tab1, tab2 = st.tabs(["📋 جميع المدفوعات", "➕ دفعة جديدة"])
    
    with tab1:
        payments = crud.get_all_payments()
        if not payments.empty:
            st.dataframe(payments, use_container_width=True, hide_index=True)
            
            total = payments['amount'].sum()
            st.success(f"💰 إجمالي المدفوعات: {total:,.2f} ج.م")
        else:
            st.info("لا توجد مدفوعات")
    
    with tab2:
        st.markdown("#### إضافة دفعة جديدة")
        
        patients = crud.get_all_patients()
        appointments = crud.get_all_appointments()
        
        if not patients.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                patient_id = st.selectbox(
                    "المريض*",
                    patients['id'].tolist(),
                    format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
                )
                
                amount = st.number_input("المبلغ (ج.م)*", min_value=0.0, step=10.0)
                payment_date = st.date_input("تاريخ الدفع", value=date.today())
            
            with col2:
                appointment_id = st.selectbox(
                    "الموعد (اختياري)",
                    [None] + appointments['id'].tolist(),
                    format_func=lambda x: "بدون موعد" if x is None else f"موعد #{x}"
                ) if not appointments.empty else None
                
                payment_method = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة ائتمان", "تحويل بنكي", "شيك"])
            
            notes = st.text_area("ملاحظات")
            
            if st.button("تسجيل الدفعة", type="primary", use_container_width=True):
                if amount > 0:
                    try:
                        crud.create_payment(
                            appointment_id, patient_id, amount,
                            payment_method, payment_date.isoformat(), notes
                        )
                        st.success("✅ تم تسجيل الدفعة بنجاح!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"حدث خطأ: {str(e)}")
                else:
                    st.warning("الرجاء إدخال مبلغ صحيح")
        else:
            st.warning("يجب إضافة مرضى أولاً")

# ========================
# صفحة المخزون
# ========================
def render_inventory():
    st.markdown("### 📦 إدارة المخزون")
    
    tab1, tab2, tab3 = st.tabs(["📋 جميع العناصر", "➕ عنصر جديد", "⚠️ مخزون منخفض"])
    
    with tab1:
        inventory = crud.get_all_inventory()
        if not inventory.empty:
            st.dataframe(inventory, use_container_width=True, hide_index=True)
        else:
            st.info("لا توجد عناصر في المخزون")
    
    with tab2:
        st.markdown("#### إضافة عنصر جديد")
        
        suppliers = crud.get_all_suppliers()
        
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("اسم العنصر*")
            category = st.selectbox("التصنيف", ["مستهلكات", "أدوية", "أجهزة", "أخرى"])
            quantity = st.number_input("الكمية*", min_value=0, step=1)
            unit_price = st.number_input("سعر الوحدة (ج.م)", min_value=0.0, step=1.0)
        
        with col2:
            min_stock_level = st.number_input("الحد الأدنى للمخزون", min_value=0, value=10, step=1)
            expiry_date = st.date_input("تاريخ انتهاء الصلاحية", min_value=date.today())
            
            supplier_id = st.selectbox(
                "المورد",
                [None] + suppliers['id'].tolist() if not suppliers.empty else [None],
                format_func=lambda x: "بدون مورد" if x is None else suppliers[suppliers['id'] == x]['name'].iloc[0]
            ) if not suppliers.empty else None
        
        if st.button("إضافة العنصر", type="primary", use_container_width=True):
            if item_name and quantity >= 0:
                try:
                    crud.create_inventory_item(
                        item_name, category, quantity, unit_price,
                        min_stock_level, supplier_id,
                        expiry_date.isoformat() if expiry_date else None
                    )
                    st.success("✅ تم إضافة العنصر بنجاح!")
                    st.balloons()
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
            else:
                st.warning("الرجاء ملء الحقول المطلوبة")
    
    with tab3:
        low_stock = crud.get_low_stock_items()
        if not low_stock.empty:
            st.warning(f"⚠️ يوجد {len(low_stock)} عنصر بمخزون منخفض")
            st.dataframe(low_stock, use_container_width=True, hide_index=True)
        else:
            st.success("✅ جميع العناصر في المستوى الآمن")

# ========================
# صفحة الموردين
# ========================
def render_suppliers():
    st.markdown("### 🏪 إدارة الموردين")
    
    tab1, tab2 = st.tabs(["📋 جميع الموردين", "➕ مورد جديد"])
    
    with tab1:
        suppliers = crud.get_all_suppliers()
        if not suppliers.empty:
            st.dataframe(suppliers, use_container_width=True, hide_index=True)
        else:
            st.info("لا يوجد موردين")
    
    with tab2:
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
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
            else:
                st.warning("الرجاء إدخال اسم الشركة")

# ========================
# صفحة المصروفات
# ========================
def render_expenses():
    st.markdown("### 💸 إدارة المصروفات")
    
    tab1, tab2 = st.tabs(["📋 جميع المصروفات", "➕ مصروف جديد"])
    
    with tab1:
        expenses = crud.get_all_expenses()
        if not expenses.empty:
            st.dataframe(expenses, use_container_width=True, hide_index=True)
            
            total = expenses['amount'].sum()
            st.error(f"💸 إجمالي المصروفات: {total:,.2f} ج.م")
        else:
            st.info("لا توجد مصروفات")
    
    with tab2:
        st.markdown("#### إضافة مصروف جديد")
        
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox("التصنيف", ["رواتب", "إيجار", "كهرباء", "صيانة", "مستلزمات", "أخرى"])
            description = st.text_input("الوصف*")
            amount = st.number_input("المبلغ (ج.م)*", min_value=0.0, step=10.0)
        
        with col2:
            expense_date = st.date_input("تاريخ المصروف", value=date.today())
            payment_method = st.selectbox("طريقة الدفع", ["نقدي", "تحويل بنكي", "شيك", "بطاقة ائتمان"])
            receipt_number = st.text_input("رقم الإيصال")
        
        notes = st.text_area("ملاحظات")
        
        if st.button("تسجيل المصروف", type="primary", use_container_width=True):
            if description and amount > 0:
                try:
                    crud.create_expense(
                        category, description, amount,
                        expense_date.isoformat(), payment_method,
                        receipt_number, notes
                    )
                    st.success("✅ تم تسجيل المصروف بنجاح!")
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
            else:
                st.warning("الرجاء ملء الحقول المطلوبة")

# ========================
# صفحة التقارير
# ========================
# ========================
# صفحة التقارير المتقدمة
# ========================
def render_reports():
    st.markdown("""
        <div class='main-header'>
            <h1>📊 التقارير والتحليلات المتقدمة</h1>
            <p>تقارير شاملة عن أداء العيادة</p>
        </div>
    """, unsafe_allow_html=True)
    
    # اختيار الفترة الزمنية
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "📅 من تاريخ", 
            value=date.today() - timedelta(days=30),
            key="report_start"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 إلى تاريخ", 
            value=date.today(),
            key="report_end"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        period_type = st.selectbox(
            "التجميع",
            ["يومي", "شهري", "سنوي"],
            key="period_type"
        )
    
    # تحويل نوع الفترة
    group_by_map = {"يومي": "day", "شهري": "month", "سنوي": "year"}
    group_by = group_by_map[period_type]
    
    # التبويبات
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 التقرير المالي",
        "👨‍⚕️ أداء الأطباء", 
        "💉 العلاجات",
        "👥 المرضى",
        "📦 المخزون",
        "📊 مؤشرات الأداء"
    ])
    
    # ==================== التقرير المالي ====================
    with tab1:
        st.markdown("### 💰 الملخص المالي الشامل")
        
        # الملخص العام
        financial_summary = crud.get_financial_summary(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class='metric-card success'>
                    <div class='metric-label'>💰 إجمالي الإيرادات</div>
                    <div class='metric-value'>{financial_summary['total_revenue']:,.0f}</div>
                    <div class='metric-label'>جنيه مصري</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='metric-card warning'>
                    <div class='metric-label'>💸 إجمالي المصروفات</div>
                    <div class='metric-value'>{financial_summary['total_expenses']:,.0f}</div>
                    <div class='metric-label'>جنيه مصري</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            profit_color = "success" if financial_summary['net_profit'] > 0 else "warning"
            st.markdown(f"""
                <div class='metric-card {profit_color}'>
                    <div class='metric-label'>📊 صافي الربح</div>
                    <div class='metric-value'>{financial_summary['net_profit']:,.0f}</div>
                    <div class='metric-label'>جنيه مصري</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if financial_summary['total_revenue'] > 0:
                profit_margin = (financial_summary['net_profit'] / financial_summary['total_revenue']) * 100
            else:
                profit_margin = 0
            
            st.markdown(f"""
                <div class='metric-card info'>
                    <div class='metric-label'>📈 هامش الربح</div>
                    <div class='metric-value'>{profit_margin:.1f}%</div>
                    <div class='metric-label'>من الإيرادات</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # الإيرادات حسب الفترة
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 📊 الإيرادات ({period_type})")
            revenue_data = crud.get_revenue_by_period(
                start_date.isoformat(),
                end_date.isoformat(),
                group_by
            )
            
            if not revenue_data.empty:
                fig = px.line(
                    revenue_data,
                    x='period',
                    y='total_revenue',
                    markers=True,
                    labels={'period': 'الفترة', 'total_revenue': 'الإيرادات'}
                )
                fig.update_traces(line_color='#38ef7d', line_width=3)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد بيانات للفترة المحددة")
        
        with col2:
            st.markdown("#### 💸 المصروفات حسب الفئة")
            expenses_data = crud.get_expenses_by_category(
                start_date.isoformat(),
                end_date.isoformat()
            )
            
            if not expenses_data.empty:
                fig = px.pie(
                    expenses_data,
                    values='total',
                    names='category',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("لا توجد مصروفات للفترة المحددة")
        
        # طرق الدفع
        st.markdown("#### 💳 طرق الدفع")
        payment_methods = crud.get_payment_methods_stats(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        if not payment_methods.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    payment_methods,
                    x='payment_method',
                    y='total',
                    color='payment_method',
                    labels={'payment_method': 'طريقة الدفع', 'total': 'المبلغ الإجمالي'}
                )
                fig.update_layout(showlegend=False, height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(
                    payment_methods.rename(columns={
                        'payment_method': 'طريقة الدفع',
                        'count': 'عدد المعاملات',
                        'total': 'الإجمالي'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
        
        # تصدير التقرير
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 تصدير PDF", use_container_width=True):
                st.info("🚧 ميزة التصدير قيد التطوير")
        
        with col2:
            if st.button("📊 تصدير Excel", use_container_width=True):
                st.info("🚧 ميزة التصدير قيد التطوير")
        
        with col3:
            if st.button("📧 إرسال بالبريد", use_container_width=True):
                st.info("🚧 ميزة الإرسال قيد التطوير")
    
    # ==================== أداء الأطباء ====================
    with tab2:
        st.markdown("### 👨‍⚕️ تقرير أداء الأطباء")
        
        doctor_performance = crud.get_doctor_performance(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        if not doctor_performance.empty:
            # عرض الجدول
            st.dataframe(
                doctor_performance.rename(columns={
                    'doctor_name': 'الطبيب',
                    'specialization': 'التخصص',
                    'total_appointments': 'إجمالي المواعيد',
                    'completed_appointments': 'المواعيد المكتملة',
                    'total_revenue': 'الإيرادات',
                    'avg_revenue_per_appointment': 'متوسط الإيراد',
                    'commission_rate': 'نسبة العمولة %',
                    'total_commission': 'إجمالي العمولة'
                }).round(2),
                use_container_width=True,
                hide_index=True
            )
            
            # رسوم بيانية
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 الإيرادات حسب الطبيب")
                fig = px.bar(
                    doctor_performance,
                    x='doctor_name',
                    y='total_revenue',
                    color='doctor_name',
                    labels={'doctor_name': 'الطبيب', 'total_revenue': 'الإيرادات'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📈 معدل إتمام المواعيد")
                doctor_performance['completion_rate'] = (
                    doctor_performance['completed_appointments'] / 
                    doctor_performance['total_appointments'] * 100
                ).round(2)
                
                fig = px.bar(
                    doctor_performance,
                    x='doctor_name',
                    y='completion_rate',
                    color='completion_rate',
                    color_continuous_scale='Greens',
                    labels={'doctor_name': 'الطبيب', 'completion_rate': 'معدل الإتمام %'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات للفترة المحددة")
    
    # ==================== تقرير العلاجات ====================
    with tab3:
        st.markdown("### 💉 تقرير العلاجات الأكثر طلباً")
        
        treatment_stats = crud.get_treatment_popularity(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        if not treatment_stats.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 أكثر العلاجات حجزاً")
                fig = px.pie(
                    treatment_stats.head(10),
                    values='booking_count',
                    names='treatment_name',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 💰 أعلى العلاجات إيراداً")
                fig = px.bar(
                    treatment_stats.head(10),
                    x='treatment_name',
                    y='total_revenue',
                    color='category',
                    labels={'treatment_name': 'العلاج', 'total_revenue': 'الإيرادات'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # الجدول التفصيلي
            st.markdown("#### 📋 جدول العلاجات التفصيلي")
            st.dataframe(
                treatment_stats.rename(columns={
                    'treatment_name': 'العلاج',
                    'category': 'الفئة',
                    'booking_count': 'عدد الحجوزات',
                    'total_revenue': 'الإيرادات',
                    'avg_price': 'متوسط السعر'
                }).round(2),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا توجد بيانات للفترة المحددة")
    
    # ==================== تقرير المرضى ====================
    with tab4:
        st.markdown("### 👥 تحليلات المرضى")
        
        # إحصائيات المرضى
        patient_stats = crud.get_patient_statistics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 توزيع المرضى حسب الجنس")
            if not patient_stats['gender'].empty:
                fig = px.pie(
                    patient_stats['gender'],
                    values='count',
                    names='gender',
                    color_discrete_map={'ذكر': '#4facfe', 'أنثى': '#f093fb'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 توزيع المرضى حسب الفئة العمرية")
            if not patient_stats['age'].empty:
                fig = px.bar(
                    patient_stats['age'],
                    x='age_group',
                    y='count',
                    color='age_group',
                    labels={'age_group': 'الفئة العمرية', 'count': 'العدد'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # أكثر المرضى زيارة
        st.markdown("#### 🏆 أكثر المرضى زيارة")
        top_patients = crud.get_top_patients(
            start_date.isoformat(),
            end_date.isoformat(),
            limit=10
        )
        
        if not top_patients.empty:
            st.dataframe(
                top_patients.rename(columns={
                    'patient_name': 'المريض',
                    'phone': 'الهاتف',
                    'visit_count': 'عدد الزيارات',
                    'total_spent': 'إجمالي الإنفاق',
                    'last_visit': 'آخر زيارة'
                }).round(2),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا توجد بيانات")
        
        # حالة المواعيد
        st.markdown("#### 📅 توزيع حالات المواعيد")
        appointment_status = crud.get_appointment_status_stats(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        if not appointment_status.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    appointment_status,
                    values='count',
                    names='status',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(
                    appointment_status.rename(columns={
                        'status': 'الحالة',
                        'count': 'العدد',
                        'total_revenue': 'الإيرادات'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
    
    # ==================== تقرير المخزون ====================
    with tab5:
        st.markdown("### 📦 تقرير المخزون")
        
        # قيمة المخزون
        inventory_value = crud.get_inventory_value()
        
        if not inventory_value.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 💰 قيمة المخزون حسب الفئة")
                fig = px.bar(
                    inventory_value,
                    x='category',
                    y='total_value',
                    color='category',
                    labels={'category': 'الفئة', 'total_value': 'القيمة الإجمالية'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 توزيع الكميات")
                fig = px.pie(
                    inventory_value,
                    values='total_quantity',
                    names='category',
                    hole=0.4
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # الجدول التفصيلي
            total_value = inventory_value['total_value'].sum()
            st.success(f"💰 إجمالي قيمة المخزون: {total_value:,.2f} جنيه")
            
            st.dataframe(
                inventory_value.rename(columns={
                    'category': 'الفئة',
                    'total_value': 'القيمة الإجمالية',
                    'total_quantity': 'إجمالي الكمية',
                    'item_count': 'عدد الأصناف'
                }),
                use_container_width=True,
                hide_index=True
            )
        
        # المخزون المنخفض
        st.markdown("#### ⚠️ تنبيهات المخزون المنخفض")
        low_stock = crud.get_low_stock_items()
        
        if not low_stock.empty:
            st.warning(f"يوجد {len(low_stock)} عنصر بمخزون منخفض")
            st.dataframe(
                low_stock[['item_name', 'category', 'quantity', 'min_stock_level']].rename(columns={
                    'item_name': 'الصنف',
                    'category': 'الفئة',
                    'quantity': 'الكمية الحالية',
                    'min_stock_level': 'الحد الأدنى'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ جميع الأصناف في المستوى الآمن")
        
        # المخزون قريب الانتهاء
        st.markdown("#### 📅 أصناف قريبة من انتهاء الصلاحية")
        expiring = crud.get_expiring_inventory(days=60)
        
        if not expiring.empty:
            st.warning(f"يوجد {len(expiring)} صنف ينتهي خلال 60 يوم")
            st.dataframe(
                expiring.rename(columns={
                    'item_name': 'الصنف',
                    'category': 'الفئة',
                    'quantity': 'الكمية',
                    'expiry_date': 'تاريخ الانتهاء',
                    'supplier_name': 'المورد',
                    'days_to_expire': 'الأيام المتبقية'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ لا توجد أصناف قريبة من الانتهاء")
    
    # ==================== مؤشرات الأداء ====================
    with tab6:
        st.markdown("### 📊 مؤشرات الأداء الرئيسية (KPIs)")
        
        # الإيرادات اليومية
        st.markdown("#### 📈 مقارنة الإيرادات اليومية (آخر 30 يوم)")
        daily_revenue = crud.get_daily_revenue_comparison(days=30)
        
        if not daily_revenue.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_revenue['payment_date'],
                y=daily_revenue['daily_revenue'],
                mode='lines+markers',
                name='الإيرادات اليومية',
                line=dict(color='#38ef7d', width=3),
                fill='tozeroy'
            ))
            
            fig.update_layout(
                xaxis_title='التاريخ',
                yaxis_title='الإيرادات (جنيه)',
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # الإحصائيات
            col1, col2, col3, col4 = st.columns(4)
            
            avg_daily = daily_revenue['daily_revenue'].mean()
            max_daily = daily_revenue['daily_revenue'].max()
            min_daily = daily_revenue['daily_revenue'].min()
            total_days = len(daily_revenue)
            
            with col1:
                st.metric("📊 متوسط الإيراد اليومي", f"{avg_daily:,.0f} ج.م")
            
            with col2:
                st.metric("🔝 أعلى إيراد يومي", f"{max_daily:,.0f} ج.م")
            
            with col3:
                st.metric("🔽 أقل إيراد يومي", f"{min_daily:,.0f} ج.م")
            
            with col4:
                st.metric("📅 عدد أيام العمل", f"{total_days} يوم")
        
        # مؤشرات إضافية
        st.markdown("---")
        st.markdown("#### 🎯 مؤشرات الأداء الإضافية")
        
        col1, col2, col3 = st.columns(3)
        
        # معدل إشغال المواعيد
        all_appointments = crud.get_all_appointments()
        if not all_appointments.empty:
            total_apps = len(all_appointments)
            completed_apps = len(all_appointments[all_appointments['status'] == 'مكتمل'])
            completion_rate = (completed_apps / total_apps * 100) if total_apps > 0 else 0
            
            with col1:
                st.metric(
                    "✅ معدل إتمام المواعيد",
                    f"{completion_rate:.1f}%",
                    delta=f"{completed_apps}/{total_apps}"
                )
        
        # متوسط قيمة الموعد
        if not all_appointments.empty and all_appointments['total_cost'].sum() > 0:
            avg_appointment_value = all_appointments['total_cost'].mean()
            
            with col2:
                st.metric(
                    "💰 متوسط قيمة الموعد",
                    f"{avg_appointment_value:,.0f} ج.م"
                )
        
        # عدد المرضى الجدد
        patients = crud.get_all_patients()
        if not patients.empty:
            recent_patients = len(patients[
                pd.to_datetime(patients['created_at']) >= 
                pd.to_datetime(start_date)
            ])
            
            with col3:
                st.metric(
                    "👥 مرضى جدد",
                    f"{recent_patients} مريض",
                    delta="في الفترة المحددة"
                )
# ========================
# التوجيه إلى الصفحات
# ========================
def main():
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'appointments':
        render_appointments()
    elif page == 'patients':
        render_patients()
    elif page == 'doctors':
        render_doctors()
    elif page == 'treatments':
        render_treatments()
    elif page == 'payments':
        render_payments()
    elif page == 'inventory':
        render_inventory()
    elif page == 'suppliers':
        render_suppliers()
    elif page == 'expenses':
        render_expenses()
    elif page == 'reports':
        render_reports()

if __name__ == "__main__":
    main()
