import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta, time
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message, 
    calculate_age, get_appointment_time_slots, get_status_color
)

def show_appointments():
    st.title("📅 إدارة المواعيد")
    st.sidebar.subheader("خيارات المواعيد")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المواعيد", "حجز موعد جديد", "تقويم المواعيد", "تقارير المواعيد", "حسابات المواعيد"]
    )
    if action == "عرض المواعيد":
        show_appointments_list()
    elif action == "حجز موعد جديد":
        book_new_appointment()
    elif action == "تقويم المواعيد":
        appointments_calendar()
    elif action == "تقارير المواعيد":
        appointments_reports()
    elif action == "حسابات المواعيد":
        appointment_accounts()

def show_appointments_list():
    """عرض قائمة المواعيد"""
    st.subheader("📋 قائمة المواعيد")
    try:
        appointments_df = crud.get_all_appointments()
        if appointments_df.empty:
            st.info("لا توجد مواعيد")
            return
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
        filtered_df = apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status)
        if filtered_df.empty:
            st.info("لا توجد مواعيد تطابق المعايير المحددة")
            return
        show_appointments_summary(filtered_df)
        display_appointments_cards(filtered_df)
        st.divider()
        st.subheader("📊 جدول المواعيد التفصيلي")
        display_appointments_table(filtered_df)
    except Exception as e:
        show_error_message(f"خطأ في تحميل المواعيد: {str(e)}")

def apply_appointments_filters(appointments_df, date_filter, selected_doctor, selected_status):
    """تطبيق فلاتر على قائمة المواعيد"""
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
        end_month = (today.replace(month=today.month + 1, day=1) - timedelta(days=1))
        filtered_df = filtered_df[(filtered_df['appointment_date'] >= start_month) & (filtered_df['appointment_date'] <= end_month)]
    if selected_doctor != "الكل":
        filtered_df = filtered_df[filtered_df['doctor_name'] == selected_doctor]
    if selected_status != "الكل":
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    return filtered_df

def show_appointments_summary(filtered_df):
    """عرض ملخص المواعيد"""
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
    """عرض المواعيد كبطاقات"""
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
                if st.button("✏️ تعديل", key=f"edit_{appt['id']}"):
                    edit_appointment(appt['id'])
            with col_b:
                if st.button("🗑️ حذف", key=f"delete_{appt['id']}"):
                    delete_appointment(appt['id'])

def display_appointments_table(filtered_df):
    """عرض جدول المواعيد"""
    st.dataframe(
        filtered_df[['patient_name', 'doctor_name', 'treatment_name', 'appointment_date', 'appointment_time', 'status', 'total_cost', 'commission_rate', 'notes']],
        column_config={
            'patient_name': 'اسم المريض',
            'doctor_name': 'اسم الطبيب',
            'treatment_name': 'العلاج',
            'appointment_date': st.column_config.DateColumn('التاريخ'),
            'appointment_time': 'الوقت',
            'status': 'الحالة',
            'total_cost': st.column_config.NumberColumn('التكلفة', format="%.2f ج.م"),
            'commission_rate': st.column_config.NumberColumn('نسبة العمولة %', format="%.1f%%"),
            'notes': 'ملاحظات'
        },
        use_container_width=True,
        hide_index=True
    )

def book_new_appointment():
    """حجز موعد جديد مع عرض نسبة العمولة"""
    st.subheader("➕ حجز موعد جديد")
    try:
        patients_df = crud.get_all_patients()
        doctors_df = crud.get_all_doctors()
        treatments_df = crud.get_all_treatments()
        if patients_df.empty or doctors_df.empty or treatments_df.empty:
            st.error("يجب إضافة مرضى، أطباء، وعلا جات أولاً")
            return
        with st.form("book_appointment_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("👤 معلومات المريض")
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox(
                    "اختر المريض *",
                    options=list(patient_options.keys()),
                    format_func=lambda x: patient_options[x]
                )
                if selected_patient_id:
                    patient = patients_df[patients_df['id'] == selected_patient_id].iloc[0]
                    st.info(f"عمر المريض: {calculate_age(patient['date_of_birth'])} سنة")
            with col2:
                st.subheader("👨‍⚕️ معلومات الطبيب والموعد")
                doctor_options = {row['id']: row['name'] for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox(
                    "اختر الطبيب *",
                    options=list(doctor_options.keys()),
                    format_func=lambda x: doctor_options[x]
                )
                appointment_date = st.date_input("تاريخ الموعد *", min_value=date.today())
                available_slots = get_appointment_time_slots(selected_doctor_id, appointment_date)
                appointment_time = st.selectbox("الوقت المتاح *", available_slots)
            st.subheader("💊 العلاج")
            treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])} (عمولة: {row['commission_rate']}%)" for _, row in treatments_df.iterrows()}
            selected_treatment_id = st.selectbox(
                "اختر العلاج *",
                options=list(treatment_options.keys()),
                format_func=lambda x: treatment_options[x]
            )
            notes = st.text_area("ملاحظات")
            total_cost = treatments_df[treatments_df['id'] == selected_treatment_id]['base_price'].iloc[0] if selected_treatment_id else 0.0
            commission_rate = treatments_df[treatments_df['id'] == selected_treatment_id]['commission_rate'].iloc[0] if selected_treatment_id else 0.0
            clinic_share = total_cost * (1 - commission_rate / 100)
            doctor_share = total_cost * (commission_rate / 100)
            st.info(f"**التكلفة الإجمالية:** {format_currency(total_cost)} | **حصة الطبيب:** {format_currency(doctor_share)} | **حصة العيادة:** {format_currency(clinic_share)}")
            submitted = st.form_submit_button("📅 حجز الموعد")
            if submitted:
                if not (selected_patient_id and selected_doctor_id and selected_treatment_id and appointment_date and appointment_time):
                    show_error_message("يجب ملء جميع الحقول المطلوبة")
                else:
                    appointment_id = crud.create_appointment(
                        patient_id=selected_patient_id,
                        doctor_id=selected_doctor_id,
                        treatment_id=selected_treatment_id,
                        appointment_date=appointment_date,
                        appointment_time=appointment_time,
                        notes=notes,
                        total_cost=total_cost
                    )
                    show_success_message(f"تم حجز الموعد رقم {appointment_id} بنجاح. التكلفة: {format_currency(total_cost)}")
                    crud.create_payment(
                        appointment_id=appointment_id,
                        patient_id=selected_patient_id,
                        amount=0.0,
                        payment_method="معلق",
                        payment_date=appointment_date,
                        status="معلق"
                    )
                    st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في حجز الموعد: {str(e)}")

def appointments_calendar():
    """تقويم المواعيد"""
    st.subheader("🗓️ تقويم المواعيد")
    import calendar
    year = st.number_input("السنة", value=date.today().year, min_value=2000, max_value=2100)
    month = st.number_input("الشهر", value=date.today().month, min_value=1, max_value=12)
    cal = calendar.monthcalendar(year, month)
    st.write(f"### {calendar.month_name[month]} {year}")
    days_header = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
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

def appointments_reports():
    """تقارير المواعيد"""
    st.subheader("📊 تقارير المواعيد")
    appointments_df = crud.get_all_appointments()
    tab1, tab2, tab3 = st.tabs(["إحصائيات عامة", "تحليل حسب الطبيب", "تحليل حسب المريض"])
    with tab1:
        show_appointments_statistics(appointments_df)
    with tab2:
        show_doctors_appointments_report(appointments_df)
    with tab3:
        show_patients_appointments_report(appointments_df)

def show_appointments_statistics(appointments_df):
    """عرض إحصائيات المواعيد"""
    st.subheader("📊 إحصائيات عامة")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_appointments = len(appointments_df)
        st.metric("📅 إجمالي المواعيد", total_appointments)
    with col2:
        completed_rate = len(appointments_df[appointments_df['status'] == 'مكتمل']) / total_appointments * 100 if total_appointments > 0 else 0
        st.metric("✅ معدل الإكمال", f"{completed_rate:.1f}%")
    with col3:
        avg_cost = appointments_df['total_cost'].mean()
        st.metric("💰 متوسط التكلفة", format_currency(avg_cost))
    with col4:
        total_revenue = appointments_df['total_cost'].sum()
        st.metric("💸 إجمالي الإيرادات", format_currency(total_revenue))
    import plotly.express as px
    fig = px.pie(appointments_df['status'].value_counts(), names=appointments_df['status'].value_counts().index, values='count',
                 title="توزيع حالات المواعيد")
    st.plotly_chart(fig, use_container_width=True)

def show_doctors_appointments_report(appointments_df):
    """تقرير مواعيد الأطباء"""
    st.subheader("👨‍⚕️ تقرير الأطباء")
    doctor_stats = appointments_df.groupby('doctor_name').agg({
        'id': 'count',
        'total_cost': 'sum',
        'status': lambda x: (x == 'مكتمل').sum(),
        'commission_rate': 'mean'
    }).round(2)
    doctor_stats.columns = ['عدد المواعيد', 'إجمالي الإيرادات', 'مكتملة', 'متوسط نسبة العمولة']
    doctor_stats = doctor_stats.reset_index()
    doctor_stats.columns = ['اسم الطبيب', 'عدد المواعيد', 'إجمالي الإيرادات', 'مكتملة', 'متوسط نسبة العمولة']
    st.dataframe(
        doctor_stats,
        column_config={
            'إجمالي الإيرادات': st.column_config.NumberColumn(format="%.2f ج.م"),
            'متوسط نسبة العمولة': st.column_config.NumberColumn(format="%.1f%%")
        },
        use_container_width=True,
        hide_index=True
    )
    import plotly.express as px
    fig = px.bar(doctor_stats, x='اسم الطبيب', y='عدد المواعيد',
                 title="عدد المواعيد حسب الطبيب")
    st.plotly_chart(fig, use_container_width=True)

def show_patients_appointments_report(appointments_df):
    """تقرير مواعيد المرضى"""
    st.subheader("👥 تقرير المرضى")
    patient_stats = appointments_df.groupby('patient_name').agg({
        'id': 'count',
        'total_cost': 'sum',
        'status': lambda x: (x == 'مكتمل').sum()
    }).round(2)
    patient_stats.columns = ['عدد الزيارات', 'إجمالي التكاليف', 'مكتملة']
    patient_stats = patient_stats.reset_index()
    patient_stats.columns = ['اسم المريض', 'عدد الزيارات', 'إجمالي التكاليف', 'مكتملة']
    st.dataframe(
        patient_stats,
        column_config={
            'إجمالي التكاليف': st.column_config.NumberColumn(format="%.2f ج.م")
        },
        use_container_width=True,
        hide_index=True
    )
    import plotly.express as px
    fig = px.bar(patient_stats, x='اسم المريض', y='عدد الزيارات',
                 title="عدد الزيارات حسب المريض")
    st.plotly_chart(fig, use_container_width=True)

def appointment_accounts():
    """حسابات المواعيد"""
    st.subheader("💳 حسابات المواعيد")
    st.markdown("**تتبع التكاليف والمدفوعات للمواعيد، مرتبطة بالمرضى، الأطباء، والمدفوعات**")
    tab1, tab2 = st.tabs(["سجل الحسابات", "تقرير الفواتير غير المدفوعة"])
    with tab1:
        show_appointment_accounts_history()
    with tab2:
        show_unpaid_invoices_report()

def show_appointment_accounts_history():
    """سجل حسابات المواعيد"""
    appointments_df = crud.get_all_appointments()
    payments_df = crud.get_all_payments()
    if appointments_df.empty:
        st.info("لا توجد مواعيد لحساباتها")
        return
    accounts_data = []
    for _, appt in appointments_df.iterrows():
        related_payments = payments_df[payments_df['appointment_id'] == appt['id']]['amount'].sum()
        remaining = appt['total_cost'] - related_payments
        doctor_share = appt['total_cost'] * (appt['commission_rate'] / 100)
        clinic_share = appt['total_cost'] - doctor_share
        accounts_data.append({
            'التاريخ': appt['appointment_date'],
            'المريض': appt['patient_name'],
            'الطبيب': appt['doctor_name'],
            'العلاج': appt['treatment_name'],
            'التكلفة': appt['total_cost'],
            'حصة الطبيب': doctor_share,
            'حصة العيادة': clinic_share,
            'المدفوع': related_payments,
            'المتبقي': max(0, remaining),
            'الحالة': appt['status']
        })
    accounts_df = pd.DataFrame(accounts_data)
    st.dataframe(
        accounts_df,
        column_config={
            'التكلفة': st.column_config.NumberColumn(format="%.2f ج.م"),
            'حصة الطبيب': st.column_config.NumberColumn(format="%.2f ج.م"),
            'حصة العيادة': st.column_config.NumberColumn(format="%.2f ج.م"),
            'المدفوع': st.column_config.NumberColumn(format="%.2f ج.م"),
            'المتبقي': st.column_config.NumberColumn(format="%.2f ج.م")
        },
        use_container_width=True,
        hide_index=True
    )
    selected_appt_id = st.selectbox(
        "إضافة دفعة لموعد",
        options=appointments_df['id'].tolist(),
        format_func=lambda x: f"موعد {x} - {appointments_df[appointments_df['id']==x]['patient_name'].iloc[0]}"
    )
    if selected_appt_id:
        with st.form("add_payment_to_appt"):
            amount = st.number_input("المبلغ *", min_value=0.0)
            payment_date = st.date_input("تاريخ الدفع", value=date.today())
            method = st.selectbox("طريقة الدفع", ['نقداً', 'بطاقة', 'تحويل'])
            notes = st.text_area("ملاحظات")
            if st.form_submit_button("💳 تسجيل الدفعة"):
                appt = appointments_df[appointments_df['id'] == selected_appt_id].iloc[0]
                crud.create_payment(
                    appointment_id=selected_appt_id,
                    patient_id=appt['patient_id'],
                    amount=amount,
                    payment_method=method,
                    payment_date=payment_date,
                    status="مكتمل",
                    notes=notes
                )
                show_success_message(f"تم تسجيل دفعة بقيمة {format_currency(amount)} للموعد")
                st.rerun()

def show_unpaid_invoices_report():
    """تقرير الفواتير غير المدفوعة"""
    appointments_df = crud.get_all_appointments()
    payments_df = crud.get_all_payments()
    unpaid_data = []
    for _, appt in appointments_df.iterrows():
        related_payments = payments_df[payments_df['appointment_id'] == appt['id']]['amount'].sum()
        if related_payments < appt['total_cost']:
            remaining = appt['total_cost'] - related_payments
            doctor_share = appt['total_cost'] * (appt['commission_rate'] / 100)
            clinic_share = appt['total_cost'] - doctor_share
            unpaid_data.append({
                'الموعد ID': appt['id'],
                'المريض': appt['patient_name'],
                'الطبيب': appt['doctor_name'],
                'التاريخ': appt['appointment_date'],
                'التكلفة': appt['total_cost'],
                'حصة الطبيب': doctor_share,
                'حصة العيادة': clinic_share,
                'المدفوع': related_payments,
                'المتبقي': remaining
            })
    unpaid_df = pd.DataFrame(unpaid_data)
    if unpaid_df.empty:
        st.success("✅ جميع الفواتير مدفوعة")
        return
    st.dataframe(
        unpaid_df,
        column_config={
            'التكلفة': st.column_config.NumberColumn(format="%.2f ج.م"),
            'حصة الطبيب': st.column_config.NumberColumn(format="%.2f ج.م"),
            'حصة العيادة': st.column_config.NumberColumn(format="%.2f ج.م"),
            'المدفوع': st.column_config.NumberColumn(format="%.2f ج.م"),
            'المتبقي': st.column_config.NumberColumn(format="%.2f ج.م")
        },
        use_container_width=True,
        hide_index=True
    )
    total_unpaid = unpaid_df['المتبقي'].sum()
    st.metric("💰 إجمالي الفواتير غير المدفوعة", format_currency(total_unpaid))

def edit_appointment(appointment_id):
    """تعديل موعد"""
    st.subheader(f"✏️ تعديل الموعد رقم {appointment_id}")
    appt = crud.get_appointment_by_id(appointment_id)
    if appt:
        with st.form(f"edit_appointment_form_{appointment_id}"):
            patients_df = crud.get_all_patients()
            doctors_df = crud.get_all_doctors()
            treatments_df = crud.get_all_treatments()
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("👤 معلومات المريض")
                patient_options = {row['id']: f"{row['name']} - {row['phone']}" for _, row in patients_df.iterrows()}
                selected_patient_id = st.selectbox(
                    "اختر المريض *",
                    options=list(patient_options.keys()),
                    format_func=lambda x: patient_options[x],
                    index=patients_df[patients_df['id'] == appt[2]].index[0] if appt[2] in patient_options else 0
                )
            with col2:
                st.subheader("👨‍⚕️ معلومات الطبيب والموعد")
                doctor_options = {row['id']: row['name'] for _, row in doctors_df.iterrows()}
                selected_doctor_id = st.selectbox(
                    "اختر الطبيب *",
                    options=list(doctor_options.keys()),
                    format_func=lambda x: doctor_options[x],
                    index=doctors_df[doctors_df['id'] == appt[3]].index[0] if appt[3] in doctor_options else 0
                )
                appointment_date = st.date_input("تاريخ الموعد *", value=date.fromisoformat(appt[5]), min_value=date.today())
                available_slots = get_appointment_time_slots(selected_doctor_id, appointment_date)
                appointment_time = st.selectbox("الوقت المتاح *", available_slots, index=available_slots.index(appt[6]) if appt[6] in available_slots else 0)
            st.subheader("💊 العلاج")
            treatment_options = {row['id']: f"{row['name']} - {format_currency(row['base_price'])} (عمولة: {row['commission_rate']}%)" for _, row in treatments_df.iterrows()}
            selected_treatment_id = st.selectbox(
                "اختر العلاج *",
                options=list(treatment_options.keys()),
                format_func=lambda x: treatment_options[x],
                index=treatments_df[treatments_df['id'] == appt[4]].index[0] if appt[4] in treatment_options else 0
            )
            status = st.selectbox("الحالة", ['مجدول', 'مكتمل', 'ملغى'], index=['مجدول', 'مكتمل', 'ملغى'].index(appt[7]))
            notes = st.text_area("ملاحظات", value=appt[8] or "")
            total_cost = treatments_df[treatments_df['id'] == selected_treatment_id]['base_price'].iloc[0] if selected_treatment_id else appt[9]
            commission_rate = treatments_df[treatments_df['id'] == selected_treatment_id]['commission_rate'].iloc[0] if selected_treatment_id else 0.0
            clinic_share = total_cost * (1 - commission_rate / 100)
            doctor_share = total_cost * (commission_rate / 100)
            st.info(f"**التكلفة الإجمالية:** {format_currency(total_cost)} | **حصة الطبيب:** {format_currency(doctor_share)} | **حصة العيادة:** {format_currency(clinic_share)}")
            submitted = st.form_submit_button("💾 حفظ التعديلات")
            if submitted:
                crud.update_appointment(
                    appointment_id=appointment_id,
                    patient_id=selected_patient_id,
                    doctor_id=selected_doctor_id,
                    treatment_id=selected_treatment_id,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    status=status,
                    notes=notes,
                    total_cost=total_cost
                )
                show_success_message("تم تعديل الموعد بنجاح")
                st.rerun()

def delete_appointment(appointment_id):
    """حذف موعد"""
    crud.delete_appointment(appointment_id)
    show_success_message("تم حذف الموعد بنجاح")
    st.rerun()

if __name__ == "__main__":
    show_appointments()
