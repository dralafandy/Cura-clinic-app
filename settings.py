import streamlit as st
from database.crud import crud
from database.models import db

def render():
    """صفحة الإعدادات"""
    st.markdown("### ⚙️ إعدادات النظام")
    
    tab1, tab2 = st.tabs(["🏥 معلومات العيادة", "💾 النسخ الاحتياطي"])
    
    with tab1:
        render_clinic_info()
    
    with tab2:
        render_backup()

def render_clinic_info():
    """معلومات العيادة"""
    st.markdown("#### معلومات العيادة")
    
    settings = crud.get_all_settings()
    
    if not settings.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            clinic_name = st.text_input(
                "اسم العيادة",
                value=settings[settings['key'] == 'clinic_name']['value'].iloc[0] if 'clinic_name' in settings['key'].values else ""
            )
            
            clinic_phone = st.text_input(
                "هاتف العيادة",
                value=settings[settings['key'] == 'clinic_phone']['value'].iloc[0] if 'clinic_phone' in settings['key'].values else ""
            )
            
            clinic_email = st.text_input(
                "بريد العيادة",
                value=settings[settings['key'] == 'clinic_email']['value'].iloc[0] if 'clinic_email' in settings['key'].values else ""
            )
        
        with col2:
            clinic_address = st.text_area(
                "عنوان العيادة",
                value=settings[settings['key'] == 'clinic_address']['value'].iloc[0] if 'clinic_address' in settings['key'].values else ""
            )
            
            working_hours = st.text_input(
                "ساعات العمل",
                value=settings[settings['key'] == 'working_hours']['value'].iloc[0] if 'working_hours' in settings['key'].values else ""
            )
        
        if st.button("💾 حفظ الإعدادات", type="primary"):
            try:
                crud.update_setting('clinic_name', clinic_name)
                crud.update_setting('clinic_phone', clinic_phone)
                crud.update_setting('clinic_email', clinic_email)
                crud.update_setting('clinic_address', clinic_address)
                crud.update_setting('working_hours', working_hours)
                
                st.success("✅ تم حفظ الإعدادات بنجاح!")
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
        
        # عرض جميع الإعدادات
        st.markdown("---")
        st.markdown("#### جميع الإعدادات")
        st.dataframe(settings, use_container_width=True, hide_index=True)

def render_backup():
    """النسخ الاحتياطي"""
    st.markdown("#### النسخ الاحتياطي")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 💾 إنشاء نسخة احتياطية")
        st.info("يمكنك إنشاء نسخة احتياطية من قاعدة البيانات لحفظ جميع البيانات")
        
        if st.button("📥 إنشاء نسخة احتياطية", type="primary", use_container_width=True):
            backup_path = db.backup_database()
            if backup_path:
                st.success(f"✅ تم إنشاء نسخة احتياطية بنجاح!\n\nالملف: {backup_path}")
            else:
                st.error("❌ فشل إنشاء النسخة الاحتياطية")
    
    with col2:
        st.markdown("##### ℹ️ معلومات")
        st.warning("""
        **تنبيه مهم:**
        - يتم حفظ النسخة الاحتياطية في نفس مجلد التطبيق
        - احفظ النسخة الاحتياطية في مكان آمن
        - يُنصح بإنشاء نسخ احتياطية دورية
        - النسخ الاحتياطية تساعد في استعادة البيانات عند الحاجة
        """)
