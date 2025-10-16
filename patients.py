import streamlit as st
import pandas as pd
from datetime import date, datetime
from database.crud import crud
from utils.helpers import (
    validate_phone_number, validate_email, calculate_age,
    show_success_message, show_error_message, format_date_arabic
)

def show_patients():
    st.title("👥 إدارة المرضى")
    
    # شريط جانبي للخيارات
    st.sidebar.subheader("خيارات المرضى")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المرضى", "إضافة مريض جديد", "البحث عن مريض", "تقرير المرضى"]
    )
    
    if action == "عرض المرضى":
        show_patients_list()
    elif action == "إضافة مريض جديد":
        add_patient_form()
    elif action == "البحث عن مريض":
        search_patients()
    elif action == "تقرير المرضى":
        patients_report()

def show_patients_list():
    """عرض قائمة المرضى"""
    st.subheader("📋 قائمة المرضى")
    
    try:
        patients_df = crud.get_all_patients()
        
        if patients_df.empty:
            st.info("لا توجد بيانات مرضى")
            return
        
        # إضافة عمود العمر
        patients_df['age'] = patients_df['date_of_birth'].apply(
            lambda x: calculate_age(x) if pd.notna(x) else "غير محدد"
        )
        
        # عرض البيانات في جدول قابل للتحرير
        edited_df = st.data_editor(
            patients_df[['id', 'name', 'phone', 'email', 'gender', 'age', 'address']],
            column_config={
                'id': st.column_config.NumberColumn('المعرف', disabled=True),
                'name': st.column_config.TextColumn('الاسم', required=True),
                'phone': st.column_config.TextColumn('الهاتف'),
                'email': st.column_config.TextColumn('البريد الإلكتروني'),
                'gender': st.column_config.SelectboxColumn(
                    'الجنس',
                    options=['ذكر', 'أنثى']
                ),
                'age': st.column_config.TextColumn('العمر', disabled=True),
                'address': st.column_config.TextColumn('العنوان')
            },
            hide_index=True,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        # أزرار العمليات
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 حفظ التعديلات"):
                save_patients_changes(edited_df, patients_df)
        
        with col2:
            selected_rows = st.multiselect(
                "اختر مرضى للحذف",
                options=patients_df['id'].tolist(),
                format_func=lambda x: patients_df[patients_df['id']==x]['name'].iloc[0]
            )
            
            if st.button("🗑️ حذف المحدد") and selected_rows:
                delete_selected_patients(selected_rows)
        
        with col3:
            # تصدير البيانات
            if st.button("📊 تصدير إلى Excel"):
                export_patients_data(patients_df)
        
        # تفاصيل المريض
        st.divider()
        show_patient_details(patients_df)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل بيانات المرضى: {str(e)}")

def add_patient_form():
    """نموذج إضافة مريض جديد"""
    st.subheader("➕ إضافة مريض جديد")
    
    with st.form("add_patient_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("الاسم الكامل *", placeholder="أدخل الاسم الكامل")
            phone = st.text_input("رقم الهاتف", placeholder="01xxxxxxxxx")
            email = st.text_input("البريد الإلكتروني", placeholder="email@example.com")
            gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
        
        with col2:
            date_of_birth = st.date_input(
                "تاريخ الميلاد",
                max_value=date.today(),
                value=date.today().replace(year=date.today().year - 25)
            )
            address = st.text_area("العنوان", placeholder="أدخل العنوان كاملاً")
            emergency_contact = st.text_input("جهة الاتصال للطوارئ", placeholder="الاسم ورقم الهاتف")
        
        medical_history = st.text_area(
            "التاريخ المرضي", 
            placeholder="أي أمراض مزمنة، حساسية، أدوية يتم تناولها..."
        )
        
        submitted = st.form_submit_button("💾 حفظ المريض")
        
        if submitted:
            # التحقق من صحة البيانات
            errors = []
            
            if not name.strip():
                errors.append("الاسم مطلوب")
            
            if phone and not validate_phone_number(phone):
                errors.append("رقم الهاتف غير صحيح")
            
            if email and not validate_email(email):
                errors.append("البريد الإلكتروني غير صحيح")
            
            if errors:
                for error in errors:
                    show_error_message(error)
                return
            
            # حفظ المريض
            try:
                patient_id = crud.create_patient(
                    name=name.strip(),
                    phone=phone.strip() if phone else None,
                    email=email.strip() if email else None,
                    address=address.strip() if address else None,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    medical_history=medical_history.strip(),
                    emergency_contact=emergency_contact.strip() if emergency_contact else None
                )
                
                show_success_message(f"تم إضافة المريض {name} بنجاح (المعرف: {patient_id})")
                st.rerun()
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ المريض: {str(e)}")

def search_patients():
    """البحث عن المرضى"""
    st.subheader("🔍 البحث عن مريض")
    
    search_term = st.text_input("ابحث بالاسم أو الهاتف أو البريد الإلكتروني")
    
    if search_term:
        try:
            patients_df = crud.get_all_patients()
            
            # البحث في الأعمدة المختلفة
            mask = (
                patients_df['name'].str.contains(search_term, case=False, na=False) |
                patients_df['phone'].str.contains(search_term, case=False, na=False) |
                patients_df['email'].str.contains(search_term, case=False, na=False)
            )
            
            filtered_patients = patients_df[mask]
            
            if not filtered_patients.empty:
                st.write(f"تم العثور على {len(filtered_patients)} نتيجة:")
                
                for _, patient in filtered_patients.iterrows():
                    with st.expander(f"👤 {patient['name']} - {patient['phone']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**المعرف:** {patient['id']}")
                            st.write(f"**الاسم:** {patient['name']}")
                            st.write(f"**الهاتف:** {patient['phone']}")
                            st.write(f"**البريد:** {patient['email']}")
                        
                        with col2:
                            st.write(f"**الجنس:** {patient['gender']}")
                            st.write(f"**تاريخ الميلاد:** {patient['date_of_birth']}")
                            st.write(f"**العمر:** {calculate_age(patient['date_of_birth'])} سنة")
                            st.write(f"**العنوان:** {patient['address']}")
                        
                        if patient['medical_history']:
                            st.write(f"**التاريخ المرضي:** {patient['medical_history']}")
                        
                        if patient['emergency_contact']:
                            st.write(f"**جهة الطوارئ:** {patient['emergency_contact']}")
                        
                        # أزرار العمليات
                        col3, col4, col5 = st.columns(3)
                        with col3:
                            if st.button(f"✏️ تعديل", key=f"edit_{patient['id']}"):
                                edit_patient(patient['id'])
                        with col4:
                            if st.button(f"📅 مواعيد", key=f"appointments_{patient['id']}"):
                                show_patient_appointments(patient['id'])
                        with col5:
                            if st.button(f"🗑️ حذف", key=f"delete_{patient['id']}"):
                                delete_patient(patient['id'])
            else:
                st.info("لم يتم العثور على نتائج")
                
        except Exception as e:
            show_error_message(f"خطأ في البحث: {str(e)}")

def patients_report():
    """تقرير المرضى"""
    st.subheader("📊 تقرير المرضى")
    
    try:
        patients_df = crud.get_all_patients()
        
        if patients_df.empty:
            st.info("لا توجد بيانات مرضى")
            return
        
        # إحصائيات عامة
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_patients = len(patients_df)
            st.metric("👥 إجمالي المرضى", total_patients)
        
        with col2:
            male_patients = len(patients_df[patients_df['gender'] == 'ذكر'])
            st.metric("👨 الذكور", male_patients)
        
        with col3:
            female_patients = len(patients_df[patients_df['gender'] == 'أنثى'])
            st.metric("👩 الإناث", female_patients)
        
        with col4:
            # المرضى الجدد هذا الشهر
            current_month = datetime.now().month
            current_year = datetime.now().year
            patients_df['created_month'] = pd.to_datetime(patients_df['created_at']).dt.month
            patients_df['created_year'] = pd.to_datetime(patients_df['created_at']).dt.year
            new_patients = len(patients_df[
                (patients_df['created_month'] == current_month) & 
                (patients_df['created_year'] == current_year)
            ])
            st.metric("🆕 جدد هذا الشهر", new_patients)
        
        # رسم بياني للجنس
        st.subheader("توزيع المرضى حسب الجنس")
        gender_counts = patients_df['gender'].value_counts()
        
        import plotly.express as px
        fig = px.pie(values=gender_counts.values, names=gender_counts.index,
                     title="توزيع المرضى حسب الجنس")
        st.plotly_chart(fig, use_container_width=True)
        
        # توزيع الأعمار
        st.subheader("توزيع الأعمار")
        patients_df['age'] = patients_df['date_of_birth'].apply(calculate_age)
        
        # تجميع الأعمار في فئات
        age_groups = pd.cut(patients_df['age'], 
                           bins=[0, 18, 30, 50, 70, 100], 
                           labels=['أقل من 18', '18-29', '30-49', '50-69', '70+'])
        
        age_distribution = age_groups.value_counts().sort_index()
        
        fig = px.bar(x=age_distribution.index, y=age_distribution.values,
                     title="توزيع المرضى حسب الفئة العمرية",
                     labels={'x': 'الفئة العمرية', 'y': 'عدد المرضى'})
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        show_error_message(f"خطأ في تحميل التقرير: {str(e)}")

def show_patient_details(patients_df):
    """عرض تفاصيل مريض محدد"""
    st.subheader("👁️ تفاصيل المريض")
    
    patient_names = {row['id']: row['name'] for _, row in patients_df.iterrows()}
    selected_patient_id = st.selectbox(
        "اختر مريض لعرض التفاصيل",
        options=list(patient_names.keys()),
        format_func=lambda x: patient_names[x]
    )
    
    if selected_patient_id:
        patient = patients_df[patients_df['id'] == selected_patient_id].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **👤 البيانات الأساسية**
            - **الاسم:** {patient['name']}
            - **الهاتف:** {patient['phone'] or 'غير محدد'}
            - **البريد:** {patient['email'] or 'غير محدد'}
            - **الجنس:** {patient['gender']}
            - **العمر:** {calculate_age(patient['date_of_birth'])} سنة
            """)
        
        with col2:
            st.info(f"""
            **📍 معلومات إضافية**
            - **تاريخ الميلاد:** {format_date_arabic(patient['date_of_birth'])}
            - **العنوان:** {patient['address'] or 'غير محدد'}
            - **جهة الطوارئ:** {patient['emergency_contact'] or 'غير محدد'}
            - **تاريخ التسجيل:** {format_date_arabic(patient['created_at'][:10])}
            """)
        
        if patient['medical_history']:
            st.warning(f"**📋 التاريخ المرضي:**\n{patient['medical_history']}")

def save_patients_changes(edited_df, original_df):
    """حفظ تعديلات المرضى"""
    try:
        # مقارنة البيانات وحفظ التغييرات
        for idx, row in edited_df.iterrows():
            original_row = original_df[original_df['id'] == row['id']].iloc[0]
            
            # التحقق من وجود تغييرات
            if (row['name'] != original_row['name'] or 
                row['phone'] != original_row['phone'] or
                row['email'] != original_row['email'] or
                row['address'] != original_row['address']):
                
                # تحديث المريض
                crud.update_patient(
                    patient_id=row['id'],
                    name=row['name'],
                    phone=row['phone'],
                    email=row['email'],
                    address=row['address'],
                    date_of_birth=original_row['date_of_birth'],
                    gender=row['gender'],
                    medical_history=original_row['medical_history'],
                    emergency_contact=original_row['emergency_contact']
                )
        
        show_success_message("تم حفظ التعديلات بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حفظ التعديلات: {str(e)}")

def delete_selected_patients(patient_ids):
    """حذف المرضى المحددين"""
    try:
        for patient_id in patient_ids:
            crud.delete_patient(patient_id)
        
        show_success_message(f"تم حذف {len(patient_ids)} مريض بنجاح")
        st.rerun()
        
    except Exception as e:
        show_error_message(f"خطأ في حذف المرضى: {str(e)}")

def export_patients_data(patients_df):
    """تصدير بيانات المرضى"""
    try:
        from utils.helpers import export_to_excel
        
        # إضافة عمود العمر
        patients_df['العمر'] = patients_df['date_of_birth'].apply(calculate_age)
        
        # تحديد الأعمدة للتصدير
        export_columns = {
            'id': 'المعرف',
            'name': 'الاسم',
            'phone': 'الهاتف',
            'email': 'البريد الإلكتروني',
            'gender': 'الجنس',
            'العمر': 'العمر',
            'address': 'العنوان',
            'medical_history': 'التاريخ المرضي',
            'emergency_contact': 'جهة الطوارئ',
            'created_at': 'تاريخ التسجيل'
        }
        
        export_df = patients_df[list(export_columns.keys())].rename(columns=export_columns)
        excel_data = export_to_excel(export_df, "patients_report")
        
        st.download_button(
            label="📥 تحميل Excel",
            data=excel_data,
            file_name=f"patients_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        show_error_message(f"خطأ في التصدير: {str(e)}")

if __name__ == "__main__":
    show_patients()