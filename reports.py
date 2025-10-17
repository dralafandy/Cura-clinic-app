import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from database.crud import crud

def render():
    """صفحة التقارير والتحليلات المتقدمة"""
    st.markdown("""
        <div class='main-header'>
            <h1>📊 التقارير والتحليلات المتقدمة</h1>
            <p>تقارير شاملة عن أداء العيادة</p>
        </div>
    """, unsafe_allow_html=True)
    
    # اختيار الفترة الزمنية
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "📅 من تاريخ", 
            value=date.today() - timedelta(days=30),
            key="report_start"
        )
    
    with col2:
        end_date = st.date_input(
            "📅 إلى تاريخ", 
            value=date.today(),
            key="report_end"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        period_type = st.selectbox(
            "التجميع",
            ["يومي", "شهري", "سنوي"],
            key="period_type"
        )
    
    # تحويل نوع الفترة
    group_by_map = {"يومي": "day", "شهري": "month", "سنوي": "year"}
    group_by = group_by_map[period_type]
    
    # التبويبات
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 التقرير المالي",
        "👨‍⚕️ أداء الأطباء", 
        "💉 العلاجات",
        "👥 المرضى",
        "📦 المخزون",
        "📊 مؤشرات الأداء"
    ])
    
    with tab1:
        render_financial_report(start_date, end_date, group_by, period_type)
    
    with tab2:
        render_doctor_performance(start_date, end_date)
    
    with tab3:
        render_treatments_report(start_date, end_date)
    
    with tab4:
        render_patients_report(start_date, end_date)
    
    with tab5:
        render_inventory_report()
    
    with tab6:
        render_kpi_report(start_date, end_date)

def render_financial_report(start_date, end_date, group_by, period_type):
    """التقرير المالي"""
    st.markdown("### 💰 الملخص المالي الشامل")
    
    financial_summary = crud.get_financial_summary(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='metric-card success'>
                <div class='metric-label'>💰 إجمالي الإيرادات</div>
                <div class='metric-value'>{financial_summary['total_revenue']:,.0f}</div>
                <div class='metric-label'>جنيه مصري</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='metric-card warning'>
                <div class='metric-label'>💸 إجمالي المصروفات</div>
                <div class='metric-value'>{financial_summary['total_expenses']:,.0f}</div>
                <div class='metric-label'>جنيه مصري</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        profit_color = "success" if financial_summary['net_profit'] > 0 else "warning"
        st.markdown(f"""
            <div class='metric-card {profit_color}'>
                <div class='metric-label'>📊 صافي الربح</div>
                <div class='metric-value'>{financial_summary['net_profit']:,.0f}</div>
                <div class='metric-label'>جنيه مصري</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if financial_summary['total_revenue'] > 0:
            profit_margin = (financial_summary['net_profit'] / financial_summary['total_revenue']) * 100
        else:
            profit_margin = 0
        
        st.markdown(f"""
            <div class='metric-card info'>
                <div class='metric-label'>📈 هامش الربح</div>
                <div class='metric-value'>{profit_margin:.1f}%</div>
                <div class='metric-label'>من الإيرادات</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # الإيرادات حسب الفترة
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 📊 الإيرادات ({period_type})")
        revenue_data = crud.get_revenue_by_period(
            start_date.isoformat(),
            end_date.isoformat(),
            group_by
        )
        
        if not revenue_data.empty:
            fig = px.line(
                revenue_data,
                x='period',
                y='total_revenue',
                markers=True,
                labels={'period': 'الفترة', 'total_revenue': 'الإيرادات'}
            )
            fig.update_traces(line_color='#38ef7d', line_width=3)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات للفترة المحددة")
    
    with col2:
        st.markdown("#### 💸 المصروفات حسب الفئة")
        expenses_data = crud.get_expenses_by_category(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        if not expenses_data.empty:
            fig = px.pie(
                expenses_data,
                values='total',
                names='category',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد مصروفات للفترة المحددة")
    
    # طرق الدفع
    st.markdown("#### 💳 طرق الدفع")
    payment_methods = crud.get_payment_methods_stats(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    if not payment_methods.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                payment_methods,
                x='payment_method',
                y='total',
                color='payment_method',
                labels={'payment_method': 'طريقة الدفع', 'total': 'المبلغ الإجمالي'}
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                payment_methods.rename(columns={
                    'payment_method': 'طريقة الدفع',
                    'count': 'عدد المعاملات',
                    'total': 'الإجمالي'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    # أرباح العيادة مقابل الأطباء
    st.markdown("#### 💰 توزيع الأرباح بين العيادة والأطباء")
    clinic_earnings = crud.get_clinic_earnings(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    if not clinic_earnings.empty:
        earnings_data = clinic_earnings.iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🏥 أرباح العيادة", f"{earnings_data['total_clinic_earnings']:,.2f} ج.م")
        with col2:
            st.metric("👨‍⚕️ أرباح الأطباء", f"{earnings_data['total_doctor_earnings']:,.2f} ج.م")
        with col3:
            clinic_percentage = (earnings_data['total_clinic_earnings'] / earnings_data['total_revenue'] * 100) if earnings_data['total_revenue'] > 0 else 0
            st.metric("📊 نسبة العيادة", f"{clinic_percentage:.1f}%")
        
        # رسم بياني
        distribution_data = pd.DataFrame({
            'الفئة': ['أرباح العيادة', 'أرباح الأطباء'],
            'المبلغ': [earnings_data['total_clinic_earnings'], earnings_data['total_doctor_earnings']]
        })
        
        fig = px.pie(
            distribution_data,
            values='المبلغ',
            names='الفئة',
            hole=0.5,
            color_discrete_map={'أرباح العيادة': '#4facfe', 'أرباح الأطباء': '#38ef7d'}
        )
        st.plotly_chart(fig, use_container_width=True)

def render_doctor_performance(start_date, end_date):
    """تقرير أداء الأطباء"""
    st.markdown("### 👨‍⚕️ تقرير أداء الأطباء")
    
    doctor_performance = crud.get_doctor_performance(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    if not doctor_performance.empty:
        st.dataframe(
            doctor_performance.rename(columns={
                'doctor_name': 'الطبيب',
                'specialization': 'التخصص',
                'total_appointments': 'إجمالي المواعيد',
                'completed_appointments': 'المواعيد المكتملة',
                'total_revenue': 'الإيرادات',
                'avg_revenue_per_appointment': 'متوسط الإيراد',
                'commission_rate': 'نسبة العمولة %',
                'total_commission': 'إجمالي العمولة'
            }).round(2),
            use_container_width=True,
            hide_index=True
        )
        
        # رسوم بيانية
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 الإيرادات حسب الطبيب")
            fig = px.bar(
                doctor_performance,
                x='doctor_name',
                y='total_revenue',
                color='doctor_name',
                labels={'doctor_name': 'الطبيب', 'total_revenue': 'الإيرادات'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 معدل إتمام المواعيد")
            doctor_performance['completion_rate'] = (
                doctor_performance['completed_appointments'] / 
                doctor_performance['total_appointments'] * 100
            ).round(2)
            
            fig = px.bar(
                doctor_performance,
                x='doctor_name',
                y='completion_rate',
                color='completion_rate',
                color_continuous_scale='Greens',
                labels={'doctor_name': 'الطبيب', 'completion_rate': 'معدل الإتمام %'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا توجد بيانات للفترة المحددة")

def render_treatments_report(start_date, end_date):
    """تقرير العلاجات"""
    st.markdown("### 💉 تقرير العلاجات الأكثر طلباً")
    
    treatment_stats = crud.get_treatment_popularity(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    if not treatment_stats.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 أكثر العلاجات حجزاً")
            fig = px.pie(
                treatment_stats.head(10),
                values='booking_count',
                names='treatment_name',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 💰 أعلى العلاجات إيراداً")
            fig = px.bar(
                treatment_stats.head(10),
                x='treatment_name',
                y='total_revenue',
                color='category',
                labels={'treatment_name': 'العلاج', 'total_revenue': 'الإيرادات'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # الجدول التفصيلي
        st.markdown("#### 📋 جدول العلاجات التفصيلي")
        st.dataframe(
            treatment_stats.rename(columns={
                'treatment_name': 'العلاج',
                'category': 'الفئة',
                'booking_count': 'عدد الحجوزات',
                'total_revenue': 'الإيرادات',
                'avg_price': 'متوسط السعر'
            }).round(2),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا توجد بيانات للفترة المحددة")

def render_patients_report(start_date, end_date):
    """تقرير المرضى"""
    st.markdown("### 👥 تحليلات المرضى")
    
    patient_stats = crud.get_patient_statistics()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 توزيع المرضى حسب الجنس")
        if not patient_stats['gender'].empty:
            fig = px.pie(
                patient_stats['gender'],
                values='count',
                names='gender',
                color_discrete_map={'ذكر': '#4facfe', 'أنثى': '#f093fb'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 توزيع المرضى حسب الفئة العمرية")
        if not patient_stats['age'].empty:
            fig = px.bar(
                patient_stats['age'],
                x='age_group',
                y='count',
                color='age_group',
                labels={'age_group': 'الفئة العمرية', 'count': 'العدد'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # أكثر المرضى زيارة
    st.markdown("#### 🏆 أكثر المرضى زيارة")
    top_patients = crud.get_top_patients(
        start_date.isoformat(),
        end_date.isoformat(),
        limit=10
    )
    
    if not top_patients.empty:
        st.dataframe(
            top_patients.rename(columns={
                'patient_name': 'المريض',
                'phone': 'الهاتف',
                'visit_count': 'عدد الزيارات',
                'total_spent': 'إجمالي الإنفاق',
                'last_visit': 'آخر زيارة'
            }).round(2),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("لا توجد بيانات")
    
    # حالة المواعيد
    st.markdown("#### 📅 توزيع حالات المواعيد")
    appointment_status = crud.get_appointment_status_stats(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    if not appointment_status.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                appointment_status,
                values='count',
                names='status',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                appointment_status.rename(columns={
                    'status': 'الحالة',
                    'count': 'العدد',
                    'total_revenue': 'الإيرادات'
                }),
                use_container_width=True,
                hide_index=True
            )

def render_inventory_report():
    """تقرير المخزون"""
    st.markdown("### 📦 تقرير المخزون")
    
    inventory_value = crud.get_inventory_value()
    
    if not inventory_value.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 قيمة المخزون حسب الفئة")
            fig = px.bar(
                inventory_value,
                x='category',
                y='total_value',
                color='category',
                labels={'category': 'الفئة', 'total_value': 'القيمة الإجمالية'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 توزيع الكميات")
            fig = px.pie(
                inventory_value,
                values='total_quantity',
                names='category',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # الجدول التفصيلي
        total_value = inventory_value['total_value'].sum()
        st.success(f"💰 إجمالي قيمة المخزون: {total_value:,.2f} جنيه")
        
        st.dataframe(
            inventory_value.rename(columns={
                'category': 'الفئة',
                'total_value': 'القيمة الإجمالية',
                'total_quantity': 'إجمالي الكمية',
                'item_count': 'عدد الأصناف'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    # المخزون المنخفض
    st.markdown("#### ⚠️ تنبيهات المخزون المنخفض")
    low_stock = crud.get_low_stock_items()
    
    if not low_stock.empty:
        st.warning(f"يوجد {len(low_stock)} عنصر بمخزون منخفض")
        st.dataframe(
            low_stock[['item_name', 'category', 'quantity', 'min_stock_level']].rename(columns={
                'item_name': 'الصنف',
                'category': 'الفئة',
                'quantity': 'الكمية الحالية',
                'min_stock_level': 'الحد الأدنى'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ جميع الأصناف في المستوى الآمن")
    
    # المخزون قريب الانتهاء
    st.markdown("#### 📅 أصناف قريبة من انتهاء الصلاحية")
    expiring = crud.get_expiring_inventory(days=60)
    
    if not expiring.empty:
        st.warning(f"يوجد {len(expiring)} صنف ينتهي خلال 60 يوم")
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

def render_kpi_report(start_date, end_date):
    """مؤشرات الأداء"""
    st.markdown("### 📊 مؤشرات الأداء الرئيسية (KPIs)")
    
    # الإيرادات اليومية
    st.markdown("#### 📈 مقارنة الإيرادات اليومية (آخر 30 يوم)")
    daily_revenue = crud.get_daily_revenue_comparison(days=30)
    
    if not daily_revenue.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_revenue['payment_date'],
            y=daily_revenue['daily_revenue'],
            mode='lines+markers',
            name='الإيرادات اليومية',
            line=dict(color='#38ef7d', width=3),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            xaxis_title='التاريخ',
            yaxis_title='الإيرادات (جنيه)',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # الإحصائيات
        col1, col2, col3, col4 = st.columns(4)
        
        avg_daily = daily_revenue['daily_revenue'].mean()
        max_daily = daily_revenue['daily_revenue'].max()
        min_daily = daily_revenue['daily_revenue'].min()
        total_days = len(daily_revenue)
        
        with col1:
            st.metric("📊 متوسط الإيراد اليومي", f"{avg_daily:,.0f} ج.م")
        
        with col2:
            st.metric("🔝 أعلى إيراد يومي", f"{max_daily:,.0f} ج.م")
        
        with col3:
            st.metric("🔽 أقل إيراد يومي", f"{min_daily:,.0f} ج.م")
        
        with col4:
            st.metric("📅 عدد أيام العمل", f"{total_days} يوم")
    
    # المقارنة الشهرية
    st.markdown("#### 📅 المقارنة الشهرية (آخر 6 شهور)")
    monthly_comparison = crud.get_monthly_comparison(months=6)
    
    if not monthly_comparison.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=monthly_comparison['month'],
            y=monthly_comparison['revenue'],
            name='الإيرادات',
            marker_color='#38ef7d'
        ))
        
        fig.add_trace(go.Bar(
            x=monthly_comparison['month'],
            y=monthly_comparison['expenses'],
            name='المصروفات',
            marker_color='#f5576c'
        ))
        
        fig.add_trace(go.Scatter(
            x=monthly_comparison['month'],
            y=monthly_comparison['profit'],
            name='صافي الربح',
            line=dict(color='#4facfe', width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            barmode='group',
            xaxis_title='الشهر',
            yaxis_title='المبلغ (جنيه)',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # مؤشرات إضافية
    st.markdown("---")
    st.markdown("#### 🎯 مؤشرات الأداء الإضافية")
    
    col1, col2, col3 = st.columns(3)
    
    # معدل إشغال المواعيد
    all_appointments = crud.get_all_appointments()
    if not all_appointments.empty:
        total_apps = len(all_appointments)
        completed_apps = len(all_appointments[all_appointments['status'] == 'مكتمل'])
        completion_rate = (completed_apps / total_apps * 100) if total_apps > 0 else 0
        
        with col1:
            st.metric(
                "✅ معدل إتمام المواعيد",
                f"{completion_rate:.1f}%",
                delta=f"{completed_apps}/{total_apps}"
            )
    
    # متوسط قيمة الموعد
    if not all_appointments.empty and all_appointments['total_cost'].sum() > 0:
        avg_appointment_value = all_appointments['total_cost'].mean()
        
        with col2:
            st.metric(
                "💰 متوسط قيمة الموعد",
                f"{avg_appointment_value:,.0f} ج.م"
            )
    
    # عدد المرضى الجدد
    patients = crud.get_all_patients()
    if not patients.empty:
        recent_patients = len(patients[
            pd.to_datetime(patients['created_at']) >= 
            pd.to_datetime(start_date)
        ])
        
        with col3:
            st.metric(
                "👥 مرضى جدد",
                f"{recent_patients} مريض",
                delta="في الفترة المحددة"
            )
