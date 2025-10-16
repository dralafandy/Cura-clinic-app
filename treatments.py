import streamlit as st
import pandas as pd
from datetime import date
from database.crud import crud
from utils.helpers import (
    format_currency, show_success_message, 
    show_error_message, format_date_arabic
)

def show_treatments():
    st.title("💊 إدارة العلاجات والخدمات")
    
    # شريط جانبي للخيارات
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
        
        # إضافة فلترة حسب الفئة
        categories = ['الكل'] + list(treatments_df['category'].unique())
        selected_category = st.selectbox("فلترة حسب الفئة", categories)
        
        if selected_category != 'الكل':
            treatments_df = treatments_df[treatments_df['category'] == selected_category]
        
        # عرض البيانات في جدول قابل للتحرير
        edited_df = st.data_editor(
            treatments_df[['id', 'name', 'description', 'base_price', 'duration_minutes', 'category']],
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
        
        # إحصائيات سريعة
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
                value=60,
                step=15
            )
        
        with col2:
            category = st.selectbox(
                "فئة العلاج *",
                ['وقائي', 'علاجي', 'جراحي', 'تقويمي', 'تجميلي', 'طوارئ']
            )
            
            # معلومات إضافية للفئة المختارة
            if category == 'وقائي':
                st.info("🛡️ العلاجات الوقائية: فحص، تنظيف، فلوريد")
            elif category == 'علاجي':
                st.info("🦷 العلاجات الطبية: حشو، علاج عصب، تلبيس")
            elif category == 'جراحي':
                st.info("🔬 العلاجات الجراحية: خلع، زراعة، جراحة لثة")
            elif category == 'تقويمي':
                st.info("📐 علاجات التقويم: تقويم معدني، شفاف، متحرك")
            elif category == 'تجميلي':
                st.info("✨ العلاجات التجميلية: تبييض، فينيرز، ابتسامة هوليود")
            elif category == 'طوارئ':
                st.info("🚨 علاجات الطوارئ: تسكين ألم، علاج التهاب")
        
        description = st.text_area(
            "وصف العلاج",
            placeholder="وصف مفصل للعلاج والإجراءات المتضمنة..."
        )
        
        # خيارات متقدمة
        with st.expander("خيارات متقدمة"):
            col3, col4 = st.columns(2)
            
            with col3:
                requires_anesthesia = st.checkbox("يتطلب تخدير")
                requires_followup = st.checkbox("يتطلب متابعة")
            
            with col4:
                complexity_level = st.selectbox(
                    "مستوى التعقيد",
                    ["بسيط", "متوسط", "معقد"]
                )
                max_sessions = st.number_input(
                    "الحد الأقصى للجلسات",
                    min_value=1,
                    value=1
                )
        
        submitted = st.form_submit_button("💾 حفظ العلاج")
        
        if submitted:
            # التحقق من صحة البيانات
            errors = []
            
            if not name.strip():
                errors.append("اسم العلاج مطلوب")
            
            if base_price <= 0:
                errors.append("السعر يجب أن يكون أكبر من صفر")
            
            # التحقق من عدم تكرار الاسم
            existing_treatments = crud.get_all_treatments()
            if not existing_treatments.empty and name.strip() in existing_treatments['name'].values:
                errors.append("اسم العلاج موجود مسبقاً")
            
            if errors:
                for error in errors:
                    show_error_message(error)
                return
            
            # حفظ العلاج
            try:
                treatment_id = crud.create_treatment(
                    name=name.strip(),
                    description=description.strip() if description else None,
                    base_price=base_price,
                    duration_minutes=duration_minutes,
                    category=category
                )
                
                show_success_message(f"تم إضافة العلاج '{name}' بنجاح (المعرف: {treatment_id})")
                st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ العلاج: {str(e)}")

def treatments_analysis():
    """تحليل العلاجات والخدمات"""
    st.subheader("📊 تحليل العلاجات")
    
    try:
        treatments_df = crud.get_all_treatments()
        appointments_df = crud.get_all_appointments()
        
        if treatments_df.empty:
            st.info("لا توجد علاجات لتحليلها")
            return
        
        # فلترة التواريخ
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("من تاريخ", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("إلى تاريخ", value=date.today())
        
        # تحليل شعبية العلاجات
        if not appointments_df.empty:
            # فلترة المواعيد حسب التاريخ
            appointments_df['appointment_date'] = pd.to_datetime(appointments_df['appointment_date']).dt.date
            filtered_appointments = appointments_df[
                (appointments_df['appointment_date'] >= start_date) & 
                (appointments_df['appointment_date'] <= end_date)
            ]
            
            if not filtered_appointments.empty:
                # العلاجات الأكثر طلباً
                treatment_popularity = filtered_appointments['treatment_name'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🏆 العلاجات الأكثر طلباً")
                    
                    import plotly.express as px
                    
                    fig1 = px.bar(
                        x=treatment_popularity.values[:10],
                        y=treatment_popularity.index[:10],
                        orientation='h',
                        title="أكثر 10 علاجات طلباً"
                    )
                    fig1.update_layout(
                        xaxis_title="عدد المواعيد",
                        yaxis_title="العلاج"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    st.subheader("💰 الإيرادات حسب العلاج")
                    
                    treatment_revenue = filtered_appointments.groupby('treatment_name')['total_cost'].sum().sort_values(ascending=False)
                    
                    fig2 = px.pie(
                        values=treatment_revenue.values[:8],
                        names=treatment_revenue.index[:8],
                        title="توزيع الإيرادات حسب العلاج"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # تحليل الفئات
                st.divider()
                st.subheader("📈 تحليل فئات العلاجات")
                
                # ربط العلاجات بفئاتها
                treatment_category_map = dict(zip(treatments_df['name'], treatments_df['category']))
                filtered_appointments['category'] = filtered_appointments['treatment_name'].map(treatment_category_map)
                
                category_stats = filtered_appointments.groupby('category').agg({
                    'id': 'count',
                    'total_cost': 'sum'
                }).round(2)
                category_stats.columns = ['عدد المواعيد', 'إجمالي الإيرادات']
                category_stats = category_stats.reset_index()
                category_stats.columns = ['الفئة', 'عدد المواعيد', 'إجمالي الإيرادات']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig3 = px.bar(
                        category_stats,
                        x='الفئة',
                        y='عدد المواعيد',
                        title='عدد المواعيد حسب فئة العلاج'
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                
                with col2:
                    fig4 = px.bar(
                        category_stats,
                        x='الفئة',
                        y='إجمالي الإيرادات',
                        title='الإيرادات حسب فئة العلاج'
                    )
                    st.plotly_chart(fig4, use_container_width=True)
                
                # جدول التحليل التفصيلي
                st.subheader("📋 تحليل تفصيلي")
                st.dataframe(
                    category_stats,
                    column_config={
                        'إجمالي الإيرادات': st.column_config.NumberColumn(
                            'إجمالي الإيرادات',
                            format="%.2f ج.م"
                        )
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            else:
                st.info("لا توجد مواعيد في هذه الفترة")
        else:
            st.info("لا توجد مواعيد لتحليلها")
        
        # تحليل أسعار العلاجات
        st.divider()
        st.subheader("💲 تحليل أسعار العلاجات")
        
        price_stats = treatments_df.groupby('category')['base_price'].agg(['mean', 'min', 'max']).round(2)
        price_stats.columns = ['متوسط السعر', 'أقل سعر', 'أعلى سعر']
        price_stats = price_stats.reset_index()
        price_stats.columns = ['الفئة', 'متوسط السعر', 'أقل سعر', 'أعلى سعر']
        
        st.dataframe(
            price_stats,
            column_config={
                'متوسط السعر': st.column_config.NumberColumn(format="%.2f ج.م"),
                'أقل سعر': st.column_config.NumberColumn(format="%.2f ج.م"),
                'أعلى سعر': st.column_config.NumberColumn(format="%.2f ج.م")
            },
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        show_error_message(f"خطأ في تحليل العلاجات: {str(e)}")

def treatments_pricing():
    """إدارة أسعار العلاجات"""
    st.subheader("💰 إدارة أسعار العلاجات")
    
    try:
        treatments_df = crud.get_all_treatments()
        
        if treatments_df.empty:
            st.info("لا توجد علاجات")
            return
        
        # قائمة الأسعار الحالية
        st.write("📋 قائمة الأسعار الحالية")
        
        # تجميع حسب الفئة
        for category in treatments_df['category'].unique():
            with st.expander(f"📁 فئة: {category}"):
                category_treatments = treatments_df[treatments_df['category'] == category]
                
                for _, treatment in category_treatments.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{treatment['name']}**")
                        if treatment['description']:
                            st.caption(treatment['description'])
                    
                    with col2:
                        st.metric(
                            "السعر الحالي",
                            format_currency(treatment['base_price'])
                        )
                    
                    with col3:
                        new_price = st.number_input(
                            "سعر جديد",
                            min_value=0.0,
                            value=float(treatment['base_price']),
                            step=50.0,
                            key=f"price_{treatment['id']}"
                        )
                        
                        if st.button(f"تحديث", key=f"update_{treatment['id']}"):
                            update_treatment_price(treatment['id'], new_price)
        
        # تحديث أسعار بالنسبة المئوية
        st.divider()
        st.subheader("📈 تحديث أسعار بالنسبة المئوية")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_category_for_update = st.selectbox(
                "اختر الفئة",
                ['جميع الفئات'] + list(treatments_df['category'].unique())
            )
        
        with col2:
            percentage_change = st.number_input(
                "نسبة التغيير (%)",
                value=0.0,
                step=1.0,
                help="رقم موجب للزيادة، سالب للتقليل"
            )
        
        with col3:
            st.write("")  # مسافة فارغة
            st.write("")
            if st.button("🔄 تطبيق التحديث"):
                apply_percentage_update(selected_category_for_update, percentage_change)
        
        # معاينة التحديث
        if percentage_change != 0:
            st.subheader("👀 معاينة التحديث")
            
            preview_df = treatments_df.copy()
            if selected_category_for_update != 'جميع الفئات':
                preview_df = preview_df[preview_df['category'] == selected_category_for_update]
            
            preview_df['السعر الجديد'] = preview_df['base_price'] * (1 + percentage_change / 100)
            preview_df['التغيير'] = preview_df['السعر الجديد'] - preview_df['base_price']
            
            st.dataframe(
                preview_df[['name', 'category', 'base_price', 'السعر الجديد', 'التغيير']],
                column_config={
                    'name': 'اسم العلاج',
                    'category': 'الفئة',
                    'base_price': st.column_config.NumberColumn('السعر الحالي', format="%.2f ج.م"),
                    'السعر الجديد': st.column_config.NumberColumn('السعر الجديد', format="%.2f ج.م"),
                    'التغيير': st.column_config.NumberColumn('التغيير', format="+%.2f ج.م")
                },
                use_container_width=True,
                hide_index=True
            )
        
    except Exception as e:
        show_error_message(f"خطأ في إدارة الأسعار: {str(e)}")

def show_treatments_stats(treatments_df):
    """عرض إحصائيات العلاجات"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_treatments = len(treatments_df)
        st.metric("💊 إجمالي العلاجات", total_treatments)
    
    with col2:
        avg_price = treatments_df['base_price'].mean()
        st.metric("💰 متوسط السعر", format_currency(avg_price))
    
    with col3:
        max_price = treatments_df['base_price'].max()
        st.metric("📈 أعلى سعر", format_currency(max_price))
    
    with col4:
        categories_count = treatments_df['category'].nunique()
        st.metric("📁 عدد الفئات", categories_count)

def save_treatments_changes(edited_df, original_df):
    """حفظ تعديلات العلاجات"""
    try:
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            
            # التحقق من وجود تغييرات
            if (row['name'] != original_row['name'] or 
                row['description'] != original_row['description'] or
                row['base_price'] != original_row['base_price'] or
                row['duration_minutes'] != original_row['duration_minutes'] or
                row['category'] != original_row['category']):
                
                crud.update_treatment(
                    treatment_id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    base_price=row['base_price'],
                    duration_minutes=row['duration_minutes'],
                    category=row['category']
                )
        
        show_success_message("تم حفظ التعديلات بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def delete_selected_treatments(treatment_ids):
    """حذف العلاجات المحددة"""
    try:
        for treatment_id in treatment_ids:
            crud.delete_treatment(treatment_id)
        
        show_success_message(f"تم إلغاء تفعيل {len(treatment_ids)} علاج بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حذف العلاجات: {str(e)}")

def export_treatments_data(treatments_df):
    """تصدير بيانات العلاجات"""
    try:
        from utils.helpers import export_to_excel
        
        export_columns = {
            'id': 'المعرف',
            'name': 'اسم العلاج',
            'description': 'الوصف',
            'base_price': 'السعر الأساسي',
            'duration_minutes': 'المدة (دقيقة)',
            'category': 'الفئة',
            'created_at': 'تاريخ الإضافة'
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

def update_treatment_price(treatment_id, new_price):
    """تحديث سعر علاج واحد"""
    try:
        treatment = crud.get_treatment_by_id(treatment_id)
        
        crud.update_treatment(
            treatment_id=treatment_id,
            name=treatment[1],  # name
            description=treatment[2],  # description
            base_price=new_price,
            duration_minutes=treatment[4],  # duration_minutes
            category=treatment[5]  # category
        )
        
        show_success_message(f"تم تحديث سعر العلاج إلى {format_currency(new_price)}")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في تحديث السعر: {str(e)}")

def apply_percentage_update(category, percentage):
    """تطبيق تحديث نسبة مئوية على الأسعار"""
    try:
        treatments_df = crud.get_all_treatments()
        
        if category != 'جميع الفئات':
            treatments_df = treatments_df[treatments_df['category'] == category]
        
        updated_count = 0
        
        for _, treatment in treatments_df.iterrows():
            new_price = treatment['base_price'] * (1 + percentage / 100)
            new_price = round(new_price, 2)  # تقريب لأقرب قرشين
            
            crud.update_treatment(
                treatment_id=treatment['id'],
                name=treatment['name'],
                description=treatment['description'],
                base_price=new_price,
                duration_minutes=treatment['duration_minutes'],
                category=treatment['category']
            )
            
            updated_count += 1
        
        show_success_message(f"تم تحديث أسعار {updated_count} علاج بنسبة {percentage:+.1f}%")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في تحديث الأسعار: {str(e)}")

def update_prices_bulk():
    """تحديث أسعار متعددة"""
    st.subheader("🔄 تحديث أسعار متعددة")
    
    with st.form("bulk_price_update"):
        st.write("رفع ملف CSV بالأسعار الجديدة")
        st.write("تنسيق الملف: treatment_id, new_price")
        
        uploaded_file = st.file_uploader(
            "اختر ملف CSV",
            type=['csv'],
            help="الملف يجب أن يحتوي على عمودين: treatment_id, new_price"
        )
        
        if uploaded_file and st.form_submit_button("📤 تحديث الأسعار"):
            try:
                import pandas as pd
                
                df = pd.read_csv(uploaded_file)
                
                if 'treatment_id' not in df.columns or 'new_price' not in df.columns:
                    show_error_message("الملف يجب أن يحتوي على عمودي treatment_id و new_price")
                    return
                
                updated_count = 0
                
                for _, row in df.iterrows():
                    treatment_id = int(row['treatment_id'])
                    new_price = float(row['new_price'])
                    
                    treatment = crud.get_treatment_by_id(treatment_id)
                    if treatment:
                        crud.update_treatment(
                            treatment_id=treatment_id,
                            name=treatment[1],
                            description=treatment[2],
                            base_price=new_price,
                            duration_minutes=treatment[4],
                            category=treatment[5]
                        )
                        updated_count += 1
                
                show_success_message(f"تم تحديث أسعار {updated_count} علاج بنجاح")
                st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في معالجة الملف: {str(e)}")

if __name__ == "__main__":
    show_treatments()