import streamlit as st
from database.crud import crud

def render():
    """صفحة سجل الأنشطة"""
    st.markdown("### 📝 سجل الأنشطة")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("سجل جميع العمليات التي تمت على النظام")
    
    with col2:
        limit = st.selectbox("عدد السجلات", [50, 100, 200, 500], index=1)
    
    activity_log = crud.get_activity_log(limit=limit)
    
    if not activity_log.empty:
        st.dataframe(
            activity_log.rename(columns={
                'id': 'الرقم',
                'action': 'العملية',
                'table_name': 'الجدول',
                'record_id': 'رقم السجل',
                'details': 'التفاصيل',
                'user_name': 'المستخدم',
                'created_at': 'التاريخ'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # إحصائيات
        st.markdown("---")
        st.markdown("### 📊 إحصائيات النشاط")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("إجمالي الأنشطة", len(activity_log))
        
        with col2:
            if 'action' in activity_log.columns:
                most_common = activity_log['action'].value_counts().index[0]
                st.metric("أكثر عملية", most_common)
        
        with col3:
            if 'table_name' in activity_log.columns:
                most_used_table = activity_log['table_name'].value_counts().index[0]
                st.metric("أكثر جدول استخداماً", most_used_table)
    else:
        st.info("لا يوجد سجل أنشطة")
