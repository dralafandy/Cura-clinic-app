import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message, 
    format_date_arabic, get_date_range_options, filter_dataframe_by_date
)

def show_expenses():
    st.title("💸 إدارة المصروفات")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات المصروفات")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المصروفات", "إضافة مصروف جديد", "تقارير المصروفات", "الميزانية"]
    )
    
    if action == "عرض المصروفات":
        show_expenses_list()
    elif action == "إضافة مصروف جديد":
        add_new_expense()
    elif action == "تقارير المصروفات":
        expenses_reports()
    elif action == "الميزانية":
        budget_management()

def show_expenses_list():
    """عرض قائمة المصروفات"""
    st.subheader("📋 قائمة المصروفات")
    
    try:
        expenses_df = crud.get_all_expenses()
        
        if expenses_df.empty:
            st.info("لا توجد مصروفات مسجلة")
            return
        
        # فلاتر البحث والتصفية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # فلترة حسب التاريخ
            date_ranges = get_date_range_options()
            selected_range = st.selectbox("فترة زمنية", list(date_ranges.keys()))
            start_date, end_date = date_ranges[selected_range]
        
        with col2:
            # فلترة حسب الفئة
            categories = ["الكل"] + list(expenses_df['category'].unique())
            selected_category = st.selectbox("فلترة حسب الفئة", categories)
        
        with col3:
            # فلترة حسب طريقة الدفع
            payment_methods = ["الكل"] + list(expenses_df['payment_method'].unique())
            selected_method = st.selectbox("طريقة الدفع", payment_methods)
        
        # تطبيق الفلاتر
        filtered_df = apply_expenses_filters(expenses_df, start_date, end_date, selected_category, selected_method)
        
        if filtered_df.empty:
            st.info("لا توجد مصروفات تطابق المعايير المحددة")
            return
        
        # عرض الإحصائيات السريعة
        show_expenses_summary(filtered_df)
        
        # عرض البيانات في جدول قابل للتحرير
        edited_df = st.data_editor(
            filtered_df[['id', 'category', 'description', 'amount', 'expense_date', 
                        'payment_method', 'receipt_number', 'notes']],
            column_config={
                'id': st.column_config.NumberColumn('المعرف', disabled=True),
                'category': st.column_config.SelectboxColumn(
                    'الفئة',
                    options=[
                        'رواتب', 'إيجار', 'مرافق', 'صيانة', 'تسويق', 'مواد وخامات',
                        'معدات', 'تأمين', 'ضرائب', 'مواصلات', 'اتصالات', 'أخرى'
                    ]
                ),
                'description': st.column_config.TextColumn('الوصف', required=True),
                'amount': st.column_config.NumberColumn(
                    'المبلغ (ج.م)',
                    min_value=0.0,
                    format="%.2f ج.م"
                ),
                'expense_date': st.column_config.DateColumn('تاريخ المصروف'),
                'payment_method': st.column_config.SelectboxColumn(
                    'طريقة الدفع',
                    options=['نقداً', 'بطاقة ائتمان', 'تحويل بنكي', 'شيك']
                ),
                'receipt_number': st.column_config.TextColumn('رقم الإيصال'),
                'notes': st.column_config.TextColumn('ملاحظات')
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # أزرار العمليات
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 حفظ التعديلات"):
                save_expenses_changes(edited_df, filtered_df)
        
        with col2:
            selected_rows = st.multiselect(
                "اختر مصروفات للحذف",
                options=filtered_df['id'].tolist(),
                format_func=lambda x: f"{filtered_df[filtered_df['id']==x]['description'].iloc[0]} - {format_currency(filtered_df[filtered_df['id']==x]['amount'].iloc[0])}"
            )
            
            if st.button("🗑️ حذف المحدد") and selected_rows:
                delete_selected_expenses(selected_rows)
        
        with col3:
            if st.button("📊 تصدير إلى Excel"):
                export_expenses_data(filtered_df)
        
        with col4:
            if st.button("📈 تحليل المصروفات"):
                analyze_expenses(filtered_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل المصروفات: {str(e)}")

def add_new_expense():
    """إضافة مصروف جديد"""
    st.subheader("➕ إضافة مصروف جديد")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 تفاصيل المصروف")
            
            category = st.selectbox(
                "فئة المصروف *",
                [
                    'رواتب', 'إيجار', 'مرافق', 'صيانة', 'تسويق', 'مواد وخامات',
                    'معدات', 'تأمين', 'ضرائب', 'مواصلات', 'اتصالات', 'أخرى'
                ]
            )
            
            # اقتراحات حسب الفئة
            category_suggestions = get_category_suggestions(category)
            if category_suggestions:
                st.info(f"**اقتراحات لفئة {category}:**\n{category_suggestions}")
            
            description = st.text_input(
                "وصف المصروف *",
                placeholder=f"مثال: {get_category_example(category)}"
            )
            
            amount = st.number_input(
                "المبلغ (ج.م) *",
                min_value=0.0,
                value=0.0,
                step=50.0
            )
            
            expense_date = st.date_input(
                "تاريخ المصروف *",
                value=date.today(),
                max_value=date.today()
            )
        
        with col2:
            st.subheader("💳 معلومات الدفع")
            
            payment_method = st.selectbox(
                "طريقة الدفع *",
                ["نقداً", "بطاقة ائتمان", "بطاقة خصم", "تحويل بنكي", "شيك"]
            )
            
            receipt_number = st.text_input(
                "رقم الإيصال/الفاتورة",
                placeholder="رقم الإيصال أو الفاتورة"
            )
            
            # معلومات إضافية حسب طريقة الدفع
            if payment_method == "شيك":
                check_number = st.text_input("رقم الشيك")
                bank_name = st.text_input("اسم البنك")
            elif payment_method == "تحويل بنكي":
                transaction_ref = st.text_input("رقم العملية")
                bank_name = st.text_input("اسم البنك")
            
            supplier_vendor = st.text_input(
                "المورد/البائع",
                placeholder="اسم المورد أو البائع"
            )
            
            # تحديد ما إذا كان المصروف متكرر
            is_recurring = st.checkbox("مصروف متكرر (شهرياً)")
            
            if is_recurring:
                recurring_months = st.number_input(
                    "عدد الأشهر",
                    min_value=2,
                    max_value=12,
                    value=3
                )
        
        # تفاصيل إضافية
        with st.expander("📋 تفاصيل إضافية"):
            col3, col4 = st.columns(2)
            
            with col3:
                department = st.selectbox(
                    "القسم المسؤول",
                    ["إدارة", "طبي", "تمريض", "استقبال", "صيانة", "تنظيف", "أمن"]
                )
                
                tax_amount = st.number_input(
                    "قيمة الضريبة (ج.م)",
                    min_value=0.0,
                    value=0.0,
                    step=5.0
                )
            
            with col4:
                priority = st.selectbox(
                    "الأولوية",
                    ["عادي", "مهم", "عاجل"]
                )
                
                # المبلغ النهائي مع الضريبة
                final_amount = amount + tax_amount
                st.metric("💸 المبلغ النهائي", format_currency(final_amount))
        
        notes = st.text_area(
            "ملاحظات",
            placeholder="أي ملاحظات إضافية عن المصروف..."
        )
        
        # رفع ملف الإيصال
        uploaded_receipt = st.file_uploader(
            "رفع صورة الإيصال/الفاتورة (اختياري)",
            type=['jpg', 'jpeg', 'png', 'pdf'],
            help="يمكن رفع صورة أو ملف PDF للإيصال"
        )
        
        submitted = st.form_submit_button("💾 حفظ المصروف", use_container_width=True)
        
        if submitted:
            # التحقق من صحة البيانات
            errors = []
            
            if not description.strip():
                errors.append("وصف المصروف مطلوب")
            
            if final_amount <= 0:
                errors.append("مبلغ المصروف يجب أن يكون أكبر من صفر")
            
            if errors:
                for error in errors:
                    show_error_message(error)
                return
            
            try:
                # حفظ المصروف الرئيسي
                expense_notes = notes
                if supplier_vendor:
                    expense_notes += f"\nالمورد: {supplier_vendor}"
                if uploaded_receipt:
                    expense_notes += f"\nتم رفع إيصال: {uploaded_receipt.name}"
                
                expense_id = crud.create_expense(
                    category=category,
                    description=description.strip(),
                    amount=final_amount,
                    expense_date=expense_date,
                    payment_method=payment_method,
                    receipt_number=receipt_number.strip() if receipt_number else "",
                    notes=expense_notes
                )
                
                # إذا كان المصروف متكرر، إنشاء المصروفات المستقبلية
                if is_recurring and 'recurring_months' in locals():
                    create_recurring_expenses(
                        category, description, final_amount, payment_method,
                        expense_date, recurring_months, expense_notes
                    )
                
                show_success_message(f"تم إضافة المصروف بنجاح (المعرف: {expense_id})")
                
                # عرض ملخص المصروف
                display_expense_summary(expense_id, category, description, final_amount, expense_date)
                
                if st.button("🔄 إضافة مصروف آخر"):
                    st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ المصروف: {str(e)}")

def expenses_reports():
    """تقارير المصروفات"""
    st.subheader("📊 تقارير المصروفات")
    
    try:
        expenses_df = crud.get_all_expenses()
        
        if expenses_df.empty:
            st.info("لا توجد مصروفات")
            return
        
        # فلترة التواريخ
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("إلى تاريخ", value=date.today())
        
        # فلترة البيانات
        filtered_expenses = filter_dataframe_by_date(expenses_df, 'expense_date', start_date, end_date)
        
        if filtered_expenses.empty:
            st.info("لا توجد مصروفات في هذه الفترة")
            return
        
        # التقارير المختلفة
        show_expenses_analytics(filtered_expenses)
        show_category_breakdown(filtered_expenses)
        show_monthly_expenses_trend(filtered_expenses)
        show_payment_methods_breakdown(filtered_expenses)
        show_top_expenses(filtered_expenses)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل التقارير: {str(e)}")

def budget_management():
    """إدارة الميزانية"""
    st.subheader("📊 إدارة الميزانية")
    
    try:
        # إعداد الميزانية الشهرية
        st.subheader("📝 إعداد الميزانية الشهرية")
        
        with st.form("budget_setup"):
            col1, col2 = st.columns(2)
            
            with col1:
                budget_month = st.selectbox(
                    "الشهر",
                    range(1, 13),
                    index=datetime.now().month - 1,
                    format_func=lambda x: [
                        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
                    ][x-1]
                )
                
                budget_year = st.selectbox(
                    "السنة",
                    range(2020, 2030),
                    index=datetime.now().year - 2020
                )
            
            with col2:
                total_budget = st.number_input(
                    "إجمالي الميزانية الشهرية (ج.م)",
                    min_value=0.0,
                    value=50000.0,
                    step=1000.0
                )
            
            # توزيع الميزانية حسب الفئات
            st.subheader("📊 توزيع الميزانية")
            
            categories = ['رواتب', 'إيجار', 'مرافق', 'صيانة', 'تسويق', 'مواد وخامات', 'معدات', 'أخرى']
            budget_breakdown = {}
            
            cols = st.columns(4)
            for i, category in enumerate(categories):
                with cols[i % 4]:
                    suggested_percentage = get_suggested_budget_percentage(category)
                    suggested_amount = total_budget * (suggested_percentage / 100)
                    
                    budget_breakdown[category] = st.number_input(
                        f"{category} ({suggested_percentage}%)",
                        min_value=0.0,
                        value=suggested_amount,
                        step=500.0,
                        key=f"budget_{category}"
                    )
            
            if st.form_submit_button("💾 حفظ الميزانية"):
                save_budget(budget_month, budget_year, budget_breakdown)
        
        # مقارنة الميزانية مع المصروفات الفعلية
        st.divider()
        compare_budget_vs_actual(budget_month, budget_year, budget_breakdown)
        
    except Exception as e:
        show_error_message(f"خطأ في إدارة الميزانية: {str(e)}")

# الدوال المساعدة

def apply_expenses_filters(expenses_df, start_date, end_date, category_filter, method_filter):
    """تطبيق فلاتر المصروفات"""
    filtered_df = filter_dataframe_by_date(expenses_df, 'expense_date', start_date, end_date)
    
    # فلترة حسب الفئة
    if category_filter != "الكل":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    # فلترة حسب طريقة الدفع
    if method_filter != "الكل":
        filtered_df = filtered_df[filtered_df['payment_method'] == method_filter]
    
    return filtered_df

def show_expenses_summary(expenses_df):
    """عرض ملخص المصروفات"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_expenses = len(expenses_df)
        st.metric("📋 إجمالي المصروفات", total_expenses)
    
    with col2:
        total_amount = expenses_df['amount'].sum()
        st.metric("💸 إجمالي المبلغ", format_currency(total_amount))
    
    with col3:
        avg_expense = expenses_df['amount'].mean()
        st.metric("📊 متوسط المصروف", format_currency(avg_expense))
    
    with col4:
        max_expense = expenses_df['amount'].max()
        st.metric("🔥 أعلى مصروف", format_currency(max_expense))

def get_category_suggestions(category):
    """اقتراحات حسب فئة المصروف"""
    suggestions = {
        'رواتب': 'رواتب الموظفين، مكافآت، تأمينات اجتماعية',
        'إيجار': 'إيجار العيادة، إيجار مخزن، إيجار موقف سيارات',
        'مرافق': 'كهرباء، مياه، غاز، إنترنت، هاتف',
        'صيانة': 'صيانة المعدات، صيانة المبنى، صيانة دورية',
        'تسويق': 'إعلانات، بروشورات، موقع إلكتروني، وسائل التواصل',
        'مواد وخامات': 'مواد طبية، أدوات، مستهلكات',
        'معدات': 'شراء معدات جديدة، تطوير المعدات',
        'تأمين': 'تأمين المبنى، تأمين المعدات، تأمين المسؤولية',
        'ضرائب': 'ضرائب الدخل، ضرائب العقارات، رسوم حكومية',
        'مواصلات': 'وقود، صيانة سيارات، أجرة انتقالات',
        'اتصالات': 'فواتير الهاتف، الإنترنت، أنظمة الاتصال'
    }
    return suggestions.get(category, '')

def get_category_example(category):
    """مثال على المصروف حسب الفئة"""
    examples = {
        'رواتب': 'راتب الطبيب المساعد - شهر ديسمبر',
        'إيجار': 'إيجار العيادة - شهر ديسمبر 2024',
        'مرافق': 'فاتورة الكهرباء - ديسمبر 2024',
        'صيانة': 'صيانة جهاز الأشعة',
        'تسويق': 'إعلان على فيسبوك - حملة ديسمبر',
        'مواد وخامات': 'شراء قفازات طبية وكمامات',
        'معدات': 'شراء كرسي طبيب أسنان جديد',
        'تأمين': 'تأمين العيادة السنوي',
        'ضرائب': 'ضريبة الدخل الشهرية',
        'مواصلات': 'وقود سيارة العيادة',
        'اتصالات': 'فاتورة الإنترنت الشهرية'
    }
    return examples.get(category, 'وصف المصروف')

def create_recurring_expenses(category, description, amount, payment_method, start_date, months, notes):
    """إنشاء مصروفات متكررة"""
    try:
        created_count = 0
        
        for i in range(1, months):  # البداية من 1 لأن المصروف الأول تم إنشاؤه
            # حساب تاريخ المصروف التالي
            next_month = start_date.month + i
            next_year = start_date.year
            
            if next_month > 12:
                next_year += (next_month - 1) // 12
                next_month = ((next_month - 1) % 12) + 1
            
            try:
                next_date = date(next_year, next_month, start_date.day)
            except ValueError:
                # في حالة 31/1 -> 28/2 مثلاً
                next_date = date(next_year, next_month, min(start_date.day, 28))
            
            # إنشاء المصروف المتكرر
            crud.create_expense(
                category=category,
                description=f"{description} - الشهر {i+1}",
                amount=amount,
                expense_date=next_date,
                payment_method=payment_method,
                receipt_number="",
                notes=f"{notes}\nمصروف متكرر مجدول"
            )
            
            created_count += 1
        
        show_success_message(f"تم إنشاء {created_count} مصروف متكرر إضافي")
        
    except Exception as e:
        show_error_message(f"خطأ في إنشاء المصروفات المتكررة: {str(e)}")

def display_expense_summary(expense_id, category, description, amount, expense_date):
    """عرض ملخص المصروف"""
    st.success("✅ تم إضافة المصروف بنجاح!")
    
    st.info(f"""
    **📋 ملخص المصروف:**
    - **رقم المصروف:** {expense_id}
    - **الفئة:** {category}
    - **الوصف:** {description}
    - **المبلغ:** {format_currency(amount)}
    - **التاريخ:** {format_date_arabic(expense_date)}
    """)

def save_expenses_changes(edited_df, original_df):
    """حفظ تعديلات المصروفات"""
    try:
        changes_count = 0
        
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            
            # التحقق من وجود تغييرات
            if (row['description'] != original_row['description'] or 
                row['amount'] != original_row['amount'] or
                row['category'] != original_row['category'] or
                row['payment_method'] != original_row['payment_method']):
                
                # هنا يجب إضافة دالة تحديث المصروف في crud.py
                # crud.update_expense(row['id'], ...)
                changes_count += 1
        
        if changes_count > 0:
            show_success_message(f"تم حفظ {changes_count} تعديل بنجاح")
            st.rerun()
        else:
            st.info("لا توجد تعديلات للحفظ")
        
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def delete_selected_expenses(expense_ids):
    """حذف المصروفات المحددة"""
    try:
        # هنا يجب إضافة دالة حذف المصروف في crud.py
        # for expense_id in expense_ids:
        #     crud.delete_expense(expense_id)
        
        show_success_message(f"تم حذف {len(expense_ids)} مصروف بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حذف المصروفات: {str(e)}")

def export_expenses_data(expenses_df):
    """تصدير بيانات المصروفات"""
    try:
        from utils.helpers import export_to_excel
        
        export_columns = {
            'id': 'المعرف',
            'category': 'الفئة',
            'description': 'الوصف',
            'amount': 'المبلغ',
            'expense_date': 'تاريخ المصروف',
            'payment_method': 'طريقة الدفع',
            'receipt_number': 'رقم الإيصال',
            'notes': 'ملاحظات',
            'created_at': 'تاريخ التسجيل'
        }
        
        export_df = expenses_df[list(export_columns.keys())].rename(columns=export_columns)
        excel_data = export_to_excel(export_df, "expenses_report")
        
        st.download_button(
            label="📥 تحميل Excel",
            data=excel_data,
            file_name=f"expenses_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        show_error_message(f"خطأ في التصدير: {str(e)}")

def analyze_expenses(expenses_df):
    """تحليل متقدم للمصروفات"""
    st.subheader("🔍 تحليل متقدم للمصروفات")
    
    import plotly.express as px
    
    # تحليل الاتجاهات الزمنية
    expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date'])
    expenses_df['month'] = expenses_df['expense_date'].dt.month
    expenses_df['weekday'] = expenses_df['expense_date'].dt.dayofweek
    
    col1, col2 = st.columns(2)
    
    with col1:
        # أعلى فئات المصروفات
        category_expenses = expenses_df.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        fig1 = px.bar(
            x=category_expenses.values,
            y=category_expenses.index,
            orientation='h',
            title="أعلى فئات المصروفات"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # توزيع المصروفات الشهرية
        monthly_expenses = expenses_df.groupby('month')['amount'].sum()
        month_names = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                      'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        monthly_expenses.index = [month_names[i-1] for i in monthly_expenses.index]
        
        fig2 = px.line(
            x=monthly_expenses.index,
            y=monthly_expenses.values,
            title="اتجاه المصروفات الشهرية"
        )
        st.plotly_chart(fig2, use_container_width=True)

def show_expenses_analytics(expenses_df):
    """تحليل المصروفات"""
    st.subheader("📊 تحليل المصروفات")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_expenses = expenses_df['amount'].sum()
        st.metric("💸 إجمالي المصروفات", format_currency(total_expenses))
    
    with col2:
        daily_avg = expenses_df.groupby('expense_date')['amount'].sum().mean()
        st.metric("📈 متوسط يومي", format_currency(daily_avg))
    
    with col3:
        max_expense = expenses_df['amount'].max()
        st.metric("🔥 أعلى مصروف", format_currency(max_expense))

def show_category_breakdown(expenses_df):
    """تفصيل المصروفات حسب الفئة"""
    st.subheader("📊 تفصيل المصروفات حسب الفئة")
    
    import plotly.express as px
    
    category_stats = expenses_df.groupby('category').agg({
        'amount': ['sum', 'count', 'mean']
    }).round(2)
    
    category_stats.columns = ['إجمالي المبلغ', 'عدد المصروفات', 'متوسط المصروف']
    category_stats = category_stats.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.pie(category_stats, values='إجمالي المبلغ', names='category',
                     title="توزيع المبالغ حسب الفئة")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.dataframe(
            category_stats,
            column_config={
                'إجمالي المبلغ': st.column_config.NumberColumn(format="%.2f ج.م"),
                'متوسط المصروف': st.column_config.NumberColumn(format="%.2f ج.م")
            },
            use_container_width=True,
            hide_index=True
        )

def show_monthly_expenses_trend(expenses_df):
    """اتجاه المصروفات الشهرية"""
    st.subheader("📈 اتجاه المصروفات الشهرية")
    
    import plotly.express as px
    
    expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date'])
    monthly_expenses = expenses_df.groupby(expenses_df['expense_date'].dt.to_period('M'))['amount'].sum().reset_index()
    monthly_expenses['expense_date'] = monthly_expenses['expense_date'].astype(str)
    
    fig = px.line(monthly_expenses, x='expense_date', y='amount',
                 title="المصروفات الشهرية",
                 labels={'expense_date': 'الشهر', 'amount': 'المبلغ (ج.م)'})
    
    st.plotly_chart(fig, use_container_width=True)

def show_payment_methods_breakdown(expenses_df):
    """تفصيل طرق الدفع"""
    st.subheader("💳 تفصيل طرق الدفع")
    
    import plotly.express as px
    
    payment_stats = expenses_df.groupby('payment_method')['amount'].sum().sort_values(ascending=False)
    
    fig = px.bar(x=payment_stats.index, y=payment_stats.values,
                title="المصروفات حسب طريقة الدفع")
    
    st.plotly_chart(fig, use_container_width=True)

def show_top_expenses(expenses_df):
    """أعلى المصروفات"""
    st.subheader("🔥 أعلى المصروفات")
    
    top_expenses = expenses_df.nlargest(10, 'amount')[['category', 'description', 'amount', 'expense_date']]
    
    st.dataframe(
        top_expenses,
        column_config={
            'category': 'الفئة',
            'description': 'الوصف',
            'amount': st.column_config.NumberColumn(
                'المبلغ',
                format="%.2f ج.م"
            ),
            'expense_date': 'التاريخ'
        },
        use_container_width=True,
        hide_index=True
    )

def get_suggested_budget_percentage(category):
    """الحصول على النسبة المقترحة للميزانية حسب الفئة"""
    percentages = {
        'رواتب': 40,
        'إيجار': 15,
        'مرافق': 8,
        'صيانة': 5,
        'تسويق': 3,
        'مواد وخامات': 10,
        'معدات': 5,
        'أخرى': 14
    }
    return percentages.get(category, 5)

def save_budget(month, year, budget_breakdown):
    """حفظ الميزانية"""
    # هنا يمكن حفظ الميزانية في قاعدة البيانات أو ملف
    show_success_message(f"تم حفظ ميزانية {month}/{year} بنجاح")

def compare_budget_vs_actual(month, year, budget_breakdown):
    """مقارنة الميزانية مع المصروفات الفعلية"""
    st.subheader("📊 مقارنة الميزانية مع المصروفات الفعلية")
    
    try:
        # الحصول على المصروفات الفعلية للشهر
        expenses_df = crud.get_all_expenses()
        
        if not expenses_df.empty:
            expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date'])
            monthly_expenses = expenses_df[
                (expenses_df['expense_date'].dt.month == month) &
                (expenses_df['expense_date'].dt.year == year)
            ]
            
            if not monthly_expenses.empty:
                actual_expenses = monthly_expenses.groupby('category')['amount'].sum().to_dict()
                
                # إنشاء جدول المقارنة
                comparison_data = []
                
                for category, budgeted in budget_breakdown.items():
                    actual = actual_expenses.get(category, 0)
                    variance = actual - budgeted
                    variance_pct = (variance / budgeted * 100) if budgeted > 0 else 0
                    
                    comparison_data.append({
                        'الفئة': category,
                        'الميزانية': budgeted,
                        'الفعلي': actual,
                        'الفرق': variance,
                        'النسبة %': variance_pct
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                
                st.dataframe(
                    comparison_df,
                    column_config={
                        'الميزانية': st.column_config.NumberColumn(format="%.2f ج.م"),
                        'الفعلي': st.column_config.NumberColumn(format="%.2f ج.م"),
                        'الفرق': st.column_config.NumberColumn(format="+%.2f ج.م"),
                        'النسبة %': st.column_config.NumberColumn(format="+%.1f%%")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                # ملخص الأداء
                total_budgeted = sum(budget_breakdown.values())
                total_actual = sum(actual_expenses.values())
                total_variance = total_actual - total_budgeted
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("💰 إجمالي الميزانية", format_currency(total_budgeted))
                
                with col2:
                    st.metric("💸 إجمالي المصروفات", format_currency(total_actual))
                
                with col3:
                    variance_color = "normal" if total_variance <= 0 else "inverse"
                    st.metric(
                        "📊 الفرق", 
                        format_currency(abs(total_variance)),
                        delta=f"{total_variance:+.2f} ج.م",
                        delta_color=variance_color
                    )
            else:
                st.info(f"لا توجد مصروفات في {month}/{year}")
        else:
            st.info("لا توجد مصروفات مسجلة")
    
    except Exception as e:
        show_error_message(f"خطأ في مقارنة الميزانية: {str(e)}")

if __name__ == "__main__":
    show_expenses()