import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database.crud import CRUDOperations
from utils.helpers import (
    format_currency, show_success_message, show_error_message,
    format_date_arabic, get_appointment_time_slots, get_status_color, calculate_age
)
import calendar

crud = CRUDOperations()

def show_appointments():
    st.title("📅 إدارة المواعيد")
    
    st.sidebar.subheader("خيارات المواعيد")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المواعيد", "حجز موعد جديد", "تقويم المواعيد", "تقارير المواعيد"]
    )
    
    if action == "عرض المواعيد":
        show_appointments_list()
    elif action == "حجز موعد جديد":
        book_new_appointment()
    elif action == "تقويم المواعيد":
        appointments_calendar()
    elif action == "تقارير المواعيد":
        appointments_reports()

def show_appointments_list():
    """عرض قائمة المواعيد"""
    st.subheader("📋 قائمة المواعيد")
    
    try:
        appointments_df = crud.get_all_appointments()
        
        if appointments_df.empty:
            st.info("لا توجد مواعيد")
            return
        
        # فلاتر البحث والتصفية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_filter = st.selectbox(
                "فلترة حسب التاريخ",
                ["الكل", "اليوم", "غداً", "هذا الأسبوع", "هذا الشهر"]
            )
        
        with col2:
            doctors = ["الكل"] + list(appointments_df['doctor_name'].unique())
            selected_doctor = st.selectbox("فلترة حسب الطبيب", doctors)
        
        with col3:
            statuses = ["الكل"] + list(appointments_df['status'].unique())
            selected_status = st.selectbox("فلترة حسب الحالة", statuses)
        
        # تطبيق الفلاتر
        filtered_df = apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status)
        
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

def apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status):
    filtered_df = appointments_df.copy()
    filtered_df['appointment_date'] = pd.to_datetime(filtered_df['appointment_date']).dt.date
    today = date.today()
    if date_filter == "اليوم":
        filtered_df = filtered_df[filtered_df['appointment_date'] == today]
    elif date_filter == "غداً":
        filtered_df = filtered_df[filtered_df['appointment_date'] == today + timedelta(days=1)]
    elif date_filter == "هذا الأسبوع":
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        filtered_df = filtered_df[(filtered_df['appointment_date'] >= start_week) & (filtered_df['appointment_date'] <= end_week)]
    elif date_filter == "هذا الشهر":
        start_month = today.replace(day=1)
        end_month = (today.replace(month=today.month + 1, day=1) - timedelta(days=1)) if today.month < 12 else today.replace(month=12, day=31)
        filtered_df = filtered_df[(filtered_df['appointment_date'] >= start_month) & (filtered_df['appointment_date'] <= end_month)]
    if selected_doctor != "الكل":
        filtered_df = filtered_df[filtered_df['doctor_name'] == selected_doctor]
    if selected_status != "الكل":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    return filtered_df

def show_appointments_summary(filtered_df):
    col1, col2, col3 = st.columns(3)
    with col1:
        total_appointments = len(filtered_df)
        st.metric("📅 إجمالي المواعيد", total_appointments)
    with col2:
        completed = len(filtered_df[filtered_df['status'] == 'مكتمل'])
        st.metric("✅ المواعيد المكتملة", completed)
    with col3:
        total_revenue = filtered_df['total_cost'].sum()
        st.metric("💰 إجمالي الإيرادات", format_currency(total_revenue))

def display_appointments_cards(filtered_df):
    for _, appt in filtered_df.iterrows():
        with st.expander(f"موعد {appt['appointment_date']} - {appt['appointment_time']} مع {appt['patient_name']}"):
            doctor_share = appt['total_cost'] * (appt['commission_rate'] / 100)
            clinic_share = appt['total_cost'] - doctor_share
            st.info(f"""
            **تفاصيل الموعد:**
            - **الطبيب:** {appt['doctor_name']}
            - **العلاج:** {appt['treatment_name']}
            - **التكلفة:** {format_currency(appt['total_cost'])}
            - **حصة الطبيب ({appt['commission_rate']}%):** {format_currency(doctor_share)}
            - **حصة العيادة:** {format_currency(clinic_share)}
            - **الحالة:** {appt['status']}
            - **ملاحظات:** {appt['notes'] or 'لا يوجد'}
            """)
            col_a, col_b = st.columns(2)
            with col_a:
                new_status = st.selectbox(
                    "تغيير الحالة",
                    ['مجدول', 'مكتمل', 'ملغى', 'معلق'],
                    index=['مجدول', 'مكتمل', 'ملغى', 'معلق'].index(appt['status']),
                    key=f"status_{appt['id']}"
                )
                if st.button("💾 حفظ الحالة", key=f"save_{appt['id']}"):
                    crud.update_appointment_status(appt['id'], new_status)
                    show_success_message("تم تحديث حالة الموعد بنجاح")
                    st.rerun()
            with col_b:
                if st.button("🗑️ حذف", key=f"delete_{appt['id']}"):
                    crud.delete_appointment(appt['id'])
                    show_success_message("تم حذف الموعد بنجاح")
                    st.rerun()

def display_appointments_table(filtered_df):
    st.dataframe(
        filtered_df[['patient_name', 'doctor_name', 'treatment_name', 'appointment_date', 'appointment_time', 'status', 'total_cost', 'notes']],
        column_config={
            'patient_name': 'اسم المريض',
            'doctor_name': 'اسم الطبيب',
            'treatment_name': 'العلاج',
            'appointment_date': st.column_config.DateColumn('التاريخ'),
            'appointment_time': 'الوقت',
            'status': 'الحالة',
            'total_cost': st.column_config.NumberColumn('التكلفة', format="%.2f ج.م"),
            'notes': 'ملاحظات'
        },
        use_container_width=True,
        hide_index=True
    )

def book_new_appointment():
    """حجز موعد جديد"""
    st.subheader("➕ حجز موعد جديد")
    
    try:
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
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" 
                                 for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox(
                    "اختر المريض *",
                    options=list(patient_options.keys()),
                    format_func=lambda x: patient_options[x]
                )
                if selected_patient_id:
                    patient_info = patients_df[patients_df['id'] == selected_patient_id].iloc[0]
                    st.info(f"""
                    **📋 معلومات المريض:**
                    - **الاسم:** {patient_info['name']}
                    - **الهاتف:** {patient_info['phone'] or 'غير محدد'}
                    - **العمر:** {calculate_age(patient_info['date_of_birth'])} سنة
                    - **التاريخ الطبي:** {patient_info['medical_history'] or 'لا يوجد'}
                    """)
            
            with col2:
                st.subheader("👨‍⚕️ معلومات الطبيب والموعد")
                doctor_options = {row['id']: f"{row['name']} - {row['specialization']}" 
                                 for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox(
                    "اختر الطبيب *",
                    options=list(doctor_options.keys()),
                    format_func=lambda x: doctor_options[x]
                )
                if selected_doctor_id:
                    doctor_info = doctors_df[doctors_df['id'] == selected_doctor_id].iloc[0]
                    st.info(f"نسبة العمولة للطبيب: {doctor_info['commission_rate']}%")
                
                appointment_date = st.date_input("تاريخ الموعد *", min_value=date.today())
                
                if selected_doctor_id and appointment_date:
                    time_slots = get_appointment_time_slots(selected_doctor_id, appointment_date)
                    appointment_time = st.selectbox("اختر الوقت *", time_slots)
            
            st.subheader("💊 اختيار العلاج")
            treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])} (عمولة: {row['commission_rate']}%)" 
                               for _, row in treatments_df.iterrows()}
            selected_treatment_ids = st.multiselect(
                "اختر العلاجات *",
                options=list(treatment_options.keys()),
                format_func=lambda x: treatment_options[x]
            )
            
            status = st.selectbox("الحالة", ['مجدول', 'مكتمل', 'ملغى', 'معلق'], index=0)
            notes = st.text_area("ملاحظات")
            
            submitted = st.form_submit_button("📅 حجز الموعد")
            
            if submitted:
                if not (selected_patient_id and selected_doctor_id and appointment_date and appointment_time and selected_treatment_ids):
                    show_error_message("يجب ملء جميع الحقول المطلوبة")
                else:
                    total_cost = treatments_df[treatments_df['id'].isin(selected_treatment_ids)]['base_price'].sum()
                    commission_rate = treatments_df[treatments_df['id'].isin(selected_treatment_ids)]['commission_rate'].mean()
                    appointment_id = crud.create_appointment(
                        patient_id=selected_patient_id,
                        doctor_id=selected_doctor_id,
                        treatment_ids=selected_treatment_ids,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        status=status,
                        total_cost=total_cost,
                        commission_rate=commission_rate,
                        notes=notes
                    )
                    show_success_message(f"تم حجز الموعد رقم {appointment_id} بنجاح. التكلفة: {format_currency(total_cost)}")
                    st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في حجز الموعد: {str(e)}")

def appointments_calendar():
    st.subheader("🗓️ تقويم المواعيد")
    try:
        appointments_df = crud.get_all_appointments()
        if appointments_df.empty:
            st.info("لا توجد مواعيد لعرضها في التقويم")
            return
        
        year = st.number_input("السنة", value=date.today().year, min_value=2020, max_value=2030)
        month = st.number_input("الشهر", value=date.today().month, min_value=1, max_value=12)
        
        cal = calendar.monthcalendar(year, month)
        st.write(f"### {calendar.month_name[month]} {year}")
        
        days_header = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        st.write(" | ".join(days_header))
        
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.write("")
                    else:
                        current_date = date(year, month, day)
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
    except Exception as e:
        show_error_message(f"خطأ في عرض التقويم: {str(e)}")

def appointments_reports():
    st.subheader("📊 تقارير المواعيد")
    try:
        appointments_df = crud.get_all_appointments()
        if appointments_df.empty:
            st.info("لا توجد مواعيد لعرض التقارير")
            return
        
        show_appointments_statistics(appointments_df)
        st.divider()
        show_appointments_analysis(appointments_df)
        st.divider()
        show_doctors_appointments_report(appointments_df)
        
        if st.button("📊 تصدير إلى Excel"):
            from utils.helpers import export_to_excel
            export_columns = {
                'id': 'المعرف',
                'patient_name': 'اسم المريض',
                'doctor_name': 'اسم الطبيب',
                'treatment_name': 'العلاج',
                'appointment_date': 'تاريخ الموعد',
                'appointment_time': 'وقت الموعد',
                'status': 'الحالة',
                'total_cost': 'التكلفة (ج.م)',
                'notes': 'ملاحظات'
            }
            export_df = appointments_df[list(export_columns.keys())].rename(columns=export_columns)
            excel_data = export_to_excel(export_df, "appointments_report")
            st.download_button(
                label="📥 تحميل Excel",
                data=excel_data,
                file_name=f"appointments_report_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        show_error_message(f"خطأ في عرض التقارير: {str(e)}")

def show_appointments_statistics(appointments_df):
    st.subheader("📊 إحصائيات عامة")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_appointments = len(appointments_df)
        st.metric("📅 إجمالي المواعيد", total_appointments)
    with col2:
        completed_rate = len(appointments_df[appointments_df['status'] == 'مكتمل']) / total_appointments * 100 if total_appointments > 0 else 0
        st.metric("✅ معدل الإكمال", f"{completed_rate:.1f}%")
    with col3:
        avg_cost = appointments_df['total_cost'].mean() if not appointments_df.empty else 0
        st.metric("💰 متوسط التكلفة", format_currency(avg_cost))
    with col4:
        total_revenue = appointments_df['total_cost'].sum()
        st.metric("💸 إجمالي الإيرادات", format_currency(total_revenue))

def show_appointments_analysis(appointments_df):
    import plotly.express as px
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 توزيع المواعيد حسب الحالة")
        status_counts = appointments_df['status'].value_counts()
        fig1 = px.pie(values=status_counts.values, names=status_counts.index, title="توزيع حالات المواعيد")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader("📊 المواعيد اليومية")
        daily_appointments = appointments_df.groupby('appointment_date').size().reset_index(name='count')
        fig2 = px.line(daily_appointments, x='appointment_date', y='count', title="عدد المواعيد اليومية")
        st.plotly_chart(fig2, use_container_width=True)

def show_doctors_appointments_report(appointments_df):
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

def edit_appointment(appointment_id):
    st.subheader(f"✏️ تعديل الموعد رقم {appointment_id}")
    try:
        appointment = crud.get_appointment_by_id(appointment_id)
        if not appointment:
            show_error_message("الموعد غير موجود")
            return
        
        with st.form(f"edit_appointment_form_{appointment_id}"):
            col1, col2 = st.columns(2)
            with col1:
                patients_df = crud.get_all_patients()
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox(
                    "اختر المريض",
                    options=list(patient_options.keys()),
                    format_func=lambda x: patient_options[x],
                    index=list(patient_options.keys()).index(appointment['patient_id'])
                )
                doctors_df = crud.get_all_doctors()
                doctor_options = {row['id']: f"{row['name']} - {row['specialization']}" for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox(
                    "اختر الطبيب",
                    options=list(doctor_options.keys()),
                    format_func=lambda x: doctor_options[x],
                    index=list(doctor_options.keys()).index(appointment['doctor_id'])
                )
            with col2:
                appointment_date = st.date_input("تاريخ الموعد", value=datetime.strptime(appointment['appointment_date'], '%Y-%m-%d').date(), min_value=date.today())
                time_slots = get_appointment_time_slots(selected_doctor_id, appointment_date)
                appointment_time = st.selectbox("اختر الوقت", time_slots, index=time_slots.index(appointment['appointment_time']) if appointment['appointment_time'] in time_slots else 0)
                treatments_df = crud.get_all_treatments()
                treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])}" for _, row in treatments_df.iterrows()}
                selected_treatment_ids = st.multiselect(
                    "اختر العلاجات",
                    options=list(treatment_options.keys()),
                    format_func=lambda x: treatment_options[x],
                    default=appointment['treatment_ids']
                )
            status = st.selectbox("الحالة", ['مجدول', 'مكتمل', 'ملغى', 'معلق'], index=['مجدول', 'مكتمل', 'ملغى', 'معلق'].index(appointment['status']))
            notes = st.text_area("ملاحظات", value=appointment['notes'] or "")
            submitted = st.form_submit_button("💾 حفظ التعديلات")
            
            if submitted:
                total_cost = treatments_df[treatments_df['id'].isin(selected_treatment_ids)]['base_price'].sum()
                commission_rate = treatments_df[treatments_df['id'].isin(selected_treatment_ids)]['commission_rate'].mean()
                crud.update_appointment(
                    appointment_id=appointment_id,
                    patient_id=selected_patient_id,
                    doctor_id=selected_doctor_id,
                    treatment_ids=selected_treatment_ids,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status=status,
                    total_cost=total_cost,
                    commission_rate=commission_rate,
                    notes=notes
                )
                show_success_message("تم تعديل الموعد بنجاح")
                st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في تعديل الموعد: {str(e)}")

if __name__ == "__main__":
    show_appointments()
