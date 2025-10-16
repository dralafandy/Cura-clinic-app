import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message, 
    format_date_arabic, get_date_range_options, filter_dataframe_by_date
)

def show_payments():
    st.title("💳 إدارة المدفوعات")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات المدفوعات")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المدفوعات", "تسجيل دفعة جديدة", "تقارير الدفع", "المدفوعات المعلقة"]
    )
    
    if action == "عرض المدفوعات":
        show_payments_list()
    elif action == "تسجيل دفعة جديدة":
        add_new_payment()
    elif action == "تقارير الدفع":
        payments_reports()
    elif action == "المدفوعات المعلقة":
        pending_payments()

def show_payments_list():
    """عرض قائمة المدفوعات"""
    st.subheader("📋 قائمة المدفوعات")
    
    try:
        payments_df = crud.get_all_payments()
        
        if payments_df.empty:
            st.info("لا توجد مدفوعات مسجلة")
            return
        
        # فلاتر البحث والتصفية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # فلترة حسب التاريخ
            date_ranges = get_date_range_options()
            selected_range = st.selectbox("فترة زمنية", list(date_ranges.keys()))
            start_date, end_date = date_ranges[selected_range]
        
        with col2:
            # فلترة حسب طريقة الدفع
            payment_methods = ["الكل"] + list(payments_df['payment_method'].unique())
            selected_method = st.selectbox("طريقة الدفع", payment_methods)
        
        with col3:
            # فلترة حسب حالة الدفع
            payment_statuses = ["الكل"] + list(payments_df['status'].unique())
            selected_status = st.selectbox("حالة الدفع", payment_statuses)
        
        # تطبيق الفلاتر
        filtered_df = apply_payment_filters(payments_df, start_date, end_date, selected_method, selected_status)
        
        if filtered_df.empty:
            st.info("لا توجد مدفوعات تطابق المعايير المحددة")
            return
        
        # عرض الإحصائيات السريعة
        show_payments_summary(filtered_df)
        
        # عرض البيانات في جدول
        display_payments_table(filtered_df)
        
        # أزرار العمليات
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 تصدير إلى Excel"):
                export_payments_data(filtered_df)
        
        with col2:
            if st.button("📈 تحليل المدفوعات"):
                analyze_payments(filtered_df)
        
        with col3:
            if st.button("🔄 تحديث البيانات"):
                st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل المدفوعات: {str(e)}")

def add_new_payment():
    """تسجيل دفعة جديدة"""
    st.subheader("➕ تسجيل دفعة جديدة")
    
    try:
        # التحقق من وجود مرضى ومواعيد
        patients_df = crud.get_all_patients()
        appointments_df = crud.get_all_appointments()
        
        if patients_df.empty:
            st.error("يجب إضافة مرضى أولاً")
            return
        
        # خيار الدفع: مرتبط بموعد أو مستقل
        payment_type = st.radio(
            "نوع الدفعة",
            ["دفعة مرتبطة بموعد", "دفعة مستقلة"],
            horizontal=True
        )
        
        with st.form("add_payment_form"):
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
                
                # عرض معلومات المريض
                if selected_patient_id:
                    patient_info = patients_df[patients_df['id'] == selected_patient_id].iloc[0]
                    st.info(f"""
                    **📋 معلومات المريض:**
                    - **الاسم:** {patient_info['name']}
                    - **الهاتف:** {patient_info['phone'] or 'غير محدد'}
                    """)
                
                # اختيار الموعد (إذا كانت الدفعة مرتبطة بموعد)
                selected_appointment_id = None
                if payment_type == "دفعة مرتبطة بموعد" and not appointments_df.empty:
                    # فلترة المواعيد للمريض المحدد
                    patient_appointments = appointments_df[
                        appointments_df['patient_name'] == patient_info['name']
                    ]
                    
                    if not patient_appointments.empty:
                        appointment_options = {
                            row['id']: f"{row['treatment_name']} - {format_date_arabic(row['appointment_date'])} - {format_currency(row['total_cost'])}"
                            for _, row in patient_appointments.iterrows()
                        }
                        
                        selected_appointment_id = st.selectbox(
                            "اختر الموعد",
                            options=list(appointment_options.keys()),
                            format_func=lambda x: appointment_options[x]
                        )
                    else:
                        st.warning("لا توجد مواعيد لهذا المريض")
            
            with col2:
                st.subheader("💰 تفاصيل الدفعة")
                
                amount = st.number_input(
                    "مبلغ الدفعة (ج.م) *",
                    min_value=0.0,
                    value=0.0,
                    step=50.0
                )
                
                # إذا كان هناك موعد محدد، اقتراح مبلغ العلاج
                if selected_appointment_id and not appointments_df.empty:
                    appointment_info = appointments_df[appointments_df['id'] == selected_appointment_id].iloc[0]
                    suggested_amount = appointment_info['total_cost']
                    
                    if st.checkbox(f"استخدام مبلغ العلاج ({format_currency(suggested_amount)})"):
                        amount = suggested_amount
                        st.rerun()
                
                payment_method = st.selectbox(
                    "طريقة الدفع *",
                    ["نقداً", "بطاقة ائتمان", "بطاقة خصم", "تحويل بنكي", "شيك", "قسط"]
                )
                
                payment_date = st.date_input(
                    "تاريخ الدفع *",
                    value=date.today(),
                    max_value=date.today()
                )
                
                payment_status = st.selectbox(
                    "حالة الدفع",
                    ["مكتمل", "معلق", "مرفوض", "قيد المراجعة"]
                )
            
            # معلومات إضافية
            st.subheader("📝 معلومات إضافية")
            
            col3, col4 = st.columns(2)
            
            with col3:
                receipt_number = st.text_input(
                    "رقم الإيصال",
                    placeholder="سيتم إنشاؤه تلقائياً إذا تُرك فارغاً"
                )
                
                discount_amount = st.number_input(
                    "مبلغ الخصم (ج.م)",
                    min_value=0.0,
                    value=0.0,
                    step=10.0
                )
            
            with col4:
                tax_amount = st.number_input(
                    "الضريبة المضافة (ج.م)",
                    min_value=0.0,
                    value=0.0,
                    step=5.0
                )
                
                # المبلغ النهائي
                final_amount = amount - discount_amount + tax_amount
                st.metric("💸 المبلغ النهائي", format_currency(final_amount))
            
            notes = st.text_area(
                "ملاحظات",
                placeholder="أي ملاحظات خاصة بالدفعة..."
            )
            
            # معلومات الدفع بالتقسيط
            if payment_method == "قسط":
                with st.expander("📊 تفاصيل التقسيط"):
                    col5, col6 = st.columns(2)
                    
                    with col5:
                        installments_count = st.number_input(
                            "عدد الأقساط",
                            min_value=2,
                            max_value=24,
                            value=3
                        )
                    
                    with col6:
                        installment_amount = final_amount / installments_count
                        st.metric("💰 قيمة القسط", format_currency(installment_amount))
                    
                    first_installment_date = st.date_input(
                        "تاريخ القسط الأول",
                        value=date.today()
                    )
            
            submitted = st.form_submit_button("💾 حفظ الدفعة", use_container_width=True)
        
        if submitted:
            # التحقق من صحة البيانات
            if not selected_patient_id:
                show_error_message("يجب اختيار مريض")
                return
            
            if final_amount <= 0:
                show_error_message("مبلغ الدفعة يجب أن يكون أكبر من صفر")
                return
            
            try:
                # إنشاء رقم إيصال إذا لم يتم إدخاله
                if not receipt_number:
                    receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # حفظ الدفعة الرئيسية
                payment_id = crud.create_payment(
                    appointment_id=selected_appointment_id,
                    patient_id=selected_patient_id,
                    amount=final_amount,
                    payment_method=payment_method,
                    payment_date=payment_date,
                    notes=f"{notes}\nرقم الإيصال: {receipt_number}"
                )
                
                # إذا كانت الدفعة بالتقسيط، إنشاء الأقساط
                if payment_method == "قسط" and 'installments_count' in locals():
                    create_installment_payments(
                        patient_id=selected_patient_id,
                        total_amount=final_amount,
                        installments_count=installments_count,
                        first_date=first_installment_date,
                        parent_payment_id=payment_id
                    )
                
                show_success_message(f"تم تسجيل الدفعة بنجاح (المعرف: {payment_id})")
                
                # عرض ملخص الدفعة
                display_payment_receipt(payment_id, selected_patient_id, final_amount, 
                                      payment_method, payment_date, receipt_number)
                
                if st.button("🔄 تسجيل دفعة أخرى"):
                    st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ الدفعة: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل نموذج الدفع: {str(e)}")

def payments_reports():
    """تقارير المدفوعات"""
    st.subheader("📊 تقارير المدفوعات")
    
    try:
        payments_df = crud.get_all_payments()
        
        if payments_df.empty:
            st.info("لا توجد مدفوعات")
            return
        
        # فلترة التواريخ
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("إلى تاريخ", value=date.today())
        
        # فلترة البيانات
        filtered_payments = filter_dataframe_by_date(payments_df, 'payment_date', start_date, end_date)
        
        if filtered_payments.empty:
            st.info("لا توجد مدفوعات في هذه الفترة")
            return
        
        # التقارير المختلفة
        show_payment_analytics(filtered_payments)
        show_payment_methods_analysis(filtered_payments)
        show_daily_revenue_trend(filtered_payments)
        show_top_paying_patients(filtered_payments)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل التقارير: {str(e)}")

def pending_payments():
    """المدفوعات المعلقة"""
    st.subheader("⏳ المدفوعات المعلقة والمتأخرة")
    
    try:
        # هنا يمكن إضافة منطق للمدفوعات المعلقة والأقساط المتأخرة
        st.info("سيتم إضافة وظيفة متابعة المدفوعات المعلقة والأقساط المتأخرة قريباً")
        
        # عرض المواعيد غير المدفوعة
        appointments_df = crud.get_all_appointments()
        payments_df = crud.get_all_payments()
        
        if not appointments_df.empty:
            # المواعيد المكتملة بدون دفع
            unpaid_appointments = get_unpaid_appointments(appointments_df, payments_df)
            
            if not unpaid_appointments.empty:
                st.warning(f"🚨 يوجد {len(unpaid_appointments)} موعد مكتمل بدون دفع")
                
                st.dataframe(
                    unpaid_appointments[['patient_name', 'doctor_name', 'treatment_name', 
                                       'appointment_date', 'total_cost']],
                    column_config={
                        'patient_name': 'اسم المريض',
                        'doctor_name': 'اسم الطبيب',
                        'treatment_name': 'العلاج',
                        'appointment_date': 'التاريخ',
                        'total_cost': st.column_config.NumberColumn(
                            'المبلغ المستحق',
                            format="%.2f ج.م"
                        )
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                total_unpaid = unpaid_appointments['total_cost'].sum()
                st.error(f"💰 إجمالي المبالغ المستحقة: {format_currency(total_unpaid)}")
            else:
                st.success("✅ جميع المواعيد المكتملة مدفوعة")
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل المدفوعات المعلقة: {str(e)}")

# الدوال المساعدة

def apply_payment_filters(payments_df, start_date, end_date, method_filter, status_filter):
    """تطبيق فلاتر المدفوعات"""
    filtered_df = filter_dataframe_by_date(payments_df, 'payment_date', start_date, end_date)
    
    # فلترة حسب طريقة الدفع
    if method_filter != "الكل":
        filtered_df = filtered_df[filtered_df['payment_method'] == method_filter]
    
    # فلترة حسب الحالة
    if status_filter != "الكل":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    return filtered_df

def show_payments_summary(payments_df):
    """عرض ملخص المدفوعات"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_payments = len(payments_df)
        st.metric("📋 إجمالي المدفوعات", total_payments)
    
    with col2:
        total_amount = payments_df['amount'].sum()
        st.metric("💰 إجمالي المبالغ", format_currency(total_amount))
    
    with col3:
        avg_payment = payments_df['amount'].mean()
        st.metric("📊 متوسط الدفعة", format_currency(avg_payment))
    
    with col4:
        completed_payments = len(payments_df[payments_df['status'] == 'مكتمل'])
        completion_rate = (completed_payments / total_payments * 100) if total_payments > 0 else 0
        st.metric("✅ معدل الإكمال", f"{completion_rate:.1f}%")

def display_payments_table(payments_df):
    """عرض جدول المدفوعات"""
    st.subheader("📋 تفاصيل المدفوعات")
    
    st.dataframe(
        payments_df[['patient_name', 'amount', 'payment_method', 'payment_date', 'status', 'notes']],
        column_config={
            'patient_name': 'اسم المريض',
            'amount': st.column_config.NumberColumn(
                'المبلغ',
                format="%.2f ج.م"
            ),
            'payment_method': 'طريقة الدفع',
            'payment_date': 'تاريخ الدفع',
            'status': 'الحالة',
            'notes': 'ملاحظات'
        },
        use_container_width=True,
        hide_index=True
    )

def create_installment_payments(patient_id, total_amount, installments_count, first_date, parent_payment_id):
    """إنشاء دفعات التقسيط"""
    try:
        installment_amount = total_amount / installments_count
        
        for i in range(installments_count):
            # حساب تاريخ كل قسط (شهرياً)
            installment_date = first_date + timedelta(days=30 * i)
            
            # الحالة: القسط الأول مكتمل، الباقي معلق
            status = "مكتمل" if i == 0 else "معلق"
            
            crud.create_payment(
                appointment_id=None,
                patient_id=patient_id,
                amount=installment_amount,
                payment_method="قسط",
                payment_date=installment_date,
                notes=f"قسط {i+1} من {installments_count} - مرتبط بالدفعة {parent_payment_id}"
            )
        
        show_success_message(f"تم إنشاء {installments_count} قسط بنجاح")
        
    except Exception as e:
        show_error_message(f"خطأ في إنشاء الأقساط: {str(e)}")

def display_payment_receipt(payment_id, patient_id, amount, method, payment_date, receipt_number):
    """عرض إيصال الدفع"""
    st.success("✅ تم تسجيل الدفعة بنجاح!")
    
    # الحصول على معلومات المريض
    patient = crud.get_patient_by_id(patient_id)
    
    st.info(f"""
    **🧾 إيصال الدفع:**
    - **رقم الإيصال:** {receipt_number}
    - **رقم الدفعة:** {payment_id}
    - **المريض:** {patient[1]} - {patient[3]}
    - **المبلغ:** {format_currency(amount)}
    - **طريقة الدفع:** {method}
    - **التاريخ:** {format_date_arabic(payment_date)}
    """)
    
    # زر طباعة الإيصال
    if st.button("🖨️ طباعة الإيصال"):
        print_receipt(payment_id, patient[1], amount, method, payment_date, receipt_number)

def print_receipt(payment_id, patient_name, amount, method, payment_date, receipt_number):
    """طباعة الإيصال"""
    st.info("سيتم إضافة وظيفة الطباعة قريباً")

def show_payment_analytics(payments_df):
    """تحليل المدفوعات"""
    st.subheader("📊 تحليل المدفوعات")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_revenue = payments_df['amount'].sum()
        st.metric("💰 إجمالي الإيرادات", format_currency(total_revenue))
    
    with col2:
        daily_avg = payments_df.groupby('payment_date')['amount'].sum().mean()
        st.metric("📈 متوسط يومي", format_currency(daily_avg))
    
    with col3:
        max_payment = payments_df['amount'].max()
        st.metric("🏆 أعلى دفعة", format_currency(max_payment))

def show_payment_methods_analysis(payments_df):
    """تحليل طرق الدفع"""
    st.subheader("💳 تحليل طرق الدفع")
    
    import plotly.express as px
    
    method_stats = payments_df.groupby('payment_method').agg({
        'amount': ['sum', 'count']
    }).round(2)
    
    method_stats.columns = ['إجمالي المبلغ', 'عدد المدفوعات']
    method_stats = method_stats.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.pie(method_stats, values='إجمالي المبلغ', names='payment_method',
                     title="توزيع الإيرادات حسب طريقة الدفع")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(method_stats, x='payment_method', y='عدد المدفوعات',
                     title="عدد المدفوعات حسب الطريقة")
        st.plotly_chart(fig2, use_container_width=True)

def show_daily_revenue_trend(payments_df):
    """اتجاه الإيرادات اليومية"""
    st.subheader("📈 اتجاه الإيرادات اليومية")
    
    import plotly.express as px
    
    daily_revenue = payments_df.groupby('payment_date')['amount'].sum().reset_index()
    
    fig = px.line(daily_revenue, x='payment_date', y='amount',
                 title="الإيرادات اليومية",
                 labels={'payment_date': 'التاريخ', 'amount': 'المبلغ (ج.م)'})
    
    st.plotly_chart(fig, use_container_width=True)

def show_top_paying_patients(payments_df):
    """أكبر المرضى دفعاً"""
    st.subheader("🏆 أكبر المرضى دفعاً")
    
    top_patients = payments_df.groupby('patient_name')['amount'].sum().sort_values(ascending=False).head(10)
    
    st.dataframe(
        top_patients.reset_index(),
        column_config={
            'patient_name': 'اسم المريض',
            'amount': st.column_config.NumberColumn(
                'إجمالي المدفوعات',
                format="%.2f ج.م"
            )
        },
        use_container_width=True,
        hide_index=True
    )

def get_unpaid_appointments(appointments_df, payments_df):
    """الحصول على المواعيد غير المدفوعة"""
    # المواعيد المكتملة
    completed_appointments = appointments_df[appointments_df['status'] == 'مكتمل'].copy()
    
    if completed_appointments.empty:
        return pd.DataFrame()
    
    # الحصول على معرفات المواعيد المدفوعة
    paid_appointment_ids = payments_df['appointment_id'].dropna().unique() if not payments_df.empty else []
    
    # المواعيد غير المدفوعة
    unpaid_appointments = completed_appointments[
        ~completed_appointments['id'].isin(paid_appointment_ids)
    ]
    
    return unpaid_appointments

def export_payments_data(payments_df):
    """تصدير بيانات المدفوعات"""
    try:
        from utils.helpers import export_to_excel
        
        export_columns = {
            'id': 'المعرف',
            'patient_name': 'اسم المريض',
            'amount': 'المبلغ',
            'payment_method': 'طريقة الدفع',
            'payment_date': 'تاريخ الدفع',
            'status': 'الحالة',
            'notes': 'ملاحظات',
            'created_at': 'تاريخ التسجيل'
        }
        
        export_df = payments_df[list(export_columns.keys())].rename(columns=export_columns)
        excel_data = export_to_excel(export_df, "payments_report")
        
        st.download_button(
            label="📥 تحميل Excel",
            data=excel_data,
            file_name=f"payments_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        show_error_message(f"خطأ في التصدير: {str(e)}")

def analyze_payments(payments_df):
    """تحليل متقدم للمدفوعات"""
    st.subheader("🔍 تحليل متقدم للمدفوعات")
    
    # تحليل الاتجاهات الزمنية
    payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
    payments_df['month'] = payments_df['payment_date'].dt.month
    payments_df['weekday'] = payments_df['payment_date'].dt.dayofweek
    
    col1, col2 = st.columns(2)
    
    with col1:
        # أفضل أيام الأسبوع للدفع
        weekday_names = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']
        weekday_payments = payments_df.groupby('weekday')['amount'].sum()
        weekday_payments.index = [weekday_names[i] for i in weekday_payments.index]
        
        import plotly.express as px
        fig1 = px.bar(x=weekday_payments.index, y=weekday_payments.values,
                     title="الإيرادات حسب أيام الأسبوع")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # أفضل الشهور للدفع
        month_names = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                      'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        monthly_payments = payments_df.groupby('month')['amount'].sum()
        monthly_payments.index = [month_names[i-1] for i in monthly_payments.index]
        
        fig2 = px.bar(x=monthly_payments.index, y=monthly_payments.values,
                     title="الإيرادات حسب الشهور")
        st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    show_payments()