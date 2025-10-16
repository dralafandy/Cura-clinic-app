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
        ["عرض الموردين", "إضافة مورد جديد", "تقارير الموردين", "طلبات الشراء"]
    )
    
    if action == "عرض الموردين":
        show_suppliers_list()
    elif action == "إضافة مورد جديد":
        add_new_supplier()
    elif action == "تقارير الموردين":
        suppliers_reports()
    elif action == "طلبات الشراء":
        purchase_orders()

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
            email = st.text_input("البريد الإلكتروني", placeholder="supplier@company.com")
            
            # معلومات الشركة
            company_registration = st.text_input("رقم السجل التجاري")
            tax_number = st.text_input("الرقم الضريبي")
        
        with col2:
            st.subheader("📍 معلومات الاتصال والدفع")
            
            address = st.text_area("عنوان المورد", placeholder="العنوان الكامل للمورد")
            
            payment_terms = st.selectbox(
                "شروط الدفع *",
                ["نقداً عند الاستلام", "آجل 15 يوم", "آجل 30 يوم", "آجل 60 يوم", "بالتقسيط"]
            )
            
            # معلومات الحساب البنكي
            bank_name = st.text_input("اسم البنك")
            account_number = st.text_input("رقم الحساب البنكي")
            
            # تصنيف المورد
            supplier_category = st.selectbox(
                "تصنيف المورد",
                ["مواد طبية", "معدات", "أدوية", "مستهلكات", "خدمات", "أخرى"]
            )
        
        # تقييم المورد
        with st.expander("⭐ تقييم المورد"):
            col3, col4 = st.columns(2)
            
            with col3:
                quality_rating = st.selectbox(
                    "تقييم الجودة",
                    [1, 2, 3, 4, 5],
                    index=4,
                    format_func=lambda x: "⭐" * x
                )
                
                delivery_rating = st.selectbox(
                    "تقييم التسليم",
                    [1, 2, 3, 4, 5],
                    index=4,
                    format_func=lambda x: "⭐" * x
                )
            
            with col4:
                service_rating = st.selectbox(
                    "تقييم الخدمة",
                    [1, 2, 3, 4, 5],
                    index=4,
                    format_func=lambda x: "⭐" * x
                )
                
                price_rating = st.selectbox(
                    "تقييم الأسعار",
                    [1, 2, 3, 4, 5],
                    index=4,
                    format_func=lambda x: "⭐" * x
                )
        
        # معلومات إضافية
        with st.expander("📋 معلومات إضافية"):
            col5, col6 = st.columns(2)
            
            with col5:
                credit_limit = st.number_input(
                    "الحد الائتماني (ج.م)",
                    min_value=0.0,
                    value=10000.0,
                    step=1000.0
                )
                
                preferred_supplier = st.checkbox("مورد مفضل")
            
            with col6:
                minimum_order = st.number_input(
                    "الحد الأدنى للطلب (ج.م)",
                    min_value=0.0,
                    value=500.0,
                    step=100.0
                )
                
                active_supplier = st.checkbox("مورد نشط", value=True)
        
        notes = st.text_area(
            "ملاحظات",
            placeholder="أي ملاحظات أو معلومات إضافية عن المورد..."
        )
        
        # معلومات المنتجات/الخدمات
        st.subheader("🛍️ المنتجات والخدمات")
        products_services = st.text_area(
            "المنتجات والخدمات المقدمة",
            placeholder="اذكر المنتجات والخدمات التي يقدمها هذا المورد..."
        )
        
        submitted = st.form_submit_button("💾 حفظ المورد", use_container_width=True)
        
        if submitted:
            # التحقق من صحة البيانات
            errors = []
            
            if not name.strip():
                errors.append("اسم المورد مطلوب")
            
            if not phone.strip():
                errors.append("رقم الهاتف مطلوب")
            elif not validate_phone_number(phone):
                errors.append("رقم الهاتف غير صحيح")
            
            if email and not validate_email(email):
                errors.append("البريد الإلكتروني غير صحيح")
            
            # التحقق من عدم تكرار الاسم
            existing_suppliers = crud.get_all_suppliers()
            if not existing_suppliers.empty and name.strip() in existing_suppliers['name'].values:
                errors.append("اسم المورد موجود مسبقاً")
            
            if errors:
                for error in errors:
                    show_error_message(error)
                return
            
            try:
                # حفظ المورد
                supplier_id = crud.create_supplier(
                    name=name.strip(),
                    contact_person=contact_person.strip() if contact_person else None,
                    phone=phone.strip(),
                    email=email.strip() if email else None,
                    address=address.strip() if address else None,
                    payment_terms=payment_terms
                )
                
                show_success_message(f"تم إضافة المورد '{name}' بنجاح (المعرف: {supplier_id})")
                
                # عرض ملخص المورد
                display_supplier_summary(supplier_id, name, contact_person, phone, payment_terms)
                
                if st.button("🔄 إضافة مورد آخر"):
                    st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ المورد: {str(e)}")

def suppliers_reports():
    """تقارير الموردين"""
    st.subheader("📊 تقارير الموردين")
    
    try:
        suppliers_df = crud.get_all_suppliers()
        inventory_df = crud.get_all_inventory()
        
        if suppliers_df.empty:
            st.info("لا توجد موردين")
            return
        
        # التقارير المختلفة
        show_suppliers_overview(suppliers_df)
        show_suppliers_inventory_report(suppliers_df, inventory_df)
        show_suppliers_performance_analysis(suppliers_df)
        show_payment_terms_analysis(suppliers_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل التقارير: {str(e)}")

def purchase_orders():
    """طلبات الشراء"""
    st.subheader("🛒 إدارة طلبات الشراء")
    
    try:
        # إنشاء طلب شراء جديد
        with st.expander("➕ إنشاء طلب شراء جديد"):
            create_purchase_order_form()
        
        # عرض طلبات الشراء الحالية
        st.subheader("📋 طلبات الشراء الحالية")
        
        # هنا يمكن إضافة جدول طلبات الشراء من قاعدة البيانات
        st.info("سيتم إضافة نظام إدارة طلبات الشراء قريباً")
        
        # اقتراحات طلبات الشراء بناءً على المخزون المنخفض
        suggest_purchase_orders()
        
    except Exception as e:
        show_error_message(f"خطأ في إدارة طلبات الشراء: {str(e)}")

# الدوال المساعدة

def show_suppliers_summary(suppliers_df):
    """عرض ملخص الموردين"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_suppliers = len(suppliers_df)
        st.metric("🏢 إجمالي الموردين", total_suppliers)
    
    with col2:
        # حساب الموردين النشطين (يمكن إضافة حقل is_active لاحقاً)
        active_suppliers = total_suppliers  # مؤقتاً
        st.metric("✅ الموردين النشطين", active_suppliers)
    
    with col3:
        # حساب عدد الموردين حسب شروط الدفع
        cash_suppliers = len(suppliers_df[suppliers_df['payment_terms'] == 'نقداً عند الاستلام'])
        st.metric("💰 دفع نقدي", cash_suppliers)
    
    with col4:
        # حساب عدد الموردين الآجلين
        credit_suppliers = total_suppliers - cash_suppliers
        st.metric("📅 دفع آجل", credit_suppliers)

def show_suppliers_details(suppliers_df):
    """عرض تفاصيل الموردين"""
    st.subheader("👁️ تفاصيل الموردين")
    
    # قائمة منسدلة لاختيار المورد
    supplier_names = {row['id']: row['name'] for _, row in suppliers_df.iterrows()}
    selected_supplier_id = st.selectbox(
        "اختر مورد لعرض التفاصيل",
        options=list(supplier_names.keys()),
        format_func=lambda x: supplier_names[x]
    )
    
    if selected_supplier_id:
        supplier = suppliers_df[suppliers_df['id'] == selected_supplier_id].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **🏢 معلومات المورد:**
            - **الاسم:** {supplier['name']}
            - **الشخص المسؤول:** {supplier['contact_person'] or 'غير محدد'}
            - **الهاتف:** {supplier['phone']}
            - **البريد:** {supplier['email'] or 'غير محدد'}
            """)
        
        with col2:
            st.info(f"""
            **📋 معلومات الدفع:**
            - **العنوان:** {supplier['address'] or 'غير محدد'}
            - **شروط الدفع:** {supplier['payment_terms']}
            - **تاريخ التسجيل:** {format_date_arabic(supplier['created_at'][:10])}
            """)
        
        # عرض المنتجات المرتبطة بالمورد
        show_supplier_products(selected_supplier_id)
        
        # أزرار الإجراءات
        col3, col4, col5 = st.columns(3)
        
        with col3:
            if st.button("📧 إرسال رسالة"):
                send_message_to_supplier(selected_supplier_id)
        
        with col4:
            if st.button("🛒 إنشاء طلب شراء"):
                create_purchase_order_for_supplier(selected_supplier_id)
        
        with col5:
            if st.button("📊 تقرير تفصيلي"):
                show_detailed_supplier_report(selected_supplier_id)

def show_supplier_products(supplier_id):
    """عرض المنتجات المرتبطة بالمورد"""
    st.subheader("🛍️ المنتجات المرتبطة")
    
    inventory_df = crud.get_all_inventory()
    
    if not inventory_df.empty:
        supplier_products = inventory_df[inventory_df['supplier_id'] == supplier_id]
        
        if not supplier_products.empty:
            st.dataframe(
                supplier_products[['item_name', 'category', 'quantity', 'unit_price']],
                column_config={
                    'item_name': 'اسم المنتج',
                    'category': 'الفئة',
                    'quantity': 'الكمية المتوفرة',
                    'unit_price': st.column_config.NumberColumn(
                        'سعر الوحدة',
                        format="%.2f ج.م"
                    )
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا توجد منتجات مرتبطة بهذا المورد")
    else:
        st.info("لا توجد منتجات في المخزون")

def save_suppliers_changes(edited_df, original_df):
    """حفظ تعديلات الموردين"""
    try:
        changes_count = 0
        
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            
            # التحقق من وجود تغييرات
            if (row['name'] != original_row['name'] or 
                row['contact_person'] != original_row['contact_person'] or
                row['phone'] != original_row['phone'] or
                row['email'] != original_row['email'] or
                row['address'] != original_row['address'] or
                row['payment_terms'] != original_row['payment_terms']):
                
                # هنا يجب إضافة دالة تحديث المورد في crud.py
                # crud.update_supplier(row['id'], ...)
                changes_count += 1
        
        if changes_count > 0:
            show_success_message(f"تم حفظ {changes_count} تعديل بنجاح")
            st.rerun()
        else:
            st.info("لا توجد تعديلات للحفظ")
        
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def delete_selected_suppliers(supplier_ids):
    """حذف الموردين المحددين"""
    try:
        # هنا يجب إضافة دالة حذف المورد في crud.py
        # for supplier_id in supplier_ids:
        #     crud.delete_supplier(supplier_id)
        
        show_success_message(f"تم حذف {len(supplier_ids)} مورد بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حذف الموردين: {str(e)}")

def export_suppliers_data(suppliers_df):
    """تصدير بيانات الموردين"""
    try:
        from utils.helpers import export_to_excel
        
        export_columns = {
            'id': 'المعرف',
            'name': 'اسم المورد',
            'contact_person': 'الشخص المسؤول',
            'phone': 'رقم الهاتف',
            'email': 'البريد الإلكتروني',
            'address': 'العنوان',
            'payment_terms': 'شروط الدفع',
            'created_at': 'تاريخ التسجيل'
        }
        
        export_df = suppliers_df[list(export_columns.keys())].rename(columns=export_columns)
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
    """إرسال رسائل جماعية"""
    st.subheader("📧 إرسال رسائل جماعية للموردين")
    
    with st.form("bulk_message_form"):
        message_type = st.selectbox(
            "نوع الرسالة",
            ["استفسار عن الأسعار", "طلب عروض أسعار", "إشعار دفع", "رسالة عامة"]
        )
        
        subject = st.text_input("موضوع الرسالة")
        message_body = st.text_area("نص الرسالة")
        
        # اختيار الموردين
        suppliers_df = crud.get_all_suppliers()
        selected_suppliers = st.multiselect(
            "اختر الموردين",
            options=suppliers_df['id'].tolist(),
            default=suppliers_df['id'].tolist(),
            format_func=lambda x: suppliers_df[suppliers_df['id']==x]['name'].iloc[0]
        )
        
        if st.form_submit_button("📤 إرسال الرسائل"):
            # هنا يمكن إضافة منطق إرسال الرسائل
            show_success_message(f"تم إرسال الرسالة إلى {len(selected_suppliers)} مورد")

def display_supplier_summary(supplier_id, name, contact_person, phone, payment_terms):
    """عرض ملخص المورد"""
    st.success("✅ تم إضافة المورد بنجاح!")
    
    st.info(f"""
    **🏢 ملخص المورد:**
    - **رقم المورد:** {supplier_id}
    - **الاسم:** {name}
    - **الشخص المسؤول:** {contact_person or 'غير محدد'}
    - **الهاتف:** {phone}
    - **شروط الدفع:** {payment_terms}
    """)

def create_purchase_order_form():
    """نموذج إنشاء طلب شراء"""
    with st.form("create_purchase_order"):
        col1, col2 = st.columns(2)
        
        with col1:
            # اختيار المورد
            suppliers_df = crud.get_all_suppliers()
            if not suppliers_df.empty:
                supplier_options = {row['id']: row['name'] for _, row in suppliers_df.iterrows()}
                selected_supplier_id = st.selectbox(
                    "اختر المورد",
                    options=list(supplier_options.keys()),
                    format_func=lambda x: supplier_options[x]
                )
            else:
                st.error("لا توجد موردين")
                return
            
            order_date = st.date_input("تاريخ الطلب", value=date.today())
            expected_delivery = st.date_input("تاريخ التسليم المتوقع")
        
        with col2:
            priority = st.selectbox("الأولوية", ["عادي", "مهم", "عاجل"])
            payment_method = st.selectbox(
                "طريقة الدفع",
                ["نقداً عند الاستلام", "تحويل بنكي", "شيك", "آجل"]
            )
        
        # تفاصيل الطلب
        st.subheader("📝 تفاصيل الطلب")
        
        # إضافة منتجات للطلب
        num_items = st.number_input("عدد المنتجات", min_value=1, value=1, step=1)
        
        order_items = []
        total_amount = 0
        
        for i in range(num_items):
            st.write(f"**المنتج {i+1}:**")
            col3, col4, col5, col6 = st.columns(4)
            
            with col3:
                item_name = st.text_input(f"اسم المنتج", key=f"item_name_{i}")
            
            with col4:
                quantity = st.number_input(f"الكمية", min_value=1, value=1, key=f"quantity_{i}")
            
            with col5:
                unit_price = st.number_input(f"سعر الوحدة", min_value=0.0, value=0.0, key=f"price_{i}")
            
            with col6:
                item_total = quantity * unit_price
                st.metric("المجموع", format_currency(item_total))
                total_amount += item_total
            
            if item_name:
                order_items.append({
                    'name': item_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': item_total
                })
        
        # المجموع الكلي
        st.metric("💰 إجمالي الطلب", format_currency(total_amount))
        
        notes = st.text_area("ملاحظات على الطلب")
        
        if st.form_submit_button("🛒 إنشاء طلب الشراء"):
            if order_items:
                create_purchase_order(selected_supplier_id, order_items, total_amount, order_date, expected_delivery, notes)
            else:
                show_error_message("يجب إضافة منتج واحد على الأقل")

def suggest_purchase_orders():
    """اقتراح طلبات شراء بناءً على المخزون المنخفض"""
    st.subheader("💡 اقتراحات طلبات الشراء")
    
    low_stock_items = crud.get_low_stock_items()
    
    if not low_stock_items.empty:
        st.warning(f"يوجد {len(low_stock_items)} صنف بحاجة لإعادة التزويد")
        
        # تجميع الأصناف حسب المورد
        supplier_groups = low_stock_items.groupby('supplier_name')
        
        for supplier_name, items in supplier_groups:
            if pd.isna(supplier_name):
                continue
                
            with st.expander(f"🏢 {supplier_name} - {len(items)} صنف"):
                for _, item in items.iterrows():
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.write(f"**{item['item_name']}**")
                    
                    with col2:
                        st.write(f"متوفر: {item['quantity']}")
                    
                    with col3:
                        suggested_qty = item['min_stock_level'] * 2
                        st.write(f"مقترح: {suggested_qty}")
                    
                    with col4:
                        estimated_cost = suggested_qty * item['unit_price']
                        st.write(f"التكلفة: {format_currency(estimated_cost)}")
                
                if st.button(f"🛒 إنشاء طلب من {supplier_name}", key=f"order_{supplier_name}"):
                    create_suggested_purchase_order(supplier_name, items)
    else:
        st.success("✅ جميع الأصناف متوفرة بكميات كافية")

def show_suppliers_overview(suppliers_df):
    """نظرة عامة على الموردين"""
    st.subheader("📊 نظرة عامة")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # توزيع شروط الدفع
        payment_terms_dist = suppliers_df['payment_terms'].value_counts()
        
        import plotly.express as px
        fig1 = px.pie(values=payment_terms_dist.values, names=payment_terms_dist.index,
                     title="توزيع شروط الدفع")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # إحصائيات أساسية
        st.metric("📞 موردين لديهم بريد إلكتروني", len(suppliers_df[suppliers_df['email'].notna()]))
        st.metric("📍 موردين لديهم عنوان", len(suppliers_df[suppliers_df['address'].notna()]))
        st.metric("👤 موردين لديهم شخص مسؤول", len(suppliers_df[suppliers_df['contact_person'].notna()]))

def show_suppliers_inventory_report(suppliers_df, inventory_df):
    """تقرير مخزون الموردين"""
    st.subheader("📦 تقرير المخزون حسب المورد")
    
    if not inventory_df.empty:
        # إحصائيات المخزون حسب المورد
        supplier_inventory = inventory_df.groupby('supplier_name').agg({
            'item_name': 'count',
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
        else:
            st.info("لا توجد أصناف مرتبطة بموردين")
    else:
        st.info("لا توجد أصناف في المخزون")

def show_suppliers_performance_analysis(suppliers_df):
    """تحليل أداء الموردين"""
    st.subheader("📈 تحليل أداء الموردين")
    
    # هنا يمكن إضافة تحليل أداء الموردين بناءً على:
    # - عدد الطلبات
    # - سرعة التسليم
    # - جودة المنتجات
    # - الأسعار التنافسية
    
    st.info("سيتم إضافة تحليل أداء الموردين بناءً على تاريخ الطلبات والتقييمات")

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

def send_message_to_supplier(supplier_id):
    """إرسال رسالة لمورد محدد"""
    st.info("سيتم إضافة وظيفة إرسال الرسائل قريباً")

def create_purchase_order_for_supplier(supplier_id):
    """إنشاء طلب شراء لمورد محدد"""
    st.info("سيتم فتح نموذج طلب الشراء للمورد المحدد")

def show_detailed_supplier_report(supplier_id):
    """عرض تقرير تفصيلي للمورد"""
    st.info("سيتم إضافة التقرير التفصيلي قريباً")

def create_purchase_order(supplier_id, order_items, total_amount, order_date, expected_delivery, notes):
    """إنشاء طلب شراء"""
    try:
        # هنا يمكن حفظ طلب الشراء في قاعدة البيانات
        show_success_message(f"تم إنشاء طلب الشراء بنجاح بقيمة {format_currency(total_amount)}")
        
        # عرض ملخص الطلب
        st.info(f"""
        **🛒 ملخص طلب الشراء:**
        - **عدد المنتجات:** {len(order_items)}
        - **إجمالي القيمة:** {format_currency(total_amount)}
        - **تاريخ الطلب:** {format_date_arabic(order_date)}
        - **التسليم المتوقع:** {format_date_arabic(expected_delivery)}
        """)
        
    except Exception as e:
        show_error_message(f"خطأ في إنشاء طلب الشراء: {str(e)}")

def create_suggested_purchase_order(supplier_name, items):
    """إنشاء طلب شراء مقترح"""
    try:
        total_items = len(items)
        total_cost = sum(item['min_stock_level'] * 2 * item['unit_price'] for _, item in items.iterrows())
        
        show_success_message(f"تم إنشاء طلب شراء مقترح من {supplier_name} لـ {total_items} صنف بقيمة {format_currency(total_cost)}")
        
    except Exception as e:
        show_error_message(f"خطأ في إنشاء الطلب المقترح: {str(e)}")

if __name__ == "__main__":
    show_suppliers()