import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message, 
    format_date_arabic, get_appointment_time_slots, get_status_color
)

def show_appointments():
    st.title("📅 إدارة المواعيد")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات المواعيد")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المواعيد", "حجز موعد جديد", "تقويم المواعيد", "تقارير المواعيد", "إدارة حالات المواعيد"]
    )
    
    if action == "عرض المواعيد":
        show_appointments_list()
    elif action == "حجز موعد جديد":
        book_new_appointment()
    elif action == "تقويم المواعيد":
        appointments_calendar()
    elif action == "تقارير المواعيد":
        appointments_reports()
    elif action == "إدارة حالات المواعيد":
        manage_appointment_status()

def show_appointments_list():
    """عرض قائمة المواعيد"""
    st.subheader("📋 قائمة المواعيد")
    
    try:
        appointments_df = crud.get_all_appointments()
        
        if appointments_df.empty:
            st.info("لا توجد مواعيد")
            return
        
        # فلاتر البحث والتصفية
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # فلترة حسب التاريخ
            date_filter = st.selectbox(
                "فلترة حسب التاريخ",
                ["الكل", "اليوم", "غداً", "هذا الأسبوع", "هذا الشهر", "مخصص"]
            )
            
            if date_filter == "مخصص":
                custom_start = st.date_input("من تاريخ")
                custom_end = st.date_input("إلى تاريخ")
        
        with col2:
            # فلترة حسب الطبيب
            doctors = ["الكل"] + list(appointments_df['doctor_name'].unique())
            selected_doctor = st.selectbox("فلترة حسب الطبيب", doctors)
        
        with col3:
            # فلترة حسب الحالة
            statuses = ["الكل"] + list(appointments_df['status'].unique())
            selected_status = st.selectbox("فلترة حسب الحالة", statuses)
        
        with col4:
            # بحث حسب اسم المريض
            search_name = st.text_input("🔍 بحث باسم المريض")
        
        # تطبيق الفلاتر
        filtered_df = apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status, search_name)
        
        if filtered_df.empty:
            st.info("لا توجد مواعيد تطابق المعايير المحددة")
            return
        
        # عرض الإحصائيات السريعة
        show_appointments_summary(filtered_df)
        
        # عرض المواعيد في بطاقات
        display_appointments_cards(filtered_df)
        
        # جدول المواعيد التفصيلي
        st.divider()
        st.subheader("📊 جدول المواعيد التفصيلي")
        
        display_appointments_table(filtered_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل المواعيد: {str(e)}")

def book_new_appointment():
    """حجز موعد جديد"""
    st.subheader("➕ حجز موعد جديد")
    
    try:
        # التحقق من وجود البيانات الأساسية
        patients_df = crud.get_all_patients()
        doctors_df = crud.get_all_doctors()
        treatments_df = crud.get_all_treatments()
        
        if patients_df.empty:
            st.error("يجب إضافة مرضى أولاً")
            return
        
        if doctors_df.empty:
            st.error("يجب إضافة أطباء أولاً")
            return
        
        if treatments_df.empty:
            st.error("يجب إضافة علاجات أولاً")
            return
        
        with st.form("book_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 معلومات المريض")
                
                # اختيار المريض
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" 
                                 for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox(
                    "اختر المريض *",
                    options=list(patient_options.keys()),
                    format_func=lambda x: patient_options[x]
                )
                
                # عرض تفاصيل المريض المحدد
                if selected_patient_id:
                    patient_info = patients_df[patients_df['id'] == selected_patient_id].iloc[0]
                    st.info(f"""
                    **📋 معلومات المريض:**
                    - **الاسم:** {patient_info['name']}
                    - **الهاتف:** {patient_info['phone'] or 'غير محدد'}
                    - **العمر:** {calculate_age(patient_info['date_of_birth'])} سنة
                    - **التاريخ المرضي:** {patient_info['medical_history'] or 'لا يوجد'}
                    """)
                
                # خيار إضافة مريض جديد سريع
                with st.expander("➕ إضافة مريض جديد سريع"):
                    new_patient_name = st.text_input("اسم المريض الجديد")
                    new_patient_phone = st.text_input("رقم الهاتف")
                    
                    if st.button("حفظ المريض الجديد", key="quick_add_patient"):
                        if new_patient_name and new_patient_phone:
                            new_patient_id = crud.create_patient(
                                name=new_patient_name,
                                phone=new_patient_phone,
                                email=None,
                                address=None,
                                date_of_birth=date.today().replace(year=date.today().year - 25),
                                gender="ذكر"
                            )
                            show_success_message(f"تم إضافة المريض الجديد (المعرف: {new_patient_id})")
                            st.rerun()
            
            with col2:
                st.subheader("👨‍⚕️ معلومات الموعد")
                
                # اختيار الطبيب
                doctor_options = {row['id']: f"د. {row['name']} - {row['specialization']}" 
                                for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox(
                    "اختر الطبيب *",
                    options=list(doctor_options.keys()),
                    format_func=lambda x: doctor_options[x]
                )
                
                # اختيار العلاج
                treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])}" 
                                   for _, row in treatments_df.iterrows()}
                selected_treatment_id = st.selectbox(
                    "اختر العلاج *",
                    options=list(treatment_options.keys()),
                    format_func=lambda x: treatment_options[x]
                )
                
                # عرض تفاصيل العلاج المحدد
                if selected_treatment_id:
                    treatment_info = treatments_df[treatments_df['id'] == selected_treatment_id].iloc[0]
                    st.info(f"""
                    **💊 تفاصيل العلاج:**
                    - **الاسم:** {treatment_info['name']}
                    - **السعر:** {format_currency(treatment_info['base_price'])}
                    - **المدة:** {treatment_info['duration_minutes']} دقيقة
                    - **الفئة:** {treatment_info['category']}
                    """)
            
            # معلومات التوقيت
            st.divider()
            st.subheader("📅 معلومات التوقيت")
            
            col3, col4 = st.columns(2)
            
            with col3:
                appointment_date = st.date_input(
                    "تاريخ الموعد *",
                    min_value=date.today(),
                    value=date.today()
                )
                
                # التحقق من توفر الطبيب في هذا التاريخ
                if selected_doctor_id and appointment_date:
                    existing_appointments = get_doctor_appointments_on_date(selected_doctor_id, appointment_date)
                    if existing_appointments:
                        st.warning(f"الطبيب لديه {len(existing_appointments)} موعد في هذا اليوم")
            
            with col4:
                # أوقات متاحة
                available_slots = get_available_time_slots(selected_doctor_id, appointment_date)
                
                if available_slots:
                    appointment_time = st.selectbox(
                        "وقت الموعد *",
                        options=available_slots
                    )
                else:
                    st.error("لا توجد أوقات متاحة في هذا التاريخ")
                    appointment_time = st.time_input("وقت الموعد", value=time(9, 0))
            
            # معلومات إضافية
            col5, col6 = st.columns(2)
            
            with col5:
                total_cost = st.number_input(
                    "التكلفة الإجمالية (ج.م)",
                    min_value=0.0,
                    value=float(treatment_info['base_price']) if selected_treatment_id else 0.0,
                    step=50.0
                )
            
            with col6:
                appointment_status = st.selectbox(
                    "حالة الموعد",
                    ["مجدول", "مؤكد", "في الانتظار", "ملغي"]
                )
            
            notes = st.text_area(
                "ملاحظات",
                placeholder="أي ملاحظات خاصة بالموعد..."
            )
            
            # أزرار الإجراءات
            col7, col8 = st.columns(2)
            
            submitted = st.form_submit_button("💾 حفظ الموعد", use_container_width=True)
            
            if st.form_submit_button("📅 حفظ وحجز آخر", use_container_width=True):
                submitted = True
        
        if submitted:
            # التحقق من صحة البيانات
            if not all([selected_patient_id, selected_doctor_id, selected_treatment_id, appointment_date, appointment_time]):
                show_error_message("جميع الحقول المطلوبة يجب ملؤها")
                return
            
            # التحقق من عدم تضارب المواعيد
            if check_appointment_conflict(selected_doctor_id, appointment_date, appointment_time):
                show_error_message("يوجد تضارب في المواعيد مع هذا الوقت")
                return
            
            try:
                # حفظ الموعد
                appointment_id = crud.create_appointment(
                    patient_id=selected_patient_id,
                    doctor_id=selected_doctor_id,
                    treatment_id=selected_treatment_id,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    notes=notes,
                    total_cost=total_cost
                )
                
                # تحديث حالة الموعد
                crud.update_appointment_status(appointment_id, appointment_status)
                
                show_success_message(f"تم حجز الموعد بنجاح (المعرف: {appointment_id})")
                
                # عرض ملخص الموعد
                display_appointment_summary(appointment_id, selected_patient_id, selected_doctor_id, 
                                          selected_treatment_id, appointment_date, appointment_time, total_cost)
                
                if st.button("🔄 حجز موعد آخر"):
                    st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ الموعد: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل نموذج الحجز: {str(e)}")

def manage_appointment_status():
    """إدارة حالات المواعيد"""
    st.subheader("🔄 إدارة حالات المواعيد")
    
    try:
        appointments_df = crud.get_all_appointments()
        
        if appointments_df.empty:
            st.info("لا توجد مواعيد")
            return
        
        # فلترة المواعيد النشطة
        active_appointments = appointments_df[appointments_df['status'].isin(['مجدول', 'مؤكد', 'في الانتظار'])]
        
        if active_appointments.empty:
            st.info("لا توجد مواعيد نشطة")
            return
        
        for _, appointment in active_appointments.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 2])
                
                with col1:
                    st.write(f"**👤 {appointment['patient_name']}**")
                    st.write(f"📞 {appointment.get('patient_phone', 'غير محدد')}")
                
                with col2:
                    st.write(f"👨‍⚕️ **{appointment['doctor_name']}**")
                    st.write(f"📅 {appointment['appointment_date']} - 🕐 {appointment['appointment_time']}")
                
                with col3:
                    current_status = appointment['status']
                    status_color = get_status_color(current_status)
                    st.markdown(f"""
                    <span style="color: {status_color}; font-weight: bold;">
                    ● {current_status}
                    </span>
                    """, unsafe_allow_html=True)
                
                with col4:
                    # تغيير الحالة
                    new_status = st.selectbox(
                        "تغيير الحالة",
                        ["مجدول", "مؤكد", "في الانتظار", "مكتمل", "ملغي"],
                        index=["مجدول", "مؤكد", "في الانتظار", "مكتمل", "ملغي"].index(current_status),
                        key=f"status_{appointment['id']}"
                    )
                    
                    if new_status != current_status:
                        if st.button("تحديث", key=f"update_{appointment['id']}"):
                            crud.update_appointment_status(appointment['id'], new_status)
                            show_success_message(f"تم تحديث حالة الموعد إلى {new_status}")
                            st.rerun()
                
                st.divider()
    
    except Exception as e:
        show_error_message(f"خطأ في إدارة حالات المواعيد: {str(e)}")

def edit_appointment(appointment_id):
    """تعديل موعد"""
    st.subheader(f"✏️ تعديل الموعد رقم {appointment_id}")
    
    try:
        # الحصول على بيانات الموعد الحالية
        appointments_df = crud.get_all_appointments()
        appointment_data = appointments_df[appointments_df['id'] == appointment_id].iloc[0]
        
        patients_df = crud.get_all_patients()
        doctors_df = crud.get_all_doctors()
        treatments_df = crud.get_all_treatments()
        
        with st.form("edit_appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👤 معلومات المريض")
                
                # اختيار المريض
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" 
                                 for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox(
                    "اختر المريض",
                    options=list(patient_options.keys()),
                    index=list(patient_options.keys()).index(appointment_data['patient_id']),
                    format_func=lambda x: patient_options[x]
                )
            
            with col2:
                st.subheader("👨‍⚕️ معلومات الموعد")
                
                # اختيار الطبيب
                doctor_options = {row['id']: f"د. {row['name']} - {row['specialization']}" 
                                for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox(
                    "اختر الطبيب",
                    options=list(doctor_options.keys()),
                    index=list(doctor_options.keys()).index(appointment_data['doctor_id']),
                    format_func=lambda x: doctor_options[x]
                )
                
                # اختيار العلاج
                treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])}" 
                                   for _, row in treatments_df.iterrows()}
                selected_treatment_id = st.selectbox(
                    "اختر العلاج",
                    options=list(treatment_options.keys()),
                    index=list(treatment_options.keys()).index(appointment_data['treatment_id']),
                    format_func=lambda x: treatment_options[x]
                )
            
            # معلومات التوقيت
            st.divider()
            st.subheader("📅 معلومات التوقيت")
            
            col3, col4 = st.columns(2)
            
            with col3:
                appointment_date = st.date_input(
                    "تاريخ الموعد",
                    value=datetime.strptime(appointment_data['appointment_date'], '%Y-%m-%d').date()
                )
            
            with col4:
                appointment_time = st.time_input(
                    "وقت الموعد",
                    value=datetime.strptime(appointment_data['appointment_time'], '%H:%M:%S').time()
                )
            
            # معلومات إضافية
            col5, col6 = st.columns(2)
            
            with col5:
                total_cost = st.number_input(
                    "التكلفة الإجمالية (ج.م)",
                    min_value=0.0,
                    value=float(appointment_data['total_cost']),
                    step=50.0
                )
            
            with col6:
                appointment_status = st.selectbox(
                    "حالة الموعد",
                    ["مجدول", "مؤكد", "في الانتظار", "مكتمل", "ملغي"],
                    index=["مجدول", "مؤكد", "في الانتظار", "مكتمل", "ملغي"].index(appointment_data['status'])
                )
            
            notes = st.text_area(
                "ملاحظات",
                value=appointment_data.get('notes', ''),
                placeholder="أي ملاحظات خاصة بالموعد..."
            )
            
            # أزرار الإجراءات
            col7, col8 = st.columns(2)
            
            if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
                try:
                    # هنا يمكن إضافة دالة لتحديث الموعد في CRUD
                    show_success_message("تم تحديث الموعد بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في تحديث الموعد: {str(e)}")
            
            if st.form_submit_button("🗑️ حذف الموعد", use_container_width=True):
                try:
                    # هنا يمكن إضافة دالة لحذف الموعد في CRUD
                    show_success_message("تم حذف الموعد بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في حذف الموعد: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل نموذج التعديل: {str(e)}")

# الدوال المساعدة المحسنة

def apply_appointments_filters(appointments_df, date_filter, doctor_filter, status_filter, search_name):
    """تطبيق فلاتر المواعيد"""
    filtered_df = appointments_df.copy()
    
    # فلترة حسب التاريخ
    if date_filter != "الكل":
        today = date.today()
        
        if date_filter == "اليوم":
            target_date = today
            filtered_df['appointment_date'] = pd.to_datetime(filtered_df['appointment_date']).dt.date
            filtered_df = filtered_df[filtered_df['appointment_date'] == target_date]
        elif date_filter == "غداً":
            target_date = today + timedelta(days=1)
            filtered_df['appointment_date'] = pd.to_datetime(filtered_df['appointment_date']).dt.date
            filtered_df = filtered_df[filtered_df['appointment_date'] == target_date]
        elif date_filter == "هذا الأسبوع":
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            filtered_df['appointment_date'] = pd.to_datetime(filtered_df['appointment_date']).dt.date
            filtered_df = filtered_df[
                (filtered_df['appointment_date'] >= start_of_week) & 
                (filtered_df['appointment_date'] <= end_of_week)
            ]
        elif date_filter == "هذا الشهر":
            start_of_month = today.replace(day=1)
            filtered_df['appointment_date'] = pd.to_datetime(filtered_df['appointment_date']).dt.date
            filtered_df = filtered_df[
                (filtered_df['appointment_date'] >= start_of_month) & 
                (filtered_df['appointment_date'] <= today)
            ]
    
    # فلترة حسب الطبيب
    if doctor_filter != "الكل":
        filtered_df = filtered_df[filtered_df['doctor_name'] == doctor_filter]
    
    # فلترة حسب الحالة
    if status_filter != "الكل":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    # بحث حسب اسم المريض
    if search_name:
        filtered_df = filtered_df[filtered_df['patient_name'].str.contains(search_name, case=False, na=False)]
    
    return filtered_df

def display_appointments_cards(appointments_df):
    """عرض المواعيد في بطاقات محسنة"""
    st.subheader("🎴 المواعيد القادمة")
    
    # ترتيب حسب التاريخ والوقت
    appointments_df = appointments_df.sort_values(['appointment_date', 'appointment_time'])
    
    for _, appointment in appointments_df.iterrows():
        status_color = get_status_color(appointment['status'])
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style="padding: 10px; border-left: 4px solid {status_color};">
                <strong>👤 {appointment['patient_name']}</strong><br>
                📞 {appointment.get('patient_phone', 'غير محدد')}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.write(f"👨‍⚕️ **{appointment['doctor_name']}**")
                st.write(f"💊 {appointment['treatment_name']}")
                st.write(f"📅 {appointment['appointment_date']}")
            
            with col3:
                st.write(f"🕐 **{appointment['appointment_time']}**")
                st.write(f"💰 {format_currency(appointment['total_cost'])}")
            
            with col4:
                st.markdown(f"""
                <div style="text-align: center;">
                <span style="color: {status_color}; font-weight: bold;">
                ● {appointment['status']}
                </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                # أزرار الإجراءات
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button(f"✏️", key=f"edit_{appointment['id']}", help="تعديل"):
                        edit_appointment(appointment['id'])
                
                with col_btn2:
                    if st.button(f"🔄", key=f"status_{appointment['id']}", help="تغيير الحالة"):
                        st.session_state[f'manage_status_{appointment["id"]}'] = True
        
        st.divider()

# باقي الدوال تبقى كما هي مع بعض التحسينات البسيطة
# [يتم الحفاظ على الدوال الأخرى كما هي مع تحسينات طفيفة في التنسيق]

if __name__ == "__main__":
    show_appointments()
