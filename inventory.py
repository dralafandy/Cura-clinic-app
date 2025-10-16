import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message, 
    format_date_arabic, create_inventory_alert_chart
)

def show_inventory():
    st.title("📦 إدارة المخزون")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات المخزون")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المخزون", "إضافة صنف جديد", "تنبيهات المخزون", "حركة المخزون", "تقارير المخزون"]
    )
    
    if action == "عرض المخزون":
        show_inventory_list()
    elif action == "إضافة صنف جديد":
        add_inventory_item()
    elif action == "تنبيهات المخزون":
        inventory_alerts()
    elif action == "حركة المخزون":
        inventory_movements()
    elif action == "تقارير المخزون":
        inventory_reports()

def show_inventory_list():
    """عرض قائمة المخزون"""
    st.subheader("📋 قائمة المخزون")
    
    try:
        inventory_df = crud.get_all_inventory()
        
        if inventory_df.empty:
            st.info("لا توجد أصناف في المخزون")
            return
        
        # فلاتر البحث والتصفية
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # فلترة حسب الفئة
            categories = ["الكل"] + list(inventory_df['category'].unique())
            selected_category = st.selectbox("فلترة حسب الفئة", categories)
        
        with col2:
            # فلترة حسب حالة المخزون
            stock_status = st.selectbox(
                "حالة المخزون",
                ["الكل", "مخزون كافي", "مخزون منخفض", "مخزون منتهي"]
            )
        
        with col3:
            # فلترة حسب تاريخ الانتهاء
            expiry_filter = st.selectbox(
                "تاريخ الانتهاء",
                ["الكل", "منتهي الصلاحية", "ينتهي قريباً", "صالح"]
            )
        
        # تطبيق الفلاتر
        filtered_df = apply_inventory_filters(inventory_df, selected_category, stock_status, expiry_filter)
        
        if filtered_df.empty:
            st.info("لا توجد أصناف تطابق المعايير المحددة")
            return
        
        # عرض الإحصائيات السريعة
        show_inventory_summary(filtered_df)
        
        # عرض البيانات في جدول قابل للتحرير
        edited_df = st.data_editor(
            filtered_df[['id', 'item_name', 'category', 'quantity', 'unit_price', 
                        'min_stock_level', 'supplier_name', 'expiry_date']],
            column_config={
                'id': st.column_config.NumberColumn('المعرف', disabled=True),
                'item_name': st.column_config.TextColumn('اسم الصنف', required=True),
                'category': st.column_config.SelectboxColumn(
                    'الفئة',
                    options=['مستهلكات', 'أدوية', 'مواد علاجية', 'أدوات جراحية', 'معدات', 'أخرى']
                ),
                'quantity': st.column_config.NumberColumn(
                    'الكمية الحالية',
                    min_value=0,
                    step=1
                ),
                'unit_price': st.column_config.NumberColumn(
                    'سعر الوحدة (ج.م)',
                    min_value=0.0,
                    format="%.2f ج.م"
                ),
                'min_stock_level': st.column_config.NumberColumn(
                    'الحد الأدنى',
                    min_value=0,
                    step=1
                ),
                'supplier_name': st.column_config.TextColumn('المورد'),
                'expiry_date': st.column_config.DateColumn('تاريخ الانتهاء')
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # أزرار العمليات
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 حفظ التعديلات"):
                save_inventory_changes(edited_df, filtered_df)
        
        with col2:
            if st.button("📊 تصدير إلى Excel"):
                export_inventory_data(filtered_df)
        
        with col3:
            if st.button("📥 استيراد البيانات"):
                import_inventory_data()
        
        with col4:
            if st.button("🔄 جرد المخزون"):
                inventory_count()
        
        # عرض التنبيهات
        show_inventory_alerts_inline(filtered_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل بيانات المخزون: {str(e)}")

def add_inventory_item():
    """إضافة صنف جديد للمخزون"""
    st.subheader("➕ إضافة صنف جديد للمخزون")
    
    with st.form("add_inventory_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            item_name = st.text_input("اسم الصنف *", placeholder="مثال: قفازات طبية")
            category = st.selectbox(
                "فئة الصنف *",
                ['مستهلكات', 'أدوية', 'مواد علاجية', 'أدوات جراحية', 'معدات', 'أخرى']
            )
            quantity = st.number_input(
                "الكمية الابتدائية *",
                min_value=0,
                value=0,
                step=1
            )
            unit_price = st.number_input(
                "سعر الوحدة (ج.م) *",
                min_value=0.0,
                value=0.0,
                step=0.1
            )
        
        with col2:
            min_stock_level = st.number_input(
                "الحد الأدنى للمخزون *",
                min_value=0,
                value=10,
                step=1,
                help="سيتم إرسال تنبيه عند الوصول لهذا الحد"
            )
            
            # اختيار المورد
            suppliers_df = crud.get_all_suppliers()
            if not suppliers_df.empty:
                supplier_options = {0: "بدون مورد"}
                supplier_options.update({row['id']: row['name'] for _, row in suppliers_df.iterrows()})
                
                selected_supplier_id = st.selectbox(
                    "المورد",
                    options=list(supplier_options.keys()),
                    format_func=lambda x: supplier_options[x]
                )
                
                if selected_supplier_id == 0:
                    selected_supplier_id = None
            else:
                selected_supplier_id = None
                st.info("لا توجد موردين. يمكنك إضافة الموردين من قسم إدارة الموردين")
            
            expiry_date = st.date_input(
                "تاريخ انتهاء الصلاحية",
                value=None,
                help="اتركه فارغاً إذا لم يكن للصنف تاريخ انتهاء"
            )
        
        # معلومات إضافية
        with st.expander("معلومات إضافية"):
            col3, col4 = st.columns(2)
            
            with col3:
                batch_number = st.text_input("رقم الدفعة")
                storage_location = st.text_input("مكان التخزين")
            
            with col4:
                reorder_point = st.number_input(
                    "نقطة إعادة الطلب",
                    min_value=0,
                    value=min_stock_level,
                    step=1
                )
                max_stock_level = st.number_input(
                    "الحد الأقصى للمخزون",
                    min_value=0,
                    value=min_stock_level * 5,
                    step=1
                )
        
        description = st.text_area(
            "وصف الصنف",
            placeholder="وصف مفصل للصنف، الاستخدامات، التعليمات الخاصة..."
        )
        
        submitted = st.form_submit_button("💾 حفظ الصنف")
        
        if submitted:
            # التحقق من صحة البيانات
            errors = []
            
            if not item_name.strip():
                errors.append("اسم الصنف مطلوب")
            
            if unit_price < 0:
                errors.append("سعر الوحدة لا يمكن أن يكون سالباً")
            
            if quantity < 0:
                errors.append("الكمية لا يمكن أن تكون سالبة")
            
            # التحقق من عدم تكرار الاسم
            existing_items = crud.get_all_inventory()
            if not existing_items.empty and item_name.strip() in existing_items['item_name'].values:
                errors.append("اسم الصنف موجود مسبقاً")
            
            if errors:
                for error in errors:
                    show_error_message(error)
                return
            
            # حفظ الصنف
            try:
                item_id = crud.create_inventory_item(
                    item_name=item_name.strip(),
                    category=category,
                    quantity=quantity,
                    unit_price=unit_price,
                    min_stock_level=min_stock_level,
                    supplier_id=selected_supplier_id,
                    expiry_date=expiry_date if expiry_date else None
                )
                
                show_success_message(f"تم إضافة الصنف '{item_name}' بنجاح (المعرف: {item_id})")
                st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ الصنف: {str(e)}")

def inventory_alerts():
    """تنبيهات المخزون"""
    st.subheader("⚠️ تنبيهات المخزون")
    
    try:
        inventory_df = crud.get_all_inventory()
        
        if inventory_df.empty:
            st.info("لا توجد أصناف في المخزون")
            return
        
        # تنبيهات المخزون المنخفض
        low_stock_items = crud.get_low_stock_items()
        
        if not low_stock_items.empty:
            st.error(f"🚨 **تنبيه: {len(low_stock_items)} صنف بحاجة لإعادة التزويد**")
            
            for _, item in low_stock_items.iterrows():
                with st.expander(f"⚠️ {item['item_name']} - الكمية: {item['quantity']}/{item['min_stock_level']}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**الفئة:** {item['category']}")
                        st.write(f"**الكمية الحالية:** {item['quantity']}")
                        st.write(f"**الحد الأدنى:** {item['min_stock_level']}")
                    
                    with col2:
                        st.write(f"**سعر الوحدة:** {format_currency(item['unit_price'])}")
                        total_value = item['quantity'] * item['unit_price']
                        st.write(f"**القيمة الإجمالية:** {format_currency(total_value)}")
                        
                        if item['supplier_name']:
                            st.write(f"**المورد:** {item['supplier_name']}")
                    
                    with col3:
                        # خيارات سريعة
                        new_quantity = st.number_input(
                            "إضافة كمية",
                            min_value=0,
                            step=1,
                            key=f"add_qty_{item['id']}"
                        )
                        
                        if st.button(f"➕ إضافة", key=f"add_btn_{item['id']}"):
                            update_inventory_quantity(item['id'], item['quantity'] + new_quantity)
                        
                        if st.button(f"📞 طلب من المورد", key=f"order_btn_{item['id']}"):
                            create_purchase_order(item['id'])
        else:
            st.success("✅ جميع الأصناف في المخزون ضمن الحد المطلوب")
        
        # تنبيهات انتهاء الصلاحية
        st.divider()
        st.subheader("📅 تنبيهات انتهاء الصلاحية")
        
        # الأصناف منتهية الصلاحية
        expired_items = inventory_df[
            (inventory_df['expiry_date'].notna()) &
            (pd.to_datetime(inventory_df['expiry_date']).dt.date <= date.today())
        ]
        
        if not expired_items.empty:
            st.error(f"🚨 **{len(expired_items)} صنف منتهي الصلاحية**")
            
            for _, item in expired_items.iterrows():
                st.error(f"❌ **{item['item_name']}** - انتهت الصلاحية في {format_date_arabic(item['expiry_date'])}")
        
        # الأصناف التي تنتهي صلاحيتها قريباً
        soon_expiry = inventory_df[
            (inventory_df['expiry_date'].notna()) &
            (pd.to_datetime(inventory_df['expiry_date']).dt.date > date.today()) &
            (pd.to_datetime(inventory_df['expiry_date']).dt.date <= date.today() + timedelta(days=30))
        ]
        
        if not soon_expiry.empty:
            st.warning(f"⚠️ **{len(soon_expiry)} صنف ينتهي خلال 30 يوم**")
            
            for _, item in soon_expiry.iterrows():
                days_left = (pd.to_datetime(item['expiry_date']).date() - date.today()).days
                st.warning(f"⏰ **{item['item_name']}** - ينتهي خلال {days_left} يوم")
        
        if expired_items.empty and soon_expiry.empty:
            st.success("✅ جميع الأصناف صالحة ولا تنتهي قريباً")
        
        # رسم بياني للتنبيهات
        if not low_stock_items.empty:
            st.divider()
            st.subheader("📊 مخطط تنبيهات المخزون")
            
            alert_chart = create_inventory_alert_chart(low_stock_items)
            if alert_chart:
                st.plotly_chart(alert_chart, use_container_width=True)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل التنبيهات: {str(e)}")

def inventory_movements():
    """حركة المخزون"""
    st.subheader("📈 حركة المخزون")
    
    try:
        # نموذج تسجيل حركة
        with st.expander("➕ تسجيل حركة جديدة"):
            with st.form("inventory_movement_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # اختيار الصنف
                    inventory_df = crud.get_all_inventory()
                    if not inventory_df.empty:
                        item_options = {row['id']: f"{row['item_name']} (متوفر: {row['quantity']})" 
                                       for _, row in inventory_df.iterrows()}
                        
                        selected_item_id = st.selectbox(
                            "اختر الصنف",
                            options=list(item_options.keys()),
                            format_func=lambda x: item_options[x]
                        )
                    else:
                        st.error("لا توجد أصناف في المخزون")
                        selected_item_id = None
                
                with col2:
                    movement_type = st.selectbox(
                        "نوع الحركة",
                        ["إضافة", "استخدام", "تلف", "إرجاع", "تعديل"]
                    )
                
                col3, col4 = st.columns(2)
                
                with col3:
                    quantity = st.number_input(
                        "الكمية",
                        min_value=1,
                        step=1
                    )
                
                with col4:
                    movement_date = st.date_input(
                        "تاريخ الحركة",
                        value=date.today()
                    )
                
                notes = st.text_area("ملاحظات")
                
                submitted = st.form_submit_button("💾 تسجيل الحركة")
                
                if submitted and selected_item_id:
                    register_inventory_movement(selected_item_id, movement_type, quantity, movement_date, notes)
        
        # عرض سجل الحركات
        st.subheader("📋 سجل حركة المخزون")
        
        # فلترة حسب التاريخ
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("إلى تاريخ", value=date.today())
        
        # هنا يمكن إضافة جدول حركة المخزون من قاعدة البيانات
        # (يحتاج إلى إنشاء جدول inventory_movements في قاعدة البيانات)
        
        st.info("سجل حركة المخزون سيتم إضافته قريباً")
        
    except Exception as e:
        show_error_message(f"خطأ في حركة المخزون: {str(e)}")

def inventory_reports():
    """تقارير المخزون"""
    st.subheader("📊 تقارير المخزون")
    
    try:
        inventory_df = crud.get_all_inventory()
        
        if inventory_df.empty:
            st.info("لا توجد بيانات مخزون")
            return
        
        # إحصائيات عامة
        show_inventory_statistics(inventory_df)
        
        # تحليل قيمة المخزون
        st.divider()
        show_inventory_value_analysis(inventory_df)
        
        # توزيع المخزون حسب الفئة
        st.divider()
        show_inventory_category_distribution(inventory_df)
        
        # تقرير الموردين
        st.divider()
        show_suppliers_inventory_report(inventory_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل التقارير: {str(e)}")

# الدوال المساعدة

def apply_inventory_filters(inventory_df, category_filter, stock_filter, expiry_filter):
    """تطبيق فلاتر المخزون"""
    filtered_df = inventory_df.copy()
    
    # فلترة حسب الفئة
    if category_filter != "الكل":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    
    # فلترة حسب حالة المخزون
    if stock_filter != "الكل":
        if stock_filter == "مخزون منخفض":
            filtered_df = filtered_df[filtered_df['quantity'] <= filtered_df['min_stock_level']]
        elif stock_filter == "مخزون منتهي":
            filtered_df = filtered_df[filtered_df['quantity'] == 0]
        elif stock_filter == "مخزون كافي":
            filtered_df = filtered_df[filtered_df['quantity'] > filtered_df['min_stock_level']]
    
    # فلترة حسب تاريخ الانتهاء
    if expiry_filter != "الكل":
        today = date.today()
        
        if expiry_filter == "منتهي الصلاحية":
            filtered_df = filtered_df[
                (filtered_df['expiry_date'].notna()) &
                (pd.to_datetime(filtered_df['expiry_date']).dt.date <= today)
            ]
        elif expiry_filter == "ينتهي قريباً":
            filtered_df = filtered_df[
                (filtered_df['expiry_date'].notna()) &
                (pd.to_datetime(filtered_df['expiry_date']).dt.date > today) &
                (pd.to_datetime(filtered_df['expiry_date']).dt.date <= today + timedelta(days=30))
            ]
        elif expiry_filter == "صالح":
            filtered_df = filtered_df[
                (filtered_df['expiry_date'].isna()) |
                (pd.to_datetime(filtered_df['expiry_date']).dt.date > today + timedelta(days=30))
            ]
    
    return filtered_df

def show_inventory_summary(inventory_df):
    """عرض ملخص المخزون"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_items = len(inventory_df)
        st.metric("📦 إجمالي الأصناف", total_items)
    
    with col2:
        total_value = (inventory_df['quantity'] * inventory_df['unit_price']).sum()
        st.metric("💰 قيمة المخزون", format_currency(total_value))
    
    with col3:
        low_stock_count = len(inventory_df[inventory_df['quantity'] <= inventory_df['min_stock_level']])
        st.metric("⚠️ أصناف منخفضة", low_stock_count)
    
    with col4:
        out_of_stock = len(inventory_df[inventory_df['quantity'] == 0])
        st.metric("❌ أصناف منتهية", out_of_stock)

def show_inventory_alerts_inline(inventory_df):
    """عرض التنبيهات السريعة"""
    low_stock_count = len(inventory_df[inventory_df['quantity'] <= inventory_df['min_stock_level']])
    
    if low_stock_count > 0:
        st.warning(f"⚠️ يوجد {low_stock_count} صنف بحاجة لإعادة التزويد")

def save_inventory_changes(edited_df, original_df):
    """حفظ تعديلات المخزون"""
    try:
        changes_count = 0
        
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            
            # التحقق من وجود تغييرات
            if (row['quantity'] != original_row['quantity'] or 
                row['unit_price'] != original_row['unit_price'] or
                row['min_stock_level'] != original_row['min_stock_level']):
                
                # تحديث الكمية في قاعدة البيانات
                crud.update_inventory_quantity(row['id'], row['quantity'])
                changes_count += 1
        
        if changes_count > 0:
            show_success_message(f"تم حفظ {changes_count} تعديل بنجاح")
            st.rerun()
        else:
            st.info("لا توجد تعديلات للحفظ")
        
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def update_inventory_quantity(item_id, new_quantity):
    """تحديث كمية المخزون"""
    try:
        crud.update_inventory_quantity(item_id, new_quantity)
        show_success_message("تم تحديث الكمية بنجاح")
        st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في تحديث الكمية: {str(e)}")

def create_purchase_order(item_id):
    """إنشاء طلب شراء"""
    st.info("سيتم إضافة وظيفة طلبات الشراء قريباً")

def register_inventory_movement(item_id, movement_type, quantity, movement_date, notes):
    """تسجيل حركة مخزون"""
    try:
        # الحصول على الكمية الحالية
        inventory_df = crud.get_all_inventory()
        current_item = inventory_df[inventory_df['id'] == item_id].iloc[0]
        current_quantity = current_item['quantity']
        
        # حساب الكمية الجديدة
        if movement_type in ["إضافة", "إرجاع"]:
            new_quantity = current_quantity + quantity
        elif movement_type in ["استخدام", "تلف"]:
            new_quantity = max(0, current_quantity - quantity)
        else:  # تعديل
            new_quantity = quantity
        
        # تحديث الكمية
        crud.update_inventory_quantity(item_id, new_quantity)
        
        # هنا يمكن إضافة تسجيل الحركة في جدول منفصل
        
        show_success_message(f"تم تسجيل حركة {movement_type} بكمية {quantity} بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في تسجيل الحركة: {str(e)}")

def export_inventory_data(inventory_df):
    """تصدير بيانات المخزون"""
    try:
        from utils.helpers import export_to_excel
        
        # إضافة عمود القيمة الإجمالية
        inventory_df['القيمة الإجمالية'] = inventory_df['quantity'] * inventory_df['unit_price']
        
        export_columns = {
            'id': 'المعرف',
            'item_name': 'اسم الصنف',
            'category': 'الفئة',
            'quantity': 'الكمية',
            'unit_price': 'سعر الوحدة',
            'القيمة الإجمالية': 'القيمة الإجمالية',
            'min_stock_level': 'الحد الأدنى',
            'supplier_name': 'المورد',
            'expiry_date': 'تاريخ الانتهاء',
            'created_at': 'تاريخ الإضافة'
        }
        
        export_df = inventory_df[list(export_columns.keys())].rename(columns=export_columns)
        excel_data = export_to_excel(export_df, "inventory_report")
        
        st.download_button(
            label="📥 تحميل Excel",
            data=excel_data,
            file_name=f"inventory_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        show_error_message(f"خطأ في التصدير: {str(e)}")

def import_inventory_data():
    """استيراد بيانات المخزون"""
    st.subheader("📤 استيراد بيانات المخزون")
    
    with st.form("import_inventory"):
        st.info("""
        **تنسيق الملف المطلوب:**
        - item_name: اسم الصنف
        - category: الفئة
        - quantity: الكمية
        - unit_price: سعر الوحدة
        - min_stock_level: الحد الأدنى
        """)
        
        uploaded_file = st.file_uploader("اختر ملف Excel", type=['xlsx', 'csv'])
        
        if uploaded_file and st.form_submit_button("📤 استيراد البيانات"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # التحقق من الأعمدة المطلوبة
                required_columns = ['item_name', 'category', 'quantity', 'unit_price', 'min_stock_level']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    show_error_message(f"الأعمدة المفقودة: {', '.join(missing_columns)}")
                    return
                
                imported_count = 0
                
                for _, row in df.iterrows():
                    try:
                        crud.create_inventory_item(
                            item_name=row['item_name'],
                            category=row['category'],
                            quantity=int(row['quantity']),
                            unit_price=float(row['unit_price']),
                            min_stock_level=int(row['min_stock_level'])
                        )
                        imported_count += 1
                    except Exception as item_error:
                        st.warning(f"خطأ في استيراد الصنف '{row['item_name']}': {str(item_error)}")
                
                show_success_message(f"تم استيراد {imported_count} صنف بنجاح")
                st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في معالجة الملف: {str(e)}")

def inventory_count():
    """جرد المخزون"""
    st.subheader("🔍 جرد المخزون")
    st.info("سيتم إضافة وظيفة الجرد الإلكتروني قريباً")

def show_inventory_statistics(inventory_df):
    """عرض إحصائيات المخزون"""
    st.subheader("📊 إحصائيات عامة")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_items = len(inventory_df)
        st.metric("📦 إجمالي الأصناف", total_items)
    
    with col2:
        total_quantity = inventory_df['quantity'].sum()
        st.metric("📊 إجمالي الكميات", f"{total_quantity:,}")
    
    with col3:
        avg_price = inventory_df['unit_price'].mean()
        st.metric("💰 متوسط السعر", format_currency(avg_price))
    
    with col4:
        categories_count = inventory_df['category'].nunique()
        st.metric("📁 عدد الفئات", categories_count)

def show_inventory_value_analysis(inventory_df):
    """تحليل قيمة المخزون"""
    st.subheader("💰 تحليل قيمة المخزون")
    
    inventory_df['total_value'] = inventory_df['quantity'] * inventory_df['unit_price']
    
    col1, col2 = st.columns(2)
    
    with col1:
        total_value = inventory_df['total_value'].sum()
        st.metric("💸 إجمالي قيمة المخزون", format_currency(total_value))
        
        # أعلى قيمة
        highest_value_item = inventory_df.loc[inventory_df['total_value'].idxmax()]
        st.info(f"**أعلى قيمة:** {highest_value_item['item_name']} - {format_currency(highest_value_item['total_value'])}")
    
    with col2:
        avg_item_value = inventory_df['total_value'].mean()
        st.metric("📈 متوسط قيمة الصنف", format_currency(avg_item_value))
        
        # أقل قيمة
        lowest_value_item = inventory_df.loc[inventory_df['total_value'].idxmin()]
        st.info(f"**أقل قيمة:** {lowest_value_item['item_name']} - {format_currency(lowest_value_item['total_value'])}")

def show_inventory_category_distribution(inventory_df):
    """توزيع المخزون حسب الفئة"""
    st.subheader("📊 توزيع المخزون حسب الفئة")
    
    import plotly.express as px
    
    category_stats = inventory_df.groupby('category').agg({
        'quantity': 'sum',
        'unit_price': 'mean'
    }).round(2)
    
    category_stats['total_value'] = inventory_df.groupby('category')['quantity'].sum() * category_stats['unit_price']
    category_stats = category_stats.reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.pie(category_stats, values='quantity', names='category',
                     title="توزيع الكميات حسب الفئة")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.bar(category_stats, x='category', y='total_value',
                     title="قيمة المخزون حسب الفئة")
        st.plotly_chart(fig2, use_container_width=True)

def show_suppliers_inventory_report(inventory_df):
    """تقرير المخزون حسب الموردين"""
    st.subheader("👥 تقرير الموردين")
    
    suppliers_stats = inventory_df.groupby('supplier_name').agg({
        'item_name': 'count',
        'quantity': 'sum'
    }).round(2)
    
    suppliers_stats.columns = ['عدد الأصناف', 'إجمالي الكميات']
    suppliers_stats = suppliers_stats.reset_index()
    suppliers_stats.columns = ['المورد', 'عدد الأصناف', 'إجمالي الكميات']
    
    # إزالة الصفوف الفارغة
    suppliers_stats = suppliers_stats[suppliers_stats['المورد'].notna()]
    
    if not suppliers_stats.empty:
        st.dataframe(suppliers_stats, use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد أصناف مرتبطة بموردين")

if __name__ == "__main__":
    show_inventory()