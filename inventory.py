import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message
)

def show_inventory():
    st.title("📦 إدارة المخزون")
    st.sidebar.subheader("خيارات المخزون")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المخزون", "إضافة عنصر جديد", "تنبيهات المخزون المنخفض"]
    )
    if action == "عرض المخزون":
        show_inventory_list()
    elif action == "إضافة عنصر جديد":
        add_inventory_form()
    elif action == "تنبيهات المخزون المنخفض":
        show_low_stock()

def show_inventory_list():
    st.subheader("📋 قائمة المخزون")
    try:
        inventory_df = crud.get_all_inventory()
        if inventory_df.empty:
            st.info("لا يوجد عناصر في المخزون")
            return
        categories = ['الكل'] + list(inventory_df['category'].unique())
        selected_category = st.selectbox("فلترة حسب الفئة", categories)
        filtered_df = inventory_df if selected_category == 'الكل' else inventory_df[inventory_df['category'] == selected_category]
        edited_df = st.data_editor(
            filtered_df[['id', 'item_name', 'category', 'quantity', 'unit_price', 'min_stock_level', 'expiry_date']],
            column_config={
                'id': st.column_config.NumberColumn('المعرف', disabled=True),
                'item_name': st.column_config.TextColumn('اسم العنصر', required=True),
                'category': st.column_config.TextColumn('الفئة'),
                'quantity': st.column_config.NumberColumn('الكمية', min_value=0),
                'unit_price': st.column_config.NumberColumn('سعر الوحدة (ج.م)', min_value=0.0, format="%.2f ج.م"),
                'min_stock_level': st.column_config.NumberColumn('الحد الأدنى', min_value=0),
                'expiry_date': st.column_config.DateColumn('تاريخ الانتهاء', format="YYYY-MM-DD")
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 حفظ التعديلات"):
                save_inventory_changes(edited_df, inventory_df)
        with col2:
            if st.button("📊 تصدير إلى Excel"):
                export_inventory_data(filtered_df)
    except Exception as e:
        show_error_message(f"خطأ في تحميل بيانات المخزون: {str(e)}")

def add_inventory_form():
    st.subheader("➕ إضافة عنصر جديد إلى المخزون")
    with st.form("add_inventory_form"):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("اسم العنصر *", placeholder="مثال: قفازات طبية")
            category = st.text_input("الفئة", placeholder="مثال: مستهلكات")
            quantity = st.number_input("الكمية *", min_value=0, value=0)
        with col2:
            unit_price = st.number_input("سعر الوحدة (ج.م)", min_value=0.0, value=0.0, step=0.1)
            min_stock_level = st.number_input("الحد الأدنى للمخزون", min_value=0, value=10)
            expiry_date = st.date_input("تاريخ الانتهاء", min_value=date.today(), value=None)
        submitted = st.form_submit_button("💾 حفظ العنصر الجديد")
        if submitted:
            if not item_name or quantity < 0:
                show_error_message("يجب إدخال اسم العنصر وكمية صالحة")
            else:
                conn = crud.db.get_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, expiry_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (item_name, category, quantity, unit_price, min_stock_level, expiry_date))
                conn.commit()
                conn.close()
                show_success_message(f"تم إضافة العنصر {item_name} بنجاح")
                st.rerun()

def save_inventory_changes(edited_df, original_df):
    try:
        conn = crud.db.get_connection()
        cursor = conn.cursor()
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            if any(row[col] != original_row[col] for col in ['item_name', 'category', 'quantity', 'unit_price', 'min_stock_level', 'expiry_date']):
                cursor.execute('''
                    UPDATE inventory 
                    SET item_name=?, category=?, quantity=?, unit_price=?, min_stock_level=?, expiry_date=?
                    WHERE id=?
                ''', (row['item_name'], row['category'], row['quantity'], row['unit_price'], row['min_stock_level'], row['expiry_date'], row['id']))
        conn.commit()
        conn.close()
        show_success_message("تم حفظ التعديلات بنجاح")
        st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def export_inventory_data(inventory_df):
    try:
        from utils.helpers import export_to_excel
        export_columns = {
            'id': 'المعرف',
            'item_name': 'اسم العنصر',
            'category': 'الفئة',
            'quantity': 'الكمية',
            'unit_price': 'سعر الوحدة (ج.م)',
            'min_stock_level': 'الحد الأدنى',
            'expiry_date': 'تاريخ الانتهاء'
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

def show_low_stock():
    st.subheader("⚠️ تنبيهات المخزون المنخفض")
    try:
        low_stock_df = crud.get_low_stock_items()
        if low_stock_df.empty:
            st.success("✅ لا توجد عناصر دون الحد الأدنى")
            return
        st.dataframe(
            low_stock_df[['item_name', 'category', 'quantity', 'min_stock_level']],
            column_config={
                'item_name': 'اسم العنصر',
                'category': 'الفئة',
                'quantity': 'الكمية الحالية',
                'min_stock_level': 'الحد الأدنى'
            },
            hide_index=True,
            use_container_width=True
        )
    except Exception as e:
        show_error_message(f"خطأ في تحميل تنبيهات المخزون: {str(e)}")

if __name__ == "__main__":
    show_inventory()
