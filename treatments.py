import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, show_error_message
)

def show_treatments():
    st.title("💊 إدارة العلاجات والخدمات")
    st.sidebar.subheader("خيارات العلاجات")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض العلاجات", "إضافة علاج جديد", "تحليل العلاجات", "أسعار العلاجات"]
    )
    if action == "عرض العلاجات":
        show_treatments_list()
    elif action == "إضافة علاج جديد":
        add_treatment_form()
    elif action == "تحليل العلاجات":
        treatments_analysis()
    elif action == "أسعار العلاجات":
        treatments_pricing()

def show_treatments_list():
    """عرض قائمة العلاجات"""
    st.subheader("📋 قائمة العلاجات المتاحة")
    try:
        treatments_df = crud.get_all_treatments()
        if treatments_df.empty:
            st.info("لا توجد علاجات متاحة")
            return
        categories = ['الكل'] + list(treatments_df['category'].unique())
        selected_category = st.selectbox("فلترة حسب الفئة", categories)
        if selected_category != 'الكل':
            treatments_df = treatments_df[treatments_df['category'] == selected_category]
        edited_df = st.data_editor(
            treatments_df[['id', 'name', 'description', 'base_price', 'duration_minutes', 'category', 'commission_rate']],
            column_config={
                'id': st.column_config.NumberColumn('المعرف', disabled=True),
                'name': st.column_config.TextColumn('اسم العلاج', required=True),
                'description': st.column_config.TextColumn('الوصف'),
                'base_price': st.column_config.NumberColumn(
                    'السعر الأساسي (ج.م)',
                    min_value=0.0,
                    format="%.2f ج.م"
                ),
                'duration_minutes': st.column_config.NumberColumn(
                    'المدة (دقيقة)',
                    min_value=0,
                    max_value=300
                ),
                'category': st.column_config.SelectboxColumn(
                    'الفئة',
                    options=['وقائي', 'علاجي', 'جراحي', 'تقويمي', 'تجميلي', 'طوارئ']
                ),
                'commission_rate': st.column_config.NumberColumn(
                    'نسبة العمولة للطبيب %',
                    min_value=0.0,
                    max_value=100.0,
                    format="%.1f%%"
                )
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("💾 حفظ التعديلات"):
                save_treatments_changes(edited_df, treatments_df)
        with col2:
            selected_rows = st.multiselect(
                "اختر علاجات للحذف",
                options=treatments_df['id'].tolist(),
                format_func=lambda x: treatments_df[treatments_df['id']==x]['name'].iloc[0]
            )
            if st.button("🗑️ حذف المحدد") and selected_rows:
                delete_selected_treatments(selected_rows)
        with col3:
            if st.button("📊 تصدير إلى Excel"):
                export_treatments_data(treatments_df)
        with col4:
            if st.button("💰 تحديث الأسعار"):
                update_prices_bulk()
        st.divider()
        show_treatments_stats(treatments_df)
    except Exception as e:
        show_error_message(f"خطأ في تحميل بيانات العلاجات: {str(e)}")

def add_treatment_form():
    """نموذج إضافة علاج جديد"""
    st.subheader("➕ إضافة علاج أو خدمة جديدة")
    with st.form("add_treatment_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم العلاج *", placeholder="مثال: فحص وتنظيف")
            base_price = st.number_input(
                "السعر الأساسي (ج.م) *",
                min_value=0.0,
                value=200.0,
                step=50.0
            )
            duration_minutes = st.number_input(
                "مدة العلاج (بالدقائق)",
                min_value=0,
                max_value=300
            )
        with col2:
            description = st.text_area("الوصف", placeholder="وصف العلاج")
            category = st.selectbox(
                "الفئة *",
                ['وقائي', 'علاجي', 'جراحي', 'تقويمي', 'تجميلي', 'طوارئ']
            )
            commission_rate = st.number_input(
                "نسبة العمولة للطبيب % *",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=5.0
            )
        submitted = st.form_submit_button("💾 حفظ العلاج الجديد")
        if submitted:
            if not name or base_price <= 0:
                show_error_message("يجب إدخال اسم وسعر صالح")
            else:
                treatment_id = crud.create_treatment(
                    name=name,
                    description=description,
                    base_price=base_price,
                    duration_minutes=duration_minutes,
                    category=category,
                    commission_rate=commission_rate
                )
                show_success_message(f"تم إضافة العلاج رقم {treatment_id} بنجاح")
                st.rerun()

def save_treatments_changes(edited_df, original_df):
    """حفظ تعديلات العلاجات"""
    try:
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            if (row['name'] != original_row['name'] or 
                row['description'] != original_row['description'] or
                row['base_price'] != original_row['base_price'] or
                row['duration_minutes'] != original_row['duration_minutes'] or
                row['category'] != original_row['category'] or
                row['commission_rate'] != original_row['commission_rate']):
                crud.update_treatment(
                    treatment_id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    base_price=row['base_price'],
                    duration_minutes=row['duration_minutes'],
                    category=row['category'],
                    commission_rate=row['commission_rate']
                )
        show_success_message("تم حفظ التعديلات بنجاح")
        st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def delete_selected_treatments(treatment_ids):
    """حذف العلاجات المحددة (تعطيل)"""
    try:
        for treatment_id in treatment_ids:
            crud.delete_treatment(treatment_id)
        show_success_message(f"تم تعطيل {len(treatment_ids)} علاج بنجاح")
        st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في الحذف: {str(e)}")

def export_treatments_data(treatments_df):
    """تصدير بيانات العلاجات"""
    try:
        from utils.helpers import export_to_excel
        export_columns = {
            'id': 'المعرف',
            'name': 'الاسم',
            'description': 'الوصف',
            'base_price': 'السعر',
            'duration_minutes': 'المدة',
            'category': 'الفئة',
            'commission_rate': 'نسبة العمولة %',
            'created_at': 'تاريخ التسجيل'
        }
        export_df = treatments_df[list(export_columns.keys())].rename(columns=export_columns)
        excel_data = export_to_excel(export_df, "treatments_report")
        st.download_button(
            label="📥 تحميل Excel",
            data=excel_data,
            file_name=f"treatments_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        show_error_message(f"خطأ في التصدير: {str(e)}")

def show_treatments_stats(treatments_df):
    """عرض إحصائيات العلاجات"""
    col1, col2, col3 = st.columns(3)
    with col1:
        total_treatments = len(treatments_df)
        st.metric("💊 إجمالي العلاجات", total_treatments)
    with col2:
        avg_price = treatments_df['base_price'].mean()
        st.metric("💰 متوسط السعر", format_currency(avg_price))
    with col3:
        avg_commission = treatments_df['commission_rate'].mean()
        st.metric("📈 متوسط العمولة", f"{avg_commission:.1f}%")

def treatments_analysis():
    """تحليل العلاجات"""
    st.subheader("📊 تحليل العلاجات")
    try:
        treatments_df = crud.get_all_treatments()
        if treatments_df.empty:
            st.info("لا توجد بيانات علاجات للتحليل")
            return
        import plotly.express as px
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("توزيع الأسعار حسب الفئة")
            fig_price = px.box(treatments_df, x='category', y='base_price', title="توزيع أسعار العلاجات")
            st.plotly_chart(fig_price, use_container_width=True)
        with col2:
            st.subheader("توزيع العلاجات حسب الفئة")
            category_counts = treatments_df['category'].value_counts()
            fig_category = px.pie(category_counts, names=category_counts.index, values='count', title="توزيع الفئات")
            st.plotly_chart(fig_category, use_container_width=True)
    except Exception as e:
        show_error_message(f"خطأ في تحليل العلاجات: {str(e)}")

def treatments_pricing():
    """إدارة أسعار العلاجات"""
    st.subheader("💰 إدارة أسعار العلاجات")
    try:
        treatments_df = crud.get_all_treatments()
        if treatments_df.empty:
            st.info("لا توجد علاجات متاحة")
            return
        st.write("### تحديث الأسعار")
        with st.form("update_pricing_form"):
            price_change_type = st.selectbox("نوع التغيير", ["زيادة", "تخفيض"])
            price_change_percent = st.number_input("نسبة التغيير (%)", min_value=0.0, max_value=100.0, value=10.0, step=5.0)
            selected_category = st.selectbox("الفئة", ['الكل'] + list(treatments_df['category'].unique()))
            submitted = st.form_submit_button("💾 تطبيق التغيير")
            if submitted:
                updated_df = treatments_df.copy()
                if selected_category != 'الكل':
                    updated_df = updated_df[updated_df['category'] == selected_category]
                factor = 1 + (price_change_percent / 100) if price_change_type == "زيادة" else 1 - (price_change_percent / 100)
                updated_df['base_price'] = updated_df['base_price'] * factor
                for _, row in updated_df.iterrows():
                    crud.update_treatment(
                        treatment_id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        base_price=row['base_price'],
                        duration_minutes=row['duration_minutes'],
                        category=row['category'],
                        commission_rate=row['commission_rate']
                    )
                show_success_message(f"تم تحديث أسعار العلاجات بنسبة {price_change_percent}%")
                st.rerun()
    except Exception as e:
        show_error_message(f"خطأ في تحديث الأسعار: {str(e)}")

def update_prices_bulk():
    """تحديث جماعي للأسعار"""
    treatments_pricing()

if __name__ == "__main__":
    show_treatments()
