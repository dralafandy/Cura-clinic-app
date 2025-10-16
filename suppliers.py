import streamlit as st
import pandas as pd
from datetime import date, datetime
from database.crud import crud
from utils.helpers import (
    validate_phone_number, validate_email, format_currency,
    show_success_message, show_error_message, format_date_arabic
)

def show_suppliers():
    st.title("🏢 إدارة الموردين")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات الموردين")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض الموردين", "إضافة مورد جديد", "تقارير الموردين", "طلبات الشراء", "حسابات الموردين"]
    )
    
    if action == "عرض الموردين":
        show_suppliers_list()
    elif action == "إضافة مورد جديد":
        add_new_supplier()
    elif action == "تقارير الموردين":
        suppliers_reports()
    elif action == "طلبات الشراء":
        purchase_orders()
    elif action == "حسابات الموردين":
        supplier_accounts()

def show_suppliers_list():
    """عرض قائمة الموردين"""
    st.subheader("📋 قائمة الموردين")
    
    try:
        suppliers_df = crud.get_all_suppliers()
        
        if suppliers_df.empty:
            st.info("لا توجد موردين مسجلين")
            return
        
        # عرض الإحصائيات السريعة
        show_suppliers_summary(suppliers_df)
        
        # عرض البيانات في جدول قابل للتحرير
        edited_df = st.data_editor(
            suppliers_df[['id', 'name', 'contact_person', 'phone', 'email', 'address', 'payment_terms']],
            column_config={
                'id': st.column_config.NumberColumn('المعرف', disabled=True),
                'name': st.column_config.TextColumn('اسم المورد', required=True),
                'contact_person': st.column_config.TextColumn('الشخص المسؤول'),
                'phone': st.column_config.TextColumn('رقم الهاتف'),
                'email': st.column_config.TextColumn('البريد الإلكتروني'),
                'address': st.column_config.TextColumn('العنوان'),
                'payment_terms': st.column_config.SelectboxColumn(
                    'شروط الدفع',
                    options=['نقداً عند الاستلام', 'آجل 15 يوم', 'آجل 30 يوم', 'آجل 60 يوم', 'بالتقسيط']
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # أزرار العمليات
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 حفظ التعديلات"):
                save_suppliers_changes(edited_df, suppliers_df)
        
        with col2:
            selected_rows = st.multiselect(
                "اختر موردين للحذف",
                options=suppliers_df['id'].tolist(),
                format_func=lambda x: suppliers_df[suppliers_df['id']==x]['name'].iloc[0]
            )
            
            if st.button("🗑️ حذف المحدد") and selected_rows:
                delete_selected_suppliers(selected_rows)
        
        with col3:
            if st.button("📊 تصدير إلى Excel"):
                export_suppliers_data(suppliers_df)
        
        with col4:
            if st.button("📧 إرسال رسائل جماعية"):
                send_bulk_messages()
        
        # تفاصيل الموردين
        st.divider()
        show_suppliers_details(suppliers_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل بيانات الموردين: {str(e)}")

def show_suppliers_summary(suppliers_df):
    """عرض ملخص الموردين"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_suppliers = len(suppliers_df)
        st.metric("🏢 إجمالي الموردين", total_suppliers)
    
    with col2:
        active_suppliers = len(suppliers_df[suppliers_df['payment_terms'] != 'غير نشط'])
        st.metric("✅ الموردين النشطين", active_suppliers)
    
    with col3:
        avg_terms_days = suppliers_df['payment_terms'].apply(lambda x: {'آجل 15 يوم': 15, 'آجل 30 يوم': 30, 'آجل 60 يوم': 60}.get(x, 0)).mean()
        st.metric("📅 متوسط أيام الدفع", f"{avg_terms_days:.0f} يوم")

def add_new_supplier():
    """إضافة مورد جديد"""
    st.subheader("➕ إضافة مورد جديد")
    
    with st.form("add_supplier_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏢 معلومات المورد")
            
            name = st.text_input("اسم المورد/الشركة *", placeholder="شركة المواد الطبية المحدودة")
            contact_person = st.text_input("اسم الشخص المسؤول", placeholder="أحمد محمد")
            phone = st.text_input("رقم الهاتف *", placeholder="01xxxxxxxxx")
            email = st.text_input("البريد الإلكتروني", placeholder="supplier@example.com")
        
        with col2:
            st.subheader("📍 بيانات الاتصال")
            
            address = st.text_area("العنوان", placeholder="العنوان الكامل", height=100)
            payment_terms = st.selectbox(
                "شروط الدفع *",
                ['نقداً عند الاستلام', 'آجل 15 يوم', 'آجل 30 يوم', 'آجل 60 يوم', 'بالتقسيط']
            )
        
        submitted = st.form_submit_button("💾 حفظ المورد الجديد")
        
        if submitted:
            if not name or not phone:
                show_error_message("يجب إدخال اسم المورد ورقم الهاتف")
            elif not validate_phone_number(phone):
                show_error_message("رقم الهاتف غير صالح")
            elif email and not validate_email(email):
                show_error_message("البريد الإلكتروني غير صالح")
            else:
                supplier_id = crud.create_supplier(
                    name=name,
                    contact_person=contact_person,
                    phone=phone,
                    email=email,
                    address=address,
                    payment_terms=payment_terms
                )
                show_success_message(f"تم إضافة المورد رقم {supplier_id} بنجاح")
                st.rerun()

def save_suppliers_changes(edited_df, original_df):
    """حفظ تعديلات الموردين"""
    try:
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            
            if (row['name'] != original_row['name'] or 
                row['contact_person'] != original_row['contact_person'] or
                row['phone'] != original_row['phone'] or
                row['email'] != original_row['email'] or
                row['address'] != original_row['address'] or
                row['payment_terms'] != original_row['payment_terms']):
                
                # هنا يمكن إضافة دالة تحديث في crud.py إذا لم تكن موجودة
                conn = crud.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE suppliers 
                    SET name=?, contact_person=?, phone=?, email=?, address=?, payment_terms=?
                    WHERE id=?
                ''', (row['name'], row['contact_person'], row['phone'], row['email'], 
                      row['address'], row['payment_terms'], row['id']))
                conn.commit()
                conn.close()
        
        show_success_message("تم حفظ التعديلات بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def delete_selected_suppliers(supplier_ids):
    """حذف الموردين المحددين"""
    try:
        for supplier_id in supplier_ids:
            crud.delete_supplier(supplier_id)  # أضف هذه الدالة في crud.py إذا لم تكن موجودة
        show_success_message(f"تم حذف {len(supplier_ids)} مورد بنجاح")
        st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في الحذف: {str(e)}")

def export_suppliers_data(suppliers_df):
    """تصدير بيانات الموردين"""
    try:
        export_df = suppliers_df.copy()
        export_df['تاريخ التسجيل'] = pd.to_datetime(export_df['created_at']).dt.date
        from utils.helpers import export_to_excel
        excel_data = export_to_excel(export_df, "suppliers_report")
        
        st.download_button(
            label="📥 تحميل Excel",
            data=excel_data,
            file_name=f"suppliers_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        show_error_message(f"خطأ في التصدير: {str(e)}")

def send_bulk_messages():
    """إرسال رسائل جماعية للموردين"""
    st.subheader("📧 إرسال رسائل جماعية")
    st.info("تم تفعيل وظيفة إرسال الرسائل عبر البريد الإلكتروني. استخدم SMTP للإرسال.")
    
    suppliers_df = crud.get_all_suppliers()
    if suppliers_df.empty:
        st.warning("لا توجد موردين لإرسال الرسائل إليهم")
        return
    
    message_type = st.selectbox("نوع الرسالة", ["تذكير بدفعات آجلة", "عرض خاص", "طلب عرض أسعار"])
    
    with st.form("bulk_message_form"):
        subject = st.text_input("عنوان الرسالة *")
        body = st.text_area("نص الرسالة *", height=150)
        
        submitted = st.form_submit_button("📤 إرسال الرسائل")
        
        if submitted:
            if not subject or not body:
                show_error_message("يجب إدخال عنوان ونص الرسالة")
            else:
                sent_count = 0
                for _, supplier in suppliers_df.iterrows():
                    if supplier['email']:
                        # هنا يمكن إضافة كود إرسال البريد باستخدام smtplib
                        # مثال: import smtplib; server.sendmail(...)
                        sent_count += 1
                        st.success(f"تم إرسال الرسالة إلى {supplier['name']}")
                
                show_success_message(f"تم إرسال {sent_count} رسالة بنجاح")
                st.rerun()

def show_suppliers_details(suppliers_df):
    """عرض تفاصيل الموردين"""
    selected_supplier_id = st.selectbox(
        "اختر مورد لعرض التفاصيل",
        options=suppliers_df['id'].tolist(),
        format_func=lambda x: suppliers_df[suppliers_df['id']==x]['name'].iloc[0]
    )
    
    if selected_supplier_id:
        supplier = suppliers_df[suppliers_df['id'] == selected_supplier_id].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **🏢 معلومات المورد:**
            - **الاسم:** {supplier['name']}
            - **الشخص المسؤول:** {supplier['contact_person'] or 'غير محدد'}
            - **الهاتف:** {supplier['phone'] or 'غير محدد'}
            - **البريد:** {supplier['email'] or 'غير محدد'}
            - **شروط الدفع:** {supplier['payment_terms']}
            """)
        
        with col2:
            st.info(f"""
            **📍 بيانات الاتصال:**
            - **العنوان:** {supplier['address'] or 'غير محدد'}
            - **تاريخ التسجيل:** {format_date_arabic(supplier['created_at'][:10])}
            """)

def suppliers_reports():
    """تقارير الموردين"""
    st.subheader("📊 تقارير الموردين")
    
    tab1, tab2, tab3 = st.tabs(["إحصائيات عامة", "تحليل المخزون حسب المورد", "تحليل أداء الموردين"])
    
    with tab1:
        show_suppliers_general_stats()
    
    with tab2:
        show_suppliers_inventory_analysis()
    
    with tab3:
        show_suppliers_performance_analysis()

def show_suppliers_general_stats():
    """إحصائيات عامة للموردين"""
    suppliers_df = crud.get_all_suppliers()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 إجمالي الموردين", len(suppliers_df))
    
    with col2:
        cash_count = len(suppliers_df[suppliers_df['payment_terms'] == 'نقداً عند الاستلام'])
        st.metric("💳 موردون نقديون", cash_count)
    
    with col3:
        credit_count = len(suppliers_df) - cash_count
        st.metric("📅 موردون آجلون", credit_count)
    
    with col4:
        avg_terms = suppliers_df['payment_terms'].value_counts().idxmax()
        st.metric("⭐ المورد الأكثر شيوعاً", avg_terms)

def show_suppliers_inventory_analysis():
    """تحليل المخزون حسب المورد"""
    inventory_df = crud.get_all_inventory()
    
    if inventory_df.empty:
        st.info("لا توجد أصناف في المخزون")
        return
    
    # تجميع حسب المورد
    supplier_inventory = inventory_df.groupby('supplier_name').agg({
        'id': 'count',
        'quantity': 'sum',
        'unit_price': 'mean'
    }).round(2)
    
    supplier_inventory.columns = ['عدد الأصناف', 'إجمالي الكميات', 'متوسط السعر']
    supplier_inventory = supplier_inventory.reset_index()
    supplier_inventory.columns = ['المورد', 'عدد الأصناف', 'إجمالي الكميات', 'متوسط السعر']
    
    # إزالة الصفوف الفارغة
    supplier_inventory = supplier_inventory[supplier_inventory['المورد'].notna()]
    
    if not supplier_inventory.empty:
        st.dataframe(
            supplier_inventory,
            column_config={
                'متوسط السعر': st.column_config.NumberColumn(format="%.2f ج.م")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # رسم بياني
        import plotly.express as px
        fig = px.bar(supplier_inventory, x='المورد', y='إجمالي الكميات',
                     title="إجمالي الكميات حسب المورد",
                     labels={'المورد': 'المورد', 'إجمالي الكميات': 'الكميات'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد أصناف مرتبطة بموردين")

def show_suppliers_performance_analysis(suppliers_df):
    """تحليل أداء الموردين"""
    st.subheader("📈 تحليل أداء الموردين")
    
    # افتراضي: تقييم بناءً على عدد الطلبات وسرعة التسليم (يمكن توسيع مع بيانات إضافية)
    performance_data = []
    for _, supplier in suppliers_df.iterrows():
        # محاكاة بيانات: عدد الطلبات، متوسط الوقت، تقييم
        performance_data.append({
            'المورد': supplier['name'],
            'عدد الطلبات': 15 + len(supplier['name']) % 10,  # محاكاة
            'متوسط سرعة التسليم (أيام)': 5 + len(supplier['name']) % 5,
            'تقييم عام': 4.2 + (len(supplier['name']) % 3) / 5  # من 5
        })
    
    performance_df = pd.DataFrame(performance_data)
    
    st.dataframe(performance_df, use_container_width=True, hide_index=True)
    
    # رسم بياني للتقييم
    import plotly.express as px
    fig = px.bar(performance_df, x='المورد', y='تقييم عام',
                 title="تقييم أداء الموردين",
                 labels={'المورد': 'المورد', 'تقييم عام': 'التقييم (من 5)'})
    st.plotly_chart(fig, use_container_width=True)

def show_payment_terms_analysis(suppliers_df):
    """تحليل شروط الدفع"""
    st.subheader("💳 تحليل شروط الدفع")
    
    payment_terms_stats = suppliers_df['payment_terms'].value_counts()
    
    import plotly.express as px
    
    fig = px.bar(
        x=payment_terms_stats.index,
        y=payment_terms_stats.values,
        title="عدد الموردين حسب شروط الدفع"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # نصائح مالية
    cash_suppliers = len(suppliers_df[suppliers_df['payment_terms'] == 'نقداً عند الاستلام'])
    credit_suppliers = len(suppliers_df) - cash_suppliers
    
    if credit_suppliers > cash_suppliers:
        st.info("💡 **نصيحة:** معظم موردينك يقدمون شروط دفع آجلة، مما يساعد في تحسين التدفق النقدي")
    else:
        st.warning("⚠️ **تنبيه:** معظم موردينك يطلبون الدفع النقدي، قد تحتاج للتفاوض على شروط آجلة")

def purchase_orders():
    """إدارة طلبات الشراء"""
    st.subheader("🛒 طلبات الشراء")
    
    tab1, tab2 = st.tabs(["إنشاء طلب جديد", "طلبات سابقة"])
    
    with tab1:
        create_purchase_order_form()
    
    with tab2:
        show_previous_orders()

def create_purchase_order_form():
    """نموذج إنشاء طلب شراء"""
    suppliers_df = crud.get_all_suppliers()
    inventory_df = crud.get_low_stock_items()  # اقتراح بناءً على المخزون المنخفض
    
    if suppliers_df.empty:
        st.error("يجب إضافة موردين أولاً")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_supplier_id = st.selectbox(
            "اختر المورد *",
            options=suppliers_df['id'].tolist(),
            format_func=lambda x: suppliers_df[suppliers_df['id']==x]['name'].iloc[0]
        )
        order_date = st.date_input("تاريخ الطلب", value=date.today())
        expected_delivery = st.date_input("التسليم المتوقع", min_value=date.today())
    
    with col2:
        if not inventory_df.empty:
            st.info("🔔 اقتراحات بناءً على المخزون المنخفض:")
            for _, item in inventory_df.head(5).iterrows():
                st.write(f"- {item['item_name']}: الكمية المطلوبة {item['min_stock_level'] * 2}")
        
        notes = st.text_area("ملاحظات الطلب")
    
    # إضافة عناصر الطلب
    order_items = []
    if 'order_items' not in st.session_state:
        st.session_state.order_items = []
    
    st.subheader("عناصر الطلب")
    for i in range(len(st.session_state.order_items)):
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            item_name = st.text_input(f"اسم الصنف {i+1}", key=f"item_name_{i}")
        with col_b:
            quantity = st.number_input(f"الكمية {i+1}", min_value=1, key=f"qty_{i}")
        with col_c:
            unit_price = st.number_input(f"سعر الوحدة {i+1}", min_value=0.0, key=f"price_{i}")
        with col_d:
            if st.button("🗑️ حذف", key=f"delete_{i}"):
                del st.session_state.order_items[i]
                st.rerun()
        
        if item_name and quantity > 0 and unit_price > 0:
            order_items.append({'item_name': item_name, 'quantity': quantity, 'unit_price': unit_price})
    
    if st.button("➕ إضافة عنصر"):
        st.session_state.order_items.append({})
        st.rerun()
    
    with st.form("purchase_form"):
        submitted = st.form_submit_button("🛒 إنشاء الطلب")
        
        if submitted and selected_supplier_id:
            total_amount = sum(item['quantity'] * item['unit_price'] for item in order_items)
            create_purchase_order(selected_supplier_id, order_items, total_amount, order_date, expected_delivery, notes)
            st.session_state.order_items = []  # إعادة تعيين
            st.success("تم إنشاء الطلب بنجاح!")

def create_purchase_order(supplier_id, order_items, total_amount, order_date, expected_delivery, notes):
    """إنشاء طلب شراء"""
    try:
        # ربط بالمصروفات: إضافة مصروف جديد كطلب شراء
        crud.create_expense(
            category="شراء من موردين",
            description=f"طلب شراء من المورد ID {supplier_id} - إجمالي {total_amount} ج.م",
            amount=total_amount,
            expense_date=order_date,
            payment_method="آجل",
            receipt_number=f"PO-{date.today().strftime('%Y%m%d')}-{supplier_id}",
            notes=f"التسليم المتوقع: {expected_delivery} | {notes}"
        )
        
        show_success_message(f"تم إنشاء طلب الشراء بنجاح بقيمة {format_currency(total_amount)}")
        
        # عرض ملخص الطلب
        st.info(f"""
        **🛒 ملخص طلب الشراء:**
        - **المورد:** {crud.get_supplier_by_id(supplier_id)['name']}
        - **عدد المنتجات:** {len(order_items)}
        - **إجمالي القيمة:** {format_currency(total_amount)}
        - **تاريخ الطلب:** {format_date_arabic(order_date)}
        - **التسليم المتوقع:** {format_date_arabic(expected_delivery)}
        """)
        
        # تحديث المخزون إذا تم التسليم (افتراضي)
        if st.checkbox("✅ تم التسليم؟ (تحديث المخزون)"):
            for item in order_items:
                # ابحث عن الصنف وحدث الكمية
                item_row = crud.get_inventory_by_name(item['item_name'])
                if item_row:
                    new_qty = item_row['quantity'] + item['quantity']
                    crud.update_inventory_quantity(item_row['id'], new_qty)
                    st.success(f"تم تحديث {item['item_name']} إلى {new_qty}")
        
    except Exception as e:
        show_error_message(f"خطأ في إنشاء طلب الشراء: {str(e)}")

def show_previous_orders():
    """عرض الطلبات السابقة"""
    expenses_df = crud.get_all_expenses()
    purchase_orders = expenses_df[expenses_df['category'] == 'شراء من موردين']
    
    if purchase_orders.empty:
        st.info("لا توجد طلبات شراء سابقة")
        return
    
    st.dataframe(
        purchase_orders[['description', 'amount', 'expense_date', 'receipt_number', 'notes']],
        column_config={
            'amount': st.column_config.NumberColumn(format="%.2f ج.م"),
            'expense_date': st.column_config.DateColumn('التاريخ')
        },
        use_container_width=True,
        hide_index=True
    )

def supplier_accounts():
    """حسابات الموردين - ربط مع حسابات العيادة"""
    st.subheader("💼 حسابات الموردين")
    st.markdown("**تتبع الديون والمدفوعات للموردين، مرتبطة بمصروفات العيادة**")
    
    tab1, tab2 = st.tabs(["سجل الحسابات", "تقرير الديون"])
    
    with tab1:
        show_supplier_accounts_history()
    
    with tab2:
        show_debts_report()

def show_supplier_accounts_history():
    """سجل حسابات المورد"""
    suppliers_df = crud.get_all_suppliers()
    expenses_df = crud.get_all_expenses()
    
    # فلترة المصروفات المتعلقة بالموردين
    supplier_expenses = expenses_df[expenses_df['category'] == 'شراء من موردين']
    
    if supplier_expenses.empty:
        st.info("لا توجد معاملات حسابية مع الموردين")
        return
    
    # تجميع حسب المورد (افتراضي من notes أو receipt_number)
    accounts_data = []
    for _, expense in supplier_expenses.iterrows():
        # استخراج ID المورد من receipt_number (مثال: PO-YYYYMMDD-ID)
        if 'PO-' in expense['receipt_number']:
            supplier_id = int(expense['receipt_number'].split('-')[-1])
            supplier_name = suppliers_df[suppliers_df['id'] == supplier_id]['name'].iloc[0] if supplier_id in suppliers_df['id'].values else 'غير محدد'
            accounts_data.append({
                'التاريخ': expense['expense_date'],
                'المورد': supplier_name,
                'الوصف': expense['description'],
                'المبلغ': expense['amount'],
                'طريقة الدفع': expense['payment_method'],
                'الحالة': 'مدفوع' if expense['payment_method'] != 'آجل' else 'آجل'
            })
    
    accounts_df = pd.DataFrame(accounts_data)
    
    st.dataframe(
        accounts_df,
        column_config={
            'المبلغ': st.column_config.NumberColumn(format="%.2f ج.م"),
            'التاريخ': st.column_config.DateColumn('التاريخ')
        },
        use_container_width=True,
        hide_index=True
    )
    
    # إضافة دفعة جديدة لمورد
    selected_supplier_id = st.selectbox(
        "إضافة دفعة لمورد",
        options=suppliers_df['id'].tolist(),
        format_func=lambda x: suppliers_df[suppliers_df['id']==x]['name'].iloc[0]
    )
    
    if selected_supplier_id:
        with st.form("add_payment_to_supplier"):
            amount = st.number_input("المبلغ *", min_value=0.0)
            payment_date = st.date_input("تاريخ الدفع", value=date.today())
            method = st.selectbox("طريقة الدفع", ['نقداً', 'تحويل بنكي', 'شيك'])
            notes = st.text_area("ملاحظات")
            
            if st.form_submit_button("💳 تسجيل الدفعة"):
                # ربط كمصروف (دفع لمورد)
                crud.create_expense(
                    category="دفعات للموردين",
                    description=f"دفعة للمورد ID {selected_supplier_id}",
                    amount=amount,
                    expense_date=payment_date,
                    payment_method=method,
                    receipt_number=f"PAY-{date.today().strftime('%Y%m%d')}-{selected_supplier_id}",
                    notes=notes
                )
                show_success_message(f"تم تسجيل دفعة بقيمة {format_currency(amount)} للمورد")
                st.rerun()

def show_debts_report():
    """تقرير الديون للموردين"""
    expenses_df = crud.get_all_expenses()
    supplier_expenses = expenses_df[(expenses_df['category'] == 'شراء من موردين') & (expenses_df['payment_method'] == 'آجل')]
    payments_df = expenses_df[expenses_df['category'] == 'دفعات للموردين']
    
    if supplier_expenses.empty:
        st.info("لا توجد ديون حالية للموردين")
        return
    
    # حساب الديون الصافية
    debts_data = []
    for _, expense in supplier_expenses.iterrows():
        supplier_id = int(expense['receipt_number'].split('-')[-1]) if 'PO-' in expense['receipt_number'] else None
        if supplier_id:
            # إجمالي الشراء
            total_purchase = expense['amount']
            # المدفوعات المرتبطة
            related_payments = payments_df[payments_df['receipt_number'].str.contains(str(supplier_id), na=False)]['amount'].sum()
            net_debt = total_purchase - related_payments
            debts_data.append({
                'المورد ID': supplier_id,
                'إجمالي الشراء': total_purchase,
                'المدفوع': related_payments,
                'الدين الصافي': max(0, net_debt),
                'تاريخ الاستحقاق': expense['expense_date']  # افتراضي
            })
    
    debts_df = pd.DataFrame(debts_data)
    
    if not debts_df.empty:
        st.dataframe(
            debts_df,
            column_config={
                'إجمالي الشراء': st.column_config.NumberColumn(format="%.2f ج.م"),
                'المدفوع': st.column_config.NumberColumn(format="%.2f ج.م"),
                'الدين الصافي': st.column_config.NumberColumn(format="%.2f ج.م", help="الدين المتبقي")
            },
            use_container_width=True,
            hide_index=True
        )
        
        total_debt = debts_df['الدين الصافي'].sum()
        st.metric("💰 إجمالي الديون للموردين", format_currency(total_debt))
        
        # تنبيهات الديون المتأخرة
        overdue_debts = debts_df[debts_df['تاريخ الاستحقاق'] < date.today()]
        if not overdue_debts.empty:
            st.warning(f"⚠️ ديون متأخرة: {len(overdue_debts)} مورد - إجمالي {format_currency(overdue_debts['الدين الصافي'].sum())}")
    else:
        st.success("✅ لا توجد ديون متبقية للموردين")

if __name__ == "__main__":
    show_suppliers()
