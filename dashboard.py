import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from database.crud import crud

def render():
    """صفحة لوحة التحكم الرئيسية"""
    st.markdown("""
        <div class='main-header'>
            <h1>🏥 لوحة معلومات العيادة</h1>
            <p>مرحباً بك في نظام إدارة العيادة المتكامل</p>
        </div>
    """, unsafe_allow_html=True)
    
    # الإحصائيات الرئيسية
    stats = crud.get_dashboard_stats()
    financial_summary = crud.get_financial_summary()
    
    # البطاقات الإحصائية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card success'>
                <div class='metric-label'>👥 إجمالي المرضى</div>
                <div class='metric-value'>{stats['total_patients']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card info'>
                <div class='metric-label'>👨‍⚕️ عدد الأطباء</div>
                <div class='metric-value'>{stats['total_doctors']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='metric-card warning'>
                <div class='metric-label'>📅 مواعيد اليوم</div>
                <div class='metric-value'>{stats['today_appointments']}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>💰 صافي الربح</div>
                <div class='metric-value'>{financial_summary['net_profit']:,.0f}</div>
                <div class='metric-label'>جنيه مصري</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # الصف الثاني - الملخص المالي
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 الإيرادات", f"{financial_summary['total_revenue']:,.0f} ج.م")
    
    with col2:
        st.metric("💸 المصروفات", f"{financial_summary['total_expenses']:,.0f} ج.م")
    
    with col3:
        st.metric("📅 المواعيد القادمة", f"{stats['upcoming_appointments']} موعد")
    
    with col4:
        profit_margin = (financial_summary['net_profit'] / financial_summary['total_revenue'] * 100) if financial_summary['total_revenue'] > 0 else 0
        st.metric("📈 هامش الربح", f"{profit_margin:.1f}%")
    
    st.markdown("---")
    
    # الصف الثالث - رسوم بيانية
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 الإيرادات والمصروفات")
        
        financial_data = pd.DataFrame({
            'الفئة': ['الإيرادات', 'المصروفات', 'صافي الربح'],
            'المبلغ': [
                financial_summary['total_revenue'],
                financial_summary['total_expenses'],
                financial_summary['net_profit']
            ]
        })
        
        fig = px.bar(
            financial_data,
            x='الفئة',
            y='المبلغ',
            color='الفئة',
            color_discrete_map={
                'الإيرادات': '#38ef7d',
                'المصروفات': '#f5576c',
                'صافي الربح': '#4facfe'
            }
        )
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 حالة المواعيد")
        
        all_appointments = crud.get_all_appointments()
        if not all_appointments.empty:
            status_counts = all_appointments['status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد مواعيد لعرضها")
    
    # مواعيد اليوم
    st.markdown("### 📅 مواعيد اليوم")
    today_appointments = crud.get_appointments_by_date(date.today().isoformat())
    
    if not today_appointments.empty:
        st.dataframe(
            today_appointments[['patient_name', 'doctor_name', 'treatment_name', 'appointment_time', 'status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا توجد مواعيد اليوم")
    
    # التنبيهات
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ تنبيهات المخزون")
        low_stock = crud.get_low_stock_items()
        if not low_stock.empty:
            st.warning(f"يوجد {len(low_stock)} عنصر بمخزون منخفض")
            st.dataframe(
                low_stock[['item_name', 'quantity', 'min_stock_level']].head(5),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ جميع العناصر في المستوى الآمن")
    
    with col2:
        st.markdown("### 📆 المواعيد القادمة")
        upcoming = crud.get_upcoming_appointments(days=7)
        if not upcoming.empty:
            st.dataframe(
                upcoming[['appointment_date', 'patient_name', 'doctor_name', 'status']].head(5),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("لا توجد مواعيد قادمة")
