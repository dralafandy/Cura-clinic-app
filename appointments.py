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
            
            custom_start = None
            custom_end = None
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
        filtered_df = apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status, search_name, custom_start, custom_end)
        
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

def show_appointments_summary(appointments_df):
    """عرض ملخص المواعيد"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_appointments = len(appointments_df)
        st.metric("📅 إجمالي المواعيد", total_appointments)
    
    with col2:
        confirmed_appointments = len(appointments_df[appointments_df['status'] == 'مؤكد'])
        st.metric("✅ المؤكدة", confirmed_appointments)
    
    with col3:
        completed_appointments = len(appointments_df[appointments_df['status'] == 'مكتمل'])
        st.metric("✅ المكتملة", completed_appointments)
    
    with col4:
        total_revenue = appointments_df['total_cost'].sum()
        st.metric("💰 إجمالي الإيرادات", format_currency(total_revenue))

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

def display_appointments_table(appointments_df):
    """عرض جدول المواعيد التفصيلي"""
    st.dataframe(
        appointments_df[['patient_name', 'doctor_name', 'treatment_name', 
                        'appointment_date', 'appointment_time', 'status', 'total_cost']],
        column_config={
            'patient_name': 'اسم المريض',
            'doctor_name': 'اسم الطبيب',
            'treatment_name': 'العلاج',
            'appointment_date': 'التاريخ',
            'appointment_time': 'الوقت',
            'status': 'الحالة',
            'total_cost': st.column_config.NumberColumn(
                'التكلفة',
                format="%.2f ج.م"
            )
        },
        use_container_width=True,
        hide_index=True
    )

def apply_appointments_filters(appointments_df, date_filter, doctor_filter, status_filter, search_name, custom_start=None, custom_end=None):
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
        elif date_filter == "مخصص" and custom_start and custom_end:
            filtered_df['appointment_date'] = pd.to_datetime(filtered_df['appointment_date']).dt.date
            filtered_df = filtered_df[
                (filtered_df['appointment_date'] >= custom_start) & 
                (filtered_df['appointment_date'] <= custom_end)
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
            if crud.check_appointment_conflict(selected_doctor_id, appointment_date, appointment_time):
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
        appointment_data = crud.get_appointment_by_id(appointment_id)
        
        if not appointment_data:
            show_error_message("لم يتم العثور على الموعد")
            return
        
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
                    crud.update_appointment(
                        appointment_id=appointment_id,
                        patient_id=selected_patient_id,
                        doctor_id=selected_doctor_id,
                        treatment_id=selected_treatment_id,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        notes=notes,
                        total_cost=total_cost,
                        status=appointment_status
                    )
                    show_success_message("تم تحديث الموعد بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في تحديث الموعد: {str(e)}")
            
            if st.form_submit_button("🗑️ حذف الموعد", use_container_width=True):
                try:
                    if can_delete_appointment(appointment_id):
                        crud.delete_appointment(appointment_id)
                        show_success_message("تم حذف الموعد بنجاح")
                        st.rerun()
                    else:
                        show_error_message("لا يمكن حذف الموعد لأنه ليس في حالة مجدولة أو في الانتظار")
                except Exception as e:
                    show_error_message(f"خطأ في حذف الموعد: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل نموذج التعديل: {str(e)}")

# الدوال المساعدة
def get_available_time_slots(doctor_id, appointment_date):
    """الحصول على الأوقات المتاحة للطبيب"""
    all_slots = get_appointment_time_slots()
    
    # الحصول على المواعيد المحجوزة
    existing_appointments = get_doctor_appointments_on_date(doctor_id, appointment_date)
    booked_times = [app['appointment_time'] for app in existing_appointments]
    
    # إزالة الأوقات المحجوزة
    available_slots = [slot for slot in all_slots if slot not in booked_times]
    
    return available_slots

def get_doctor_appointments_on_date(doctor_id, appointment_date):
    """الحصول على مواعيد الطبيب في تاريخ محدد"""
    appointments_df = crud.get_appointments_by_date(appointment_date)
    
    if appointments_df.empty:
        return []
    
    doctor_appointments = appointments_df[appointments_df['doctor_name'] == get_doctor_name_by_id(doctor_id)]
    
    return doctor_appointments.to_dict('records')

def get_doctor_name_by_id(doctor_id):
    """الحصول على اسم الطبيب من المعرف"""
    doctor = crud.get_doctor_by_id(doctor_id)
    return doctor[1] if doctor else ""

def check_appointment_conflict(doctor_id, appointment_date, appointment_time):
    """التحقق من تضارب المواعيد"""
    existing_appointments = get_doctor_appointments_on_date(doctor_id, appointment_date)
    
    for appointment in existing_appointments:
        if appointment['appointment_time'] == str(appointment_time):
            return True
    
    return False

def calculate_age(birth_date):
    """حساب العمر من تاريخ الميلاد"""
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
    
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def display_appointment_summary(appointment_id, patient_id, doctor_id, treatment_id, 
                              appointment_date, appointment_time, total_cost):
    """عرض ملخص الموعد المحجوز"""
    st.success("✅ تم حجز الموعد بنجاح!")
    
    # الحصول على التفاصيل
    patient = crud.get_patient_by_id(patient_id)
    doctor = crud.get_doctor_by_id(doctor_id)
    treatment = crud.get_treatment_by_id(treatment_id)
    
    st.info(f"""
    **📋 ملخص الموعد:**
    - **رقم الموعد:** {appointment_id}
    - **المريض:** {patient[1]} - {patient[3]}
    - **الطبيب:** د. {doctor[1]}
    - **العلاج:** {treatment[1]}
    - **التاريخ:** {format_date_arabic(appointment_date)}
    - **الوقت:** {appointment_time}
    - **التكلفة:** {format_currency(total_cost)}
    """)

def get_appointment_details(appointment_id):
    """الحصول على تفاصيل الموعد"""
    try:
        return crud.get_appointment_by_id(appointment_id)
    except Exception as e:
        show_error_message(f"خطأ في تحميل بيانات الموعد: {str(e)}")
        return None

def can_delete_appointment(appointment_id):
    """التحقق من إمكانية حذف الموعد"""
    appointment = crud.get_appointment_by_id(appointment_id)
    if appointment:
        status = appointment['status']
        # يمكن حذف المواعيد المجدولة فقط
        return status in ['مجدول', 'في الانتظار']
    return False

# الدوال الأخرى تبقى كما هي
def appointments_calendar():
    """تقويم المواعيد"""
    st.subheader("📅 تقويم المواعيد")
    
    try:
        # اختيار الأسبوع أو الشهر للعرض
        view_type = st.radio("نوع العرض", ["أسبوعي", "شهري"], horizontal=True)
        
        if view_type == "أسبوعي":
            show_weekly_calendar()
        else:
            show_monthly_calendar()
    
    except Exception as e:
        show_error_message(f"خطأ في عرض التقويم: {str(e)}")

def show_weekly_calendar():
    """عرض التقويم الأسبوعي"""
    # اختيار الأسبوع
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    selected_week_start = st.date_input(
        "اختر بداية الأسبوع",
        value=start_of_week,
        help="سيتم عرض 7 أيام من هذا التاريخ"
    )
    
    # عرض أيام الأسبوع
    days = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
    
    for i, day_name in enumerate(days):
        current_date = selected_week_start + timedelta(days=i)
        
        st.subheader(f"{day_name} - {format_date_arabic(current_date)}")
        
        day_appointments = crud.get_appointments_by_date(current_date)
        
        if not day_appointments.empty:
            for _, appointment in day_appointments.iterrows():
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"🕐 **{appointment['appointment_time']}**")
                
                with col2:
                    st.write(f"👤 {appointment['patient_name']}")
                    st.write(f"👨‍⚕️ {appointment['doctor_name']}")
                
                with col3:
                    status_color = get_status_color(appointment['status'])
                    st.markdown(f"""
                    <span style="color: {status_color}; font-weight: bold;">
                    ● {appointment['status']}
                    </span>
                    """, unsafe_allow_html=True)
        else:
            st.info("لا توجد مواعيد")
        
        st.divider()

def show_monthly_calendar():
    """عرض التقويم الشهري"""
    import calendar
    
    # اختيار الشهر والسنة
    col1, col2 = st.columns(2)
    
    with col1:
        selected_month = st.selectbox(
            "الشهر",
            range(1, 13),
            index=datetime.now().month - 1,
            format_func=lambda x: calendar.month_name[x]
        )
    
    with col2:
        selected_year = st.selectbox(
            "السنة",
            range(2020, 2030),
            index=datetime.now().year - 2020
        )
    
    # إنشاء التقويم
    cal = calendar.monthcalendar(selected_year, selected_month)
    
    # عناوين الأيام
    st.write("### " + calendar.month_name[selected_month] + f" {selected_year}")
    
    days_header = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
    
    # عرض التقويم
    for week in cal:
        cols = st.columns(7)
        
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")  # يوم فارغ
                else:
                    current_date = date(selected_year, selected_month, day)
                    day_appointments = crud.get_appointments_by_date(current_date)
                    
                    appointments_count = len(day_appointments) if not day_appointments.empty else 0
                    
                    if appointments_count > 0:
                        st.markdown(f"""
                        <div style="background-color: #e3f2fd; padding: 5px; border-radius: 5px; text-align: center;">
                        <strong>{day}</strong><br>
                        <small>{appointments_count} موعد</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="padding: 5px; text-align: center;">
                        {day}
                        </div>
                        """, unsafe_allow_html=True)

def appointments_reports():
    """تقارير المواعيد"""
    st.subheader("📊 تقارير المواعيد")
    
    try:
        # فلترة التواريخ
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("إلى تاريخ", value=date.today())
        
        appointments_df = crud.get_all_appointments()
        
        if appointments_df.empty:
            st.info("لا توجد مواعيد")
            return
        
        # فلترة البيانات
        appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date']).dt.date
        filtered_appointments = appointments_df[
            (appointments_df['appointment_date'] >= start_date) & 
            (appointments_df['appointment_date'] <= end_date)
        ]
        
        if filtered_appointments.empty:
            st.info("لا توجد مواعيد في هذه الفترة")
            return
        
        # إحصائيات عامة
        show_appointments_statistics(filtered_appointments)
        
        # تحليل أداء المواعيد
        show_appointments_analysis(filtered_appointments)
        
        # تقرير الأطباء
        show_doctors_appointments_report(filtered_appointments)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل التقارير: {str(e)}")

def show_appointments_statistics(appointments_df):
    """عرض إحصائيات المواعيد"""
    st.subheader("📊 إحصائيات عامة")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_appointments = len(appointments_df)
        st.metric("📅 إجمالي المواعيد", total_appointments)
    
    with col2:
        completed_rate = len(appointments_df[appointments_df['status'] == 'مكتمل']) / total_appointments * 100
        st.metric("✅ معدل الإكمال", f"{completed_rate:.1f}%")
    
    with col3:
        avg_cost = appointments_df['total_cost'].mean()
        st.metric("💰 متوسط التكلفة", format_currency(avg_cost))
    
    with col4:
        total_revenue = appointments_df['total_cost'].sum()
        st.metric("💸 إجمالي الإيرادات", format_currency(total_revenue))

def show_appointments_analysis(appointments_df):
    """عرض تحليل المواعيد"""
    import plotly.express as px
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 توزيع المواعيد حسب الحالة")
        status_counts = appointments_df['status'].value_counts()
        
        fig1 = px.pie(values=status_counts.values, names=status_counts.index,
                     title="توزيع حالات المواعيد")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("📊 المواعيد اليومية")
        daily_appointments = appointments_df.groupby('appointment_date').size().reset_index(name='count')
        
        fig2 = px.line(daily_appointments, x='appointment_date', y='count',
                      title="عدد المواعيد اليومية")
        st.plotly_chart(fig2, use_container_width=True)

def show_doctors_appointments_report(appointments_df):
    """تقرير مواعيد الأطباء"""
    st.subheader("👨‍⚕️ تقرير الأطباء")
    
    doctor_stats = appointments_df.groupby('doctor_name').agg({
        'id': 'count',
        'total_cost': ['sum', 'mean']
    }).round(2)
    
    doctor_stats.columns = ['عدد المواعيد', 'إجمالي الإيرادات', 'متوسط قيمة الموعد']
    doctor_stats = doctor_stats.reset_index()
    doctor_stats.columns = ['اسم الطبيب', 'عدد المواعيد', 'إجمالي الإيرادات', 'متوسط قيمة الموعد']
    
    st.dataframe(
        doctor_stats,
        column_config={
            'إجمالي الإيرادات': st.column_config.NumberColumn(format="%.2f ج.م"),
            'متوسط قيمة الموعد': st.column_config.NumberColumn(format="%.2f ج.م")
        },
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    show_appointments()
