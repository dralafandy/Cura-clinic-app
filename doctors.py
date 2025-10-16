import streamlit as st
import pandas as pd
from datetime import date, datetime
from database.crud import crud
from utils.helpers import (
    validate_phone_number, validate_email, format_currency,
    show_success_message, show_error_message, format_date_arabic
)

def show_doctors():
    st.title("👨‍⚕️ إدارة الأطباء")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات الأطباء")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض الأطباء", "إضافة طبيب جديد", "أداء الأطباء", "رواتب الأطباء"]
    )
    
    if action == "عرض الأطباء":
        show_doctors_list()
    elif action == "إضافة طبيب جديد":
        add_doctor_form()
    elif action == "أداء الأطباء":
        doctors_performance()
    elif action == "رواتب الأطباء":
        doctors_salaries()

def show_doctors_list():
    """عرض قائمة الأطباء"""
    st.subheader("📋 قائمة الأطباء")
    
    try:
        doctors_df = crud.get_all_doctors()
        
        if doctors_df.empty:
            st.info("لا توجد بيانات أطباء")
            return
        
        # عرض البيانات في جدول قابل للتحرير
        edited_df = st.data_editor(
            doctors_df[['id', 'name', 'specialization', 'phone', 'email', 'salary', 'commission_rate']],
            column_config={
                'id': st.column_config.NumberColumn('المعرف', disabled=True),
                'name': st.column_config.TextColumn('الاسم', required=True),
                'specialization': st.column_config.SelectboxColumn(
                    'التخصص',
                    options=[
                        'طب الأسنان العام',
                        'تقويم الأسنان',
                        'جراحة الفم والوجه',
                        'طب أسنان الأطفال',
                        'علاج الجذور',
                        'تركيبات الأسنان',
                        'طب اللثة'
                    ]
                ),
                'phone': st.column_config.TextColumn('الهاتف'),
                'email': st.column_config.TextColumn('البريد الإلكتروني'),
                'salary': st.column_config.NumberColumn(
                    'الراتب الأساسي',
                    min_value=0,
                    format="%.2f ج.م"
                ),
                'commission_rate': st.column_config.NumberColumn(
                    'نسبة العمولة %',
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # أزرار العمليات
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 حفظ التعديلات"):
                save_doctors_changes(edited_df, doctors_df)
        
        with col2:
            selected_rows = st.multiselect(
                "اختر أطباء للحذف",
                options=doctors_df['id'].tolist(),
                format_func=lambda x: doctors_df[doctors_df['id']==x]['name'].iloc[0]
            )
            
            if st.button("🗑️ حذف المحدد") and selected_rows:
                delete_selected_doctors(selected_rows)
        
        with col3:
            if st.button("📊 تصدير إلى Excel"):
                export_doctors_data(doctors_df)
        
        # تفاصيل الطبيب
        st.divider()
        show_doctor_details(doctors_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل بيانات الأطباء: {str(e)}")

def add_doctor_form():
    """نموذج إضافة طبيب جديد"""
    st.subheader("➕ إضافة طبيب جديد")
    
    with st.form("add_doctor_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("الاسم الكامل *", placeholder="د. أحمد محمد")
            specialization = st.selectbox(
                "التخصص *",
                [
                    'طب الأسنان العام',
                    'تقويم الأسنان',
                    'جراحة الفم والوجه',
                    'طب أسنان الأطفال',
                    'علاج الجذور',
                    'تركيبات الأسنان',
                    'طب اللثة'
                ]
            )
            phone = st.text_input("رقم الهاتف", placeholder="01xxxxxxxxx")
            email = st.text_input("البريد الإلكتروني", placeholder="doctor@clinic.com")
        
        with col2:
            hire_date = st.date_input(
                "تاريخ التعيين",
                max_value=date.today(),
                value=date.today()
            )
            salary = st.number_input(
                "الراتب الأساسي (ج.م) *",
                min_value=0.0,
                value=15000.0,
                step=500.0
            )
            commission_rate = st.number_input(
                "نسبة العمولة (%)",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=0.5
            )
            address = st.text_area("العنوان", placeholder="أدخل العنوان كاملاً")
        
        submitted = st.form_submit_button("💾 حفظ الطبيب")
        
        if submitted:
            # التحقق من صحة البيانات
            errors = []
            
            if not name.strip():
                errors.append("الاسم مطلوب")
            
            if phone and not validate_phone_number(phone):
                errors.append("رقم الهاتف غير صحيح")
            
            if email and not validate_email(email):
                errors.append("البريد الإلكتروني غير صحيح")
            
            if salary <= 0:
                errors.append("الراتب يجب أن يكون أكبر من صفر")
            
            if errors:
                for error in errors:
                    show_error_message(error)
                return
            
            # حفظ الطبيب
            try:
                doctor_id = crud.create_doctor(
                    name=name.strip(),
                    specialization=specialization,
                    phone=phone.strip() if phone else None,
                    email=email.strip() if email else None,
                    address=address.strip() if address else None,
                    hire_date=hire_date,
                    salary=salary,
                    commission_rate=commission_rate
                )
                
                show_success_message(f"تم إضافة الطبيب {name} بنجاح (المعرف: {doctor_id})")
                st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ الطبيب: {str(e)}")

def doctors_performance():
    """تقرير أداء الأطباء"""
    st.subheader("📊 أداء الأطباء")
    
    try:
        # الحصول على بيانات المواعيد مع تفاصيل الأطباء
        appointments_df = crud.get_all_appointments()
        
        if appointments_df.empty:
            st.info("لا توجد بيانات مواعيد لعرض الأداء")
            return
        
        # فلترة حسب التاريخ
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("إلى تاريخ", value=date.today())
        
        # فلترة البيانات
        appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date']).dt.date
        filtered_appointments = appointments_df[
            (appointments_df['appointment_date'] >= start_date) & 
            (appointments_df['appointment_date'] <= end_date)
        ]
        
        if filtered_appointments.empty:
            st.info("لا توجد مواعيد في هذه الفترة")
            return
        
        # حساب إحصائيات الأداء لكل طبيب
        performance_stats = filtered_appointments.groupby('doctor_name').agg({
            'id': 'count',  # عدد المواعيد
            'total_cost': ['sum', 'mean']  # إجمالي ومتوسط التكلفة
        }).round(2)
        
        performance_stats.columns = ['عدد المواعيد', 'إجمالي الإيرادات', 'متوسط قيمة الموعد']
        performance_stats = performance_stats.reset_index()
        performance_stats.columns = ['اسم الطبيب', 'عدد المواعيد', 'إجمالي الإيرادات', 'متوسط قيمة الموعد']
        
        # حساب العمولات
        doctors_df = crud.get_all_doctors()
        doctor_commissions = {}
        
        for _, doctor in doctors_df.iterrows():
            doctor_revenue = performance_stats[
                performance_stats['اسم الطبيب'] == doctor['name']
            ]['إجمالي الإيرادات'].sum() if not performance_stats.empty else 0
            
            commission = doctor_revenue * (doctor['commission_rate'] / 100)
            doctor_commissions[doctor['name']] = commission
        
        performance_stats['العمولة المستحقة'] = performance_stats['اسم الطبيب'].map(doctor_commissions)
        
        # عرض الجدول
        st.dataframe(
            performance_stats,
            column_config={
                'إجمالي الإيرادات': st.column_config.NumberColumn(
                    'إجمالي الإيرادات',
                    format="%.2f ج.م"
                ),
                'متوسط قيمة الموعد': st.column_config.NumberColumn(
                    'متوسط قيمة الموعد',
                    format="%.2f ج.م"
                ),
                'العمولة المستحقة': st.column_config.NumberColumn(
                    'العمولة المستحقة',
                    format="%.2f ج.م"
                )
            },
            use_container_width=True,
            hide_index=True
        )
        
        # رسم بياني للأداء
        import plotly.express as px
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                performance_stats, 
                x='اسم الطبيب', 
                y='عدد المواعيد',
                title='عدد المواعيد لكل طبيب'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(
                performance_stats, 
                x='اسم الطبيب', 
                y='إجمالي الإيرادات',
                title='إجمالي الإيرادات لكل طبيب'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # أفضل أداء
        st.subheader("🏆 أفضل أداء")
        
        if not performance_stats.empty:
            best_revenue = performance_stats.loc[performance_stats['إجمالي الإيرادات'].idxmax()]
            best_appointments = performance_stats.loc[performance_stats['عدد المواعيد'].idxmax()]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"""
                **💰 أعلى إيرادات**
                - **الطبيب:** {best_revenue['اسم الطبيب']}
                - **الإيرادات:** {format_currency(best_revenue['إجمالي الإيرادات'])}
                - **العمولة:** {format_currency(best_revenue['العمولة المستحقة'])}
                """)
            
            with col2:
                st.success(f"""
                **📅 أكثر مواعيد**
                - **الطبيب:** {best_appointments['اسم الطبيب']}
                - **عدد المواعيد:** {best_appointments['عدد المواعيد']}
                - **متوسط القيمة:** {format_currency(best_appointments['متوسط قيمة الموعد'])}
                """)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل تقرير الأداء: {str(e)}")

def doctors_salaries():
    """حساب رواتب الأطباء"""
    st.subheader("💰 رواتب الأطباء")
    
    try:
        doctors_df = crud.get_all_doctors()
        
        if doctors_df.empty:
            st.info("لا توجد بيانات أطباء")
            return
        
        # فلترة حسب الشهر
        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox(
                "اختر الشهر",
                range(1, 13),
                index=datetime.now().month - 1,
                format_func=lambda x: [
                    'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                    'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
                ][x-1]
            )
        
        with col2:
            selected_year = st.selectbox(
                "اختر السنة",
                range(2020, 2030),
                index=datetime.now().year - 2020
            )
        
        # حساب الرواتب مع العمولات
        appointments_df = crud.get_all_appointments()
        
        salary_data = []
        
        for _, doctor in doctors_df.iterrows():
            # الراتب الأساسي
            base_salary = doctor['salary']
            
            # حساب العمولة من المواعيد في الشهر المحدد
            if not appointments_df.empty:
                doctor_appointments = appointments_df[
                    appointments_df['doctor_name'] == doctor['name']
                ]
                
                # فلترة حسب الشهر والسنة
                doctor_appointments['appointment_date'] = pd.to_datetime(doctor_appointments['appointment_date'])
                monthly_appointments = doctor_appointments[
                    (doctor_appointments['appointment_date'].dt.month == selected_month) &
                    (doctor_appointments['appointment_date'].dt.year == selected_year)
                ]
                
                monthly_revenue = monthly_appointments['total_cost'].sum()
                commission = monthly_revenue * (doctor['commission_rate'] / 100)
            else:
                monthly_revenue = 0
                commission = 0
            
            total_salary = base_salary + commission
            
            salary_data.append({
                'اسم الطبيب': doctor['name'],
                'التخصص': doctor['specialization'],
                'الراتب الأساسي': base_salary,
                'إيرادات الشهر': monthly_revenue,
                'نسبة العمولة': doctor['commission_rate'],
                'العمولة': commission,
                'إجمالي الراتب': total_salary
            })
        
        salary_df = pd.DataFrame(salary_data)
        
        # عرض الجدول
        st.dataframe(
            salary_df,
            column_config={
                'الراتب الأساسي': st.column_config.NumberColumn(
                    'الراتب الأساسي',
                    format="%.2f ج.م"
                ),
                'إيرادات الشهر': st.column_config.NumberColumn(
                    'إيرادات الشهر',
                    format="%.2f ج.م"
                ),
                'نسبة العمولة': st.column_config.NumberColumn(
                    'نسبة العمولة',
                    format="%.1f%%"
                ),
                'العمولة': st.column_config.NumberColumn(
                    'العمولة',
                    format="%.2f ج.م"
                ),
                'إجمالي الراتب': st.column_config.NumberColumn(
                    'إجمالي الراتب',
                    format="%.2f ج.م"
                )
            },
            use_container_width=True,
            hide_index=True
        )
        
        # ملخص الرواتب
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_base_salaries = salary_df['الراتب الأساسي'].sum()
            st.metric("💼 إجمالي الرواتب الأساسية", format_currency(total_base_salaries))
        
        with col2:
            total_commissions = salary_df['العمولة'].sum()
            st.metric("💰 إجمالي العمولات", format_currency(total_commissions))
        
        with col3:
            total_salaries = salary_df['إجمالي الراتب'].sum()
            st.metric("💸 إجمالي المرتبات", format_currency(total_salaries))
        
        # رسم بياني للرواتب
        import plotly.express as px
        
        fig = px.bar(
            salary_df, 
            x='اسم الطبيب', 
            y=['الراتب الأساسي', 'العمولة'],
            title=f'تفصيل رواتب الأطباء - {selected_month}/{selected_year}',
            barmode='stack'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # تصدير كشف الرواتب
        if st.button("📊 تصدير كشف الرواتب"):
            export_salary_report(salary_df, selected_month, selected_year)
        
    except Exception as e:
        show_error_message(f"خطأ في حساب الرواتب: {str(e)}")

def show_doctor_details(doctors_df):
    """عرض تفاصيل طبيب محدد"""
    st.subheader("👁️ تفاصيل الطبيب")
    
    doctor_names = {row['id']: row['name'] for _, row in doctors_df.iterrows()}
    selected_doctor_id = st.selectbox(
        "اختر طبيب لعرض التفاصيل",
        options=list(doctor_names.keys()),
        format_func=lambda x: doctor_names[x]
    )
    
    if selected_doctor_id:
        doctor = doctors_df[doctors_df['id'] == selected_doctor_id].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **👨‍⚕️ البيانات المهنية**
            - **الاسم:** {doctor['name']}
            - **التخصص:** {doctor['specialization']}
            - **تاريخ التعيين:** {format_date_arabic(doctor['hire_date'])}
            - **الراتب الأساسي:** {format_currency(doctor['salary'])}
            - **نسبة العمولة:** {doctor['commission_rate']}%
            """)
        
        with col2:
            st.info(f"""
            **📞 بيانات الاتصال**
            - **الهاتف:** {doctor['phone'] or 'غير محدد'}
            - **البريد:** {doctor['email'] or 'غير محدد'}
            - **العنوان:** {doctor['address'] or 'غير محدد'}
            - **تاريخ التسجيل:** {format_date_arabic(doctor['created_at'][:10])}
            """)

def save_doctors_changes(edited_df, original_df):
    """حفظ تعديلات الأطباء"""
    try:
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            
            # التحقق من وجود تغييرات
            if (row['name'] != original_row['name'] or 
                row['specialization'] != original_row['specialization'] or
                row['phone'] != original_row['phone'] or
                row['email'] != original_row['email'] or
                row['salary'] != original_row['salary'] or
                row['commission_rate'] != original_row['commission_rate']):
                
                crud.update_doctor(
                    doctor_id=row['id'],
                    name=row['name'],
                    specialization=row['specialization'],
                    phone=row['phone'],
                    email=row['email'],
                    address=original_row['address'],
                    salary=row['salary'],
                    commission_rate=row['commission_rate']
                )
        
        show_success_message("تم حفظ التعديلات بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def delete_selected_doctors(doctor_ids):
    """حذف الأطباء المحددين"""
    try:
        for doctor_id in doctor_ids:
            crud.delete_doctor(doctor_id)
        
        show_success_message(f"تم حذف {len(doctor_ids)} طبيب بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حذف الأطباء: {str(e)}")

def export_doctors_data(doctors_df):
    """تصدير بيانات الأطباء"""
    try:
        from utils.helpers import export_to_excel
        
        export_columns = {
            'id': 'المعرف',
            'name': 'الاسم',
            'specialization': 'التخصص',
            'phone': 'الهاتف',
            'email': 'البريد الإلكتروني',
            'address': 'العنوان',
            'hire_date': 'تاريخ التعيين',
            'salary': 'الراتب الأساسي',
            'commission_rate': 'نسبة العمولة',
            'created_at': 'تاريخ التسجيل'
        }
        
        export_df = doctors_df[list(export_columns.keys())].rename(columns=export_columns)
        excel_data = export_to_excel(export_df, "doctors_report")
        
        st.download_button(
            label="📥 تحميل Excel",
            data=excel_data,
            file_name=f"doctors_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        show_error_message(f"خطأ في التصدير: {str(e)}")

def export_salary_report(salary_df, month, year):
    """تصدير كشف الرواتب"""
    try:
        from utils.helpers import export_to_excel
        
        excel_data = export_to_excel(salary_df, f"salary_report_{month}_{year}")
        
        st.download_button(
            label="📥 تحميل كشف الرواتب",
            data=excel_data,
            file_name=f"salary_report_{month}_{year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        show_error_message(f"خطأ في تصدير كشف الرواتب: {str(e)}")

if __name__ == "__main__":
    show_doctors()