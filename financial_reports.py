import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from database.crud import crud
from utils.helpers import format_currency, show_success_message, show_error_message

def show_financial_dashboard():
    st.title("📊 لوحة التحكم المالية")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات التقارير")
    report_type = st.sidebar.radio(
        "اختر التقرير",
        ["نظرة عامة", "تقارير الأطباء", "تقارير المرضى", "المخزون والمصروفات", "تقارير مفصلة"]
    )
    
    # فلترة التواريخ
    st.sidebar.subheader("فلترة التاريخ")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
    with col2:
        end_date = st.date_input("إلى تاريخ", value=date.today())
    
    if report_type == "نظرة عامة":
        show_financial_overview(start_date, end_date)
    elif report_type == "تقارير الأطباء":
        show_doctors_reports(start_date, end_date)
    elif report_type == "تقارير المرضى":
        show_patients_reports(start_date, end_date)
    elif report_type == "المخزون والمصروفات":
        show_inventory_expenses_reports(start_date, end_date)
    elif report_type == "تقارير مفصلة":
        show_detailed_reports(start_date, end_date)

def show_financial_overview(start_date, end_date):
    """عرض النظرة العامة المالية"""
    st.subheader("📈 النظرة العامة المالية")
    
    try:
        # الحصول على البيانات
        payments_df = crud.get_all_payments()
        expenses_df = crud.get_all_expenses()
        appointments_df = crud.get_all_appointments()
        
        # فلترة البيانات حسب التاريخ
        if not payments_df.empty:
            payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date']).dt.date
            payments_df = payments_df[(payments_df['payment_date'] >= start_date) & 
                                    (payments_df['payment_date'] <= end_date)]
        
        if not expenses_df.empty:
            expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date']).dt.date
            expenses_df = expenses_df[(expenses_df['expense_date'] >= start_date) & 
                                    (expenses_df['expense_date'] <= end_date)]
        
        if not appointments_df.empty:
            appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date']).dt.date
            appointments_df = appointments_df[(appointments_df['appointment_date'] >= start_date) & 
                                            (appointments_df['appointment_date'] <= end_date)]
        
        # عرض الإحصائيات الرئيسية
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_revenue = payments_df['amount'].sum() if not payments_df.empty else 0
            st.metric("💰 إجمالي الإيرادات", format_currency(total_revenue))
        
        with col2:
            total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
            st.metric("💸 إجمالي المصروفات", format_currency(total_expenses))
        
        with col3:
            net_profit = total_revenue - total_expenses
            st.metric("📊 صافي الربح", format_currency(net_profit))
        
        with col4:
            total_appointments = len(appointments_df) if not appointments_df.empty else 0
            st.metric("📅 عدد الجلسات", total_appointments)
        
        # مخطط الإيرادات vs المصروفات
        st.subheader("📊 الإيرادات vs المصروفات")
        show_revenue_vs_expenses_chart(payments_df, expenses_df, start_date, end_date)
        
        # أفضل الأطباء أداءً
        st.subheader("👨‍⚕️ أفضل الأطباء أداءً")
        show_top_doctors_performance(appointments_df, payments_df)
        
        # توزيع المصروفات
        st.subheader("🧾 توزيع المصروفات")
        show_expenses_breakdown(expenses_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل البيانات: {str(e)}")

def show_doctors_reports(start_date, end_date):
    """تقارير أداء الأطباء"""
    st.subheader("👨‍⚕️ تقارير أداء الأطباء")
    
    try:
        appointments_df = crud.get_all_appointments()
        payments_df = crud.get_all_payments()
        doctors_df = crud.get_all_doctors()
        
        if appointments_df.empty or doctors_df.empty:
            st.info("لا توجد بيانات كافية")
            return
        
        # فلترة البيانات
        appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date']).dt.date
        filtered_appointments = appointments_df[
            (appointments_df['appointment_date'] >= start_date) & 
            (appointments_df['appointment_date'] <= end_date)
        ]
        
        # إحصائيات الأطباء
        doctor_stats = filtered_appointments.groupby('doctor_name').agg({
            'id': 'count',
            'total_cost': ['sum', 'mean']
        }).round(2)
        
        if not doctor_stats.empty:
            doctor_stats.columns = ['عدد الجلسات', 'إجمالي الإيرادات', 'متوسط قيمة الجلسة']
            doctor_stats = doctor_stats.reset_index()
            doctor_stats.columns = ['اسم الطبيب', 'عدد الجلسات', 'إجمالي الإيرادات', 'متوسط قيمة الجلسة']
            
            # عرض جدول الأطباء
            st.dataframe(
                doctor_stats,
                column_config={
                    'إجمالي الإيرادات': st.column_config.NumberColumn(format="%.2f ج.م"),
                    'متوسط قيمة الجلسة': st.column_config.NumberColumn(format="%.2f ج.م")
                },
                use_container_width=True,
                hide_index=True
            )
            
            # مخطط أداء الأطباء
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.bar(doctor_stats, x='اسم الطبيب', y='إجمالي الإيرادات',
                             title="إيرادات الأطباء")
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.pie(doctor_stats, values='عدد الجلسات', names='اسم الطبيب',
                             title="توزيع الجلسات بين الأطباء")
                st.plotly_chart(fig2, use_container_width=True)
        
        # عمولات الأطباء
        st.subheader("💵 حسابات عمولات الأطباء")
        show_doctors_commissions(doctors_df, filtered_appointments)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل تقارير الأطباء: {str(e)}")

def show_doctors_commissions(doctors_df, appointments_df):
    """عرض حسابات عمولات الأطباء"""
    commissions_data = []
    
    for _, doctor in doctors_df.iterrows():
        doctor_appointments = appointments_df[appointments_df['doctor_name'] == doctor['name']]
        
        if not doctor_appointments.empty:
            total_revenue = doctor_appointments['total_cost'].sum()
            commission_rate = doctor.get('commission_rate', 0) / 100
            commission_amount = total_revenue * commission_rate
            
            commissions_data.append({
                'الطبيب': doctor['name'],
                'التخصص': doctor['specialization'],
                'إجمالي الإيرادات': total_revenue,
                'نسبة العمولة': f"{doctor.get('commission_rate', 0)}%",
                'قيمة العمولة': commission_amount,
                'صافي الدخل': total_revenue - commission_amount
            })
    
    if commissions_data:
        commissions_df = pd.DataFrame(commissions_data)
        st.dataframe(
            commissions_df,
            column_config={
                'إجمالي الإيرادات': st.column_config.NumberColumn(format="%.2f ج.م"),
                'قيمة العمولة': st.column_config.NumberColumn(format="%.2f ج.م"),
                'صافي الدخل': st.column_config.NumberColumn(format="%.2f ج.م")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # تصدير البيانات
        csv = commissions_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 تحميل تقرير العمولات",
            data=csv,
            file_name=f"doctors_commissions_{date.today()}.csv",
            mime="text/csv"
        )

def show_patients_reports(start_date, end_date):
    """تقارير المرضى"""
    st.subheader("👥 تقارير المرضى")
    
    try:
        appointments_df = crud.get_all_appointments()
        payments_df = crud.get_all_payments()
        patients_df = crud.get_all_patients()
        
        if appointments_df.empty:
            st.info("لا توجد بيانات عن المرضى")
            return
        
        # فلترة البيانات
        appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date']).dt.date
        filtered_appointments = appointments_df[
            (appointments_df['appointment_date'] >= start_date) & 
            (appointments_df['appointment_date'] <= end_date)
        ]
        
        # إحصائيات المرضى
        patient_stats = filtered_appointments.groupby('patient_name').agg({
            'id': 'count',
            'total_cost': 'sum',
            'doctor_name': lambda x: ', '.join(x.unique())
        }).round(2)
        
        if not patient_stats.empty:
            patient_stats.columns = ['عدد الجلسات', 'إجمالي المصروفات', 'الأطباء']
            patient_stats = patient_stats.reset_index()
            patient_stats.columns = ['اسم المريض', 'عدد الجلسات', 'إجمالي المصروفات', 'الأطباء']
            
            # عرض جدول المرضى
            st.dataframe(
                patient_stats,
                column_config={
                    'إجمالي المصروفات': st.column_config.NumberColumn(format="%.2f ج.م")
                },
                use_container_width=True,
                hide_index=True
            )
        
        # أفضل العملاء
        st.subheader("⭐ أفضل العملاء")
        show_top_patients(patient_stats)
        
        # مدفوعات المرضى
        st.subheader("💳 حالة مدفوعات المرضى")
        show_patients_payments_status(payments_df, start_date, end_date)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل تقارير المرضى: {str(e)}")

def show_top_patients(patient_stats):
    """عرض أفضل العملاء"""
    if not patient_stats.empty:
        top_patients = patient_stats.nlargest(10, 'إجمالي المصروفات')
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(top_patients, x='اسم المريض', y='إجمالي المصروفات',
                         title="أعلى 10 عملاء من حيث الإنفاق")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.pie(top_patients, values='عدد الجلسات', names='اسم المريض',
                         title="توزيع جلسات أفضل العملاء")
            st.plotly_chart(fig2, use_container_width=True)

def show_patients_payments_status(payments_df, start_date, end_date):
    """عرض حالة مدفوعات المرضى"""
    if not payments_df.empty:
        payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date']).dt.date
        filtered_payments = payments_df[
            (payments_df['payment_date'] >= start_date) & 
            (payments_df['payment_date'] <= end_date)
        ]
        
        # توزيع طرق الدفع
        payment_methods = filtered_payments['payment_method'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.pie(values=payment_methods.values, names=payment_methods.index,
                         title="توزيع طرق الدفع")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            daily_payments = filtered_payments.groupby('payment_date')['amount'].sum().reset_index()
            fig2 = px.line(daily_payments, x='payment_date', y='amount',
                          title="المدفوعات اليومية")
            st.plotly_chart(fig2, use_container_width=True)

def show_inventory_expenses_reports(start_date, end_date):
    """تقارير المخزون والمصروفات"""
    st.subheader("📦 تقارير المخزون والمصروفات")
    
    try:
        inventory_df = crud.get_all_inventory()
        expenses_df = crud.get_all_expenses()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🛒 حالة المخزون")
            show_inventory_status(inventory_df)
        
        with col2:
            st.subheader("🧾 تحليل المصروفات")
            show_expenses_analysis(expenses_df, start_date, end_date)
        
        # تقرير المواد المنتهية الصلاحية
        st.subheader("⚠️ المواد المنتهية الصلاحية")
        show_expired_items(inventory_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل تقارير المخزون: {str(e)}")

def show_inventory_status(inventory_df):
    """عرض حالة المخزون"""
    if not inventory_df.empty:
        # العناصر قليلة المخزون
        low_stock = inventory_df[inventory_df['quantity'] <= inventory_df['min_stock_level']]
        
        if not low_stock.empty:
            st.warning(f"⚠️ يوجد {len(low_stock)} عنصر تحت مستوى المخزون الأدنى")
            
            for _, item in low_stock.iterrows():
                st.error(f"**{item['item_name']}**: {item['quantity']} متبقي (الحد الأدنى: {item['min_stock_level']})")
        else:
            st.success("✅ جميع العناصر فوق مستوى المخزون الأدنى")
        
        # قيمة المخزون الإجمالية
        total_inventory_value = (inventory_df['quantity'] * inventory_df['unit_price']).sum()
        st.metric("💰 قيمة المخزون الإجمالية", format_currency(total_inventory_value))
        
        # توزيع المخزون حسب الفئة
        category_value = inventory_df.groupby('category').apply(
            lambda x: (x['quantity'] * x['unit_price']).sum()
        ).reset_index(name='قيمة المخزون')
        
        if not category_value.empty:
            fig = px.pie(category_value, values='قيمة المخزون', names='category',
                        title="توزيع قيمة المخزون حسب الفئة")
            st.plotly_chart(fig, use_container_width=True)

def show_expenses_analysis(expenses_df, start_date, end_date):
    """تحليل المصروفات"""
    if not expenses_df.empty:
        expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date']).dt.date
        filtered_expenses = expenses_df[
            (expenses_df['expense_date'] >= start_date) & 
            (expenses_df['expense_date'] <= end_date)
        ]
        
        if not filtered_expenses.empty:
            # توزيع المصروفات حسب الفئة
            category_expenses = filtered_expenses.groupby('category')['amount'].sum().reset_index()
            
            fig = px.bar(category_expenses, x='category', y='amount',
                        title="توزيع المصروفات حسب الفئة")
            st.plotly_chart(fig, use_container_width=True)
            
            # أعلى المصروفات
            st.subheader("🔝 أعلى المصروفات")
            top_expenses = filtered_expenses.nlargest(5, 'amount')[['description', 'amount', 'expense_date']]
            st.dataframe(top_expenses, use_container_width=True)

def show_expired_items(inventory_df):
    """عرض المواد المنتهية الصلاحية"""
    if not inventory_df.empty and 'expiry_date' in inventory_df.columns:
        today = date.today()
        inventory_df['expiry_date'] = pd.to_datetime(inventory_df['expiry_date']).dt.date
        expired_items = inventory_df[inventory_df['expiry_date'] < today]
        expiring_soon = inventory_df[
            (inventory_df['expiry_date'] >= today) & 
            (inventory_df['expiry_date']_date'] <= <= today today + timedelta + timedelta(days=30))
        ]
        
(days=30))
        ]
        
        if        if not not expired_items.empty:
            st expired_items.empty:
            st.error(f.error(f"❌ يوجد"❌ يوجد {len(expired {len(expired_items)} عنصر منتهي_items)} عنصر منتهي الصل الصلاحية")
            forاحية")
            for _, item _, item in expired_items in expired_items.iter.iterrows():
                strows():
                st.error(f.error(f"**{item"**{item['item['item_name']}_name']}** -** - انتهى انتهى في: في: {item['exp {item['expiry_dateiry_date']}")
        
']}")
        
        if        if not expiring not expiring_soon_soon.empty:
            st.empty:
            st.warning(f"⚠️ يوجد.warning(f"⚠️ {len(expiring يوجد {len(expiring_soon)} عن_soon)} عنصر سصر سينتهينتهي خلال 30 يوم")
ي خلال 30 يوم")
            for            for _, item in _, item in expiring_ expiring_soon.iterrows():
soon.iterrows():
                               st.warning(f st.warning(f""**{**{itemitem['item_name']}['item_name']}** - ينتهي في** - ينتهي في: {item['expiry: {item['expiry_date']}")

def show_detailed_reports(start_date, end_date):
_date']}")

def show_detailed_reports(start_date, end_date):
    """تقارير مفصلة    """تقارير مفص"""
    st.subheaderلة"""
    st.subheader("📋("📋 تقارير مفصلة")
    
 تقارير مفصلة")
    
       tab1, tab tab1, tab22, tab3, tab, tab3, tab4 = st.tabs(["4 = st.tabs(["الإيراداتالإيرادات",", "المصروفات "المصروفات", "المخزون", "المخزون", "التصد", "التصدير"])
    
    with tabير"])
    
    with tab1:
        show1:
        show_detailed_revenue_detailed_revenue_report_report(start_date, end(start_date, end_date_date)
    
    with tab)
    
    with tab2:
       2:
        show_d show_detetailed_expailed_expenses_report(start_date, end_date)
    
enses_report(start_date, end_date)
    
    with tab3    with tab3:
        show_detailed_inventory_report:
        show_detailed_inventory_report()
    
   ()
    
    with tab4 with tab4:
        show_export_options(start_date:
        show_export_options(start_date, end_date, end_date)

def)

def show_detailed show_detailed_revenue_report(start_date, end_revenue_report(start_date, end_date):
    """_date):
    """تقرتقرير الإيراداتير الإيرادات المفصل"""
    payments_df المفصل"""
    payments_df = crud.get = crud.get_all_payments()
    appointments_df =_all_payments()
    appointments_df = cr crud.get_all_appud.get_all_appointmentsointments()
    
    if()
    
    if not payments not payments_df.empty:
       _df.empty:
        payments_df['payment_date'] payments_df['payment_date'] = pd.to_datetime(p = pd.to_datetime(payments_dfayments_df['payment_date['payment_date']).dt']).dt.date
.date
               filtered_payments filtered_payments = payments_df[
            (pay = payments_df[
            (paymentsments_df['payment_date_df['payment_date'] >= start_date'] >= start_date) &) & 
 
            (payments_df            (payments_df['payment['payment_date']_date'] <= end_date)
 <= end_date)
        ]
        ]
        
        st.dataframe(filtered_payments, use_container_width=True)
        
        # إح        
        st.dataframe(filtered_payments, use_container_width=True)
        
        # إحصائياتصائيات الإير الإيرادات
ادات
        revenue_stats        revenue_stats = filtered_payments.groupby('payment_method').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        if not revenue_stats.empty:
            st.subheader("إحصائيات الإيرادات حسب طريقة الدفع")
            st.dataframe(revenue_stats, use_container_width=True)

def show_detailed_expenses_report(start_date, end_date):
    """تقرير المصروفات المفصل"""
    expenses_df = crud.get_all_expenses()
    
    if not expenses_df.empty:
        expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date']).dt.date
        filtered_expenses = expenses_df = filtered_payments.groupby('payment_method').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        if not revenue_stats.empty:
            st.subheader("إحصائيات الإيرادات حسب طريقة الدفع")
            st.dataframe(revenue_stats, use_container_width=True)

def show_detailed_expenses_report(start_date, end_date):
    """تقرير المصروفات المفصل"""
    expenses_df = crud.get_all_expenses()
    
    if not expenses_df.empty:
        expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date']).dt.date
        filtered_expenses = expenses_df[
           [
            (expenses_df (expenses_df['exp['expense_date'] >=ense_date'] >= start start_date) &_date) & 
            
            (expenses_df (expenses_df['exp['expense_date'] <= end_date)
        ]
        
        st.dataframe(filtered_expenses, useense_date'] <= end_date)
        ]
        
        st.dataframe(filtered_expenses_container_width=True)

, use_container_width=True)

def show_detailed_indef show_detailed_inventory_report():
    """تventory_report():
    """قرير المخزتقرير المخزون المفصل"""
    inventoryون المفصل"""
    inventory_df = crud.get_df = crud.get_all_inventory()
    
    if not inventory_df.empty:
        st.dataframe(inventory_df, use_container_width=True)

def show_export_options(start_date, end_date):
    """خيارات تصدير التقارير"""
    st.subheader("📤 تصدير التقارير")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 تصدير تقرير الإيرادات"):
            export_revenue_report(start_date, end_date)
    
    with col2:
        if st.button("📥 تصدير تقرير المصروفات"):
            export_expenses_report(start_date, end_date)
    
   _all_inventory()
    
    if not inventory_df.empty:
        st.dataframe(inventory_df, use_container_width=True)

def show_export_options(start_date, end_date):
    """خيارات تصدير التقارير"""
    st.subheader("📤 تصدير التقارير")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 تصدير تقرير الإيرادات"):
            export_revenue_report(start_date, end_date)
    
    with col2:
        if st.button("📥 تصدير تقرير المصروفات"):
            export_expenses_report with col3:
        if(start_date, end_date)
    
    with col3:
        if st.button("📥 تص st.button("دير تقرير📥 تصدير تقرير المخزون"):
            المخزون"):
            export_inventory_report()

 export_inventory_report()

defdef export_revenue_report export_revenue_report(start_date(start_date, end_date):
, end_date):
    """تصدير    """تصدير تق تقرير الإيررير الإيرادات"""
ادات"""
    payments_df = crud.get_all    payments_df = crud.get_all_payments()
    
    if not payments_df.empty:
       _payments()
    
    if not payments_df.empty:
        payments payments_df['payment_df['payment_date']_date'] = pd.to_datetime(payments_df['payment_date']).dt.date
        filtered_payments = payments_df[
            ( = pd.to_datetime(payments_df['payment_date']).dt.date
        filtered_payments = payments_df[
            (payments_df['paymentpayments_df['payment_date'] >=_date'] >= start_date start_date) &) & 
            (pay 
            (payments_dfments_df['payment['payment_date'] <=_date'] <= end_date)
 end_date)
        ]
        ]
        
        csv =        
        csv = filtered_p filtered_payments.to_csvayments.to_csv(index=False,(index=False, encoding=' encoding='utf-utf-8-s8-sig')
        stig')
        st.download_button(
.download_button(
            label            label="="📥 تحميل📥 تحميل تقر تقرير الإير الإيرادات",
يرادات",
            data=c            data=csv,
sv,
            file_name            file_name=f"=f"revenue_reportrevenue_report_{date.t_{date.today()}.oday()}.csv",
csv",
            mime="            mime="texttext/csv"
       /csv"
        )

def )

def export_exp export_expenses_reportenses_report(start_date, end(start_date, end_date):
    """تصدير_date):
    """تصد تقرير المصروفير تقرير المصروفات"""
    expenses_dfات"""
    expenses_df = = crud.get_all_expenses()
    
    if crud.get_all_expenses()
    
    if not expenses_df.empty:
        not expenses_df.empty:
        expenses_df['exp expenses_df['expense_date'] = pd.toense_date'] = pd.to_datetime_datetime(expenses_df['expense(expenses_df['expense_date_date']).dt.date
       ']).dt.date
        filtered_expenses = filtered_expenses = expenses_df expenses_df[
            (expenses[
            (expenses_df['expense_date_df['expense_date'] >= start_date) &'] >= start_date) & 
            (expenses 
            (expenses_df_df['expense_date['expense_date'] <= end_date)
       '] <= end_date)
        ]
        
        csv ]
        
        csv = filtered_expenses = filtered_expenses.to_csv.to_csv(index=False, encoding='utf(index=False, encoding='utf-8-sig-8-sig')
       ')
        st.download_button st.download_button(
            label="📥(
            label="📥 تحميل تق تحميل تقررير المصروفات",
ير المصروفات",
            data=csv,
                       data=csv,
            file_name=f"exp file_name=f"expensesenses_report_{date.t_report_{date.today()}.csv",
           oday() mime="text}.csv",
            mime="text/csv"
        )

def/csv"
        )

def export_inventory_report():
    export_inventory_report():
    """تصدير """تصدير تقرير المخزون تقرير المخزون"""
    inventory_df"""
    inventory_df = = crud.get_all_in crud.get_all_inventory()
    
   ventory()
    
    if not inventory_df.empty:
 if not inventory_df.empty:
        csv = inventory_df.to        csv = inventory_df.to_csv(index=False, encoding_csv(index=False,='utf-8-s encoding='utf-8-sig')
        st.dig')
        st.downloadownload_button(
            label_button(
            label="📥 تحميل="📥 تحميل تقرير المخ تقرير المخزونزون",
            data=c",
            data=csv,
            file_name=f"inventory_report_{date.today()}.csvsv,
            file_name=f"inventory_report_{date.today()}.csv",
",
            mime="            mime="text/ctext/csv"
        )

sv"
        )

defdef show_revenue show_revenue_vs_vs_expenses_chart_expenses_chart(payments(payments_df, expenses_df_df, expenses_df, start, start_date,_date, end_date end_date):
    """ع):
    """عرض مخططرض مخطط الإيرادات vs الإيرادات vs المص المصروفاتروفات"""
   """
    # تجميع البيانات يوم # تجميع البيانات يومياًياً
    if not payments_df.empty:
        daily_revenue
    if not payments_df.empty:
        daily_revenue = payments_df.groupby('payment_date')['amount'].sum().reset_index()
        daily_revenue.columns = ['date', 'revenue']
    else:
        daily_revenue = pd.DataFrame(columns=['date', = payments_df.groupby('payment_date')['amount'].sum().reset_index()
        daily_revenue.columns = ['date', 'revenue']
    else:
        daily_revenue = pd.DataFrame(columns=['date', 'revenue'])
    
    'revenue'])
    
 if not expenses_df.empty:
    if not expenses_df.empty:
        daily_exp        daily_expenses =enses = expenses_df.groupby(' expenses_df.groupby('expense_date')['amountexpense_date')['amount'].sum().reset'].sum().reset_index()
        daily_expenses.columns_index()
        daily_expenses.columns = ['date', ' = ['date', 'expenses']
    elseexpenses']
    else:
:
        daily_expenses        daily_expenses = pd = pd.DataFrame(columns=['.DataFrame(columns=['date',date', 'exp 'expenses'])
enses'])
    
    # د    
    # دمج البياناتمج البيانات
    dates
    dates = pd = pd.date_range.date_range(start=start(start=start_date, end_date, end=end=end_date, freq='_date, freq='D')
D')
    comparison    comparison_df = pd_df = pd.DataFrame({'date.DataFrame({'date': dates': dates})
    
    comparison})
    
    comparison_df =_df = comparison_df comparison_df.merge(daily.merge(daily_revenue_revenue, on, on='date', how='date', how='left='left')
    comparison_df')
    comparison_df = comparison = comparison_df.merge_df.merge(daily(daily_expenses,_expenses, on=' on='date', how='date', how='left')
left')
    comparison    comparison_df_df = comparison_df.fill = comparison_df.fillna(na(0)
    
   0)
    
    # إن # إنشاء المخططشاء المخطط
    fig = go.Figure
    fig = go.Figure()
    
    fig.add_t()
    
    fig.add_trace(go.Scatterrace(go.Scatter(
(
        x=compar        x=comparisonison_df['date'],
       _df['date'],
        y=comparison y=comparison_df['_df['revenue'],
       revenue'],
        name=' name='الإالإيرادات',
        lineيرادات',
        line=dict(color='#2E8B57=dict(color='#2E8B57', width=3', width=3)
    ))
    
    fig)
    ))
    
    fig.add_trace(go.Sc.add_trace(goatter(
        x=.Scatter(
        xcomparison_df['date=comparison_df['date'],
        y=comparison'],
        y=compar_df['expenses'],
ison_df['expenses        name='المص'],
        name='المصروفات',
        lineروفات',
        line=dict(color='#DC=dict(color='#143C', width=DC143C', width=3)
    ))
3)
    ))
    
    fig.update_layout(
    
    fig.update_layout(
        title="الإيرادات        title="الإيرادات vs المصروفات",
        vs المصروفات",
        xaxis_title=" xaxis_title="التاريخ",
        yaxisالتاريخ",
        yaxis_title="_title="المبلغ (جالمبلغ (ج.م.م)",
        hovermode)",
        hovermode='x unified'
='x unified'
    )
    )
    
    st.plot    
    st.plotly_chly_chart(figart(fig,, use_container use_container_width=True)

if __name__ ==_width=True)

if __name__ == "__main "__main____":
":
    show_fin    show_financial_dancialashboard()
