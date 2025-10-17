import streamlit as st
from datetime import date
from database.crud import crud

def render():
    """صفحة إدارة المخزون"""
    st.markdown("### 📦 إدارة المخزون")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 جميع العناصر", "➕ عنصر جديد", "⚠️ مخزون منخفض", "📅 قريب الانتهاء"])
    
    with tab1:
        render_all_inventory()
    
    with tab2:
        render_add_inventory()
    
    with tab3:
        render_low_stock()
    
    with tab4:
        render_expiring_items()

def render_all_inventory():
    """عرض جميع عناصر المخزون"""
    inventory = crud.get_all_inventory()
    if not inventory.empty:
        st.dataframe(
            inventory[['id', 'item_name', 'category', 'quantity', 'unit_price', 
                      'min_stock_level', 'supplier_name', 'expiry_date', 'location']],
            use_container_width=True,
            hide_index=True
        )
        
        # إحصائيات
        col1, col2, col3 = st.columns(3)
        with col1:
            total_items = len(inventory)
            st.metric("إجمالي الأصناف", total_items)
        with col2:
            total_value = (inventory['quantity'] * inventory['unit_price']).sum()
            st.metric("قيمة المخزون", f"{total_value:,.0f} ج.م")
        with col3:
            low_stock_count = len(inventory[inventory['quantity'] <= inventory['min_stock_level']])
            st.metric("أصناف منخفضة", low_stock_count)
    else:
        st.info("لا توجد عناصر في المخزون")

def render_add_inventory():
    """نموذج إضافة عنصر جديد"""
    st.markdown("#### إضافة عنصر جديد")
    
    suppliers = crud.get_all_suppliers()
    
    col1, col2 = st.columns(2)
    
    with col1:
        item_name = st.text_input("اسم العنصر*")
        category = st.selectbox("التصنيف", ["مستهلكات", "أدوية", "أجهزة", "مواد طبية", "منتجات", "أخرى"])
        quantity = st.number_input("الكمية*", min_value=0, step=1)
        unit_price = st.number_input("سعر الوحدة (ج.م)", min_value=0.0, step=1.0)
        min_stock_level = st.number_input("الحد الأدنى للمخزون", min_value=0, value=10, step=1)
    
    with col2:
        location = st.text_input("الموقع/المخزن", placeholder="مثال: مخزن A")
        barcode = st.text_input("الباركود", placeholder="اختياري")
        expiry_date = st.date_input("تاريخ انتهاء الصلاحية", min_value=date.today())
        
        supplier_id = st.selectbox(
            "المورد",
            [None] + suppliers['id'].tolist() if not suppliers.empty else [None],
            format_func=lambda x: "بدون مورد" if x is None else suppliers[suppliers['id'] == x]['name'].iloc[0]
        ) if not suppliers.empty else None
    
    if st.button("إضافة العنصر", type="primary", use_container_width=True):
        if item_name and quantity >= 0:
            try:
                crud.create_inventory_item(
                    item_name, category, quantity, unit_price,
                    min_stock_level, supplier_id,
                    expiry_date.isoformat() if expiry_date else None,
                    location, barcode
                )
                st.success("✅ تم إضافة العنصر بنجاح!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
        else:
            st.warning("الرجاء ملء الحقول المطلوبة")

def render_low_stock():
    """عرض الأصناف منخفضة المخزون"""
    low_stock = crud.get_low_stock_items()
    if not low_stock.empty:
        st.warning(f"⚠️ يوجد {len(low_stock)} عنصر بمخزون منخفض")
        st.dataframe(
            low_stock[['item_name', 'category', 'quantity', 'min_stock_level', 'supplier_name']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ جميع العناصر في المستوى الآمن")

def render_expiring_items():
    """عرض الأصناف قريبة الانتهاء"""
    expiring = crud.get_expiring_inventory(days=60)
    if not expiring.empty:
        st.warning(f"📅 يوجد {len(expiring)} صنف ينتهي خلال 60 يوم")
        
        st.dataframe(
            expiring.rename(columns={
                'item_name': 'الصنف',
                'category': 'الفئة',
                'quantity': 'الكمية',
                'expiry_date': 'تاريخ الانتهاء',
                'supplier_name': 'المورد',
                'days_to_expire': 'الأيام المتبقية'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ لا توجد أصناف قريبة من الانتهاء")
