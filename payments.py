import streamlit as st
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
from database.crud import crud

def render():
    """صفحة إدارة المدفوعات"""
    st.markdown("### 💰 إدارة المدفوعات")
    
    tab1, tab2, tab3 = st.tabs(["📋 جميع المدفوعات", "➕ دفعة جديدة", "📊 أرباح الأطباء"])
    
    with tab1:
        render_all_payments()
    
    with tab2:
        render_add_payment()
    
    with tab3:
        render_doctor_earnings()

def render_all_payments():
    """عرض جميع المدفوعات"""
    payments = crud.get_all_payments()
    if not payments.empty:
        display_df = payments[[
            'id', 'patient_name', 'amount', 
            'doctor_percentage', 'doctor_share',
            'clinic_percentage', 'clinic_share',
            'payment_method', 'payment_date', 'status'
        ]].copy()
        
        display_df.columns = [
            'الرقم', 'المريض', 'المبلغ',
            'نسبة الطبيب %', 'حصة الطبيب',
            'نسبة العيادة %', 'حصة العيادة',
            'طريقة الدفع', 'التاريخ', 'الحالة'
        ]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # الإحصائيات
        col1, col2, col3 = st.columns(3)
        
        total = payments['amount'].sum()
        doctor_total = payments['doctor_share'].sum()
        clinic_total = payments['clinic_share'].sum()
        
        with col1:
            st.metric("💰 إجمالي المدفوعات", f"{total:,.2f} ج.م")
        with col2:
            st.metric("👨‍⚕️ حصة الأطباء", f"{doctor_total:,.2f} ج.م")
        with col3:
            st.metric("🏥 حصة العيادة", f"{clinic_total:,.2f} ج.م")
    else:
        st.info("لا توجد مدفوعات")

def render_add_payment():
    """نموذج إضافة دفعة جديدة"""
    st.markdown("#### إضافة دفعة جديدة")
    
    patients = crud.get_all_patients()
    appointments = crud.get_all_appointments()
    
    if not patients.empty:
        appointment_id = st.selectbox(
            "الموعد (اختياري)",
            [None] + appointments['id'].tolist() if not appointments.empty else [None],
            format_func=lambda x: "دفعة بدون موعد" if x is None else 
                f"موعد #{x} - {appointments[appointments['id']==x]['patient_name'].iloc[0]} - {appointments[appointments['id']==x]['treatment_name'].iloc[0]}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if appointment_id:
                appointment_data = appointments[appointments['id'] == appointment_id].iloc[0]
                patient_name = appointment_data['patient_name']
                amount = st.number_input("المبلغ (ج.م)*", value=float(appointment_data['total_cost']), min_value=0.0, step=10.0)
                
                st.info(f"المريض: {patient_name}")
                
                treatments = crud.get_all_treatments()
                if not treatments.empty:
                    treatment_name = appointment_data['treatment_name']
                    treatment_info = treatments[treatments['name'] == treatment_name]
                    
                    if not treatment_info.empty:
                        doctor_pct = treatment_info['doctor_percentage'].iloc[0]
                        clinic_pct = treatment_info['clinic_percentage'].iloc[0]
                    else:
                        doctor_pct = 50.0
                        clinic_pct = 50.0
                else:
                    doctor_pct = 50.0
                    clinic_pct = 50.0
                
                st.markdown("---")
                st.markdown("##### 💰 توزيع المبلغ التلقائي:")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    doctor_share = (amount * doctor_pct) / 100
                    st.success(f"👨‍⚕️ الطبيب ({doctor_pct}%): **{doctor_share:,.2f} ج.م**")
                with col_b:
                    clinic_share = (amount * clinic_pct) / 100
                    st.info(f"🏥 العيادة ({clinic_pct}%): **{clinic_share:,.2f} ج.م**")
                
                patient_id = patients[patients['name'] == patient_name]['id'].iloc[0]
            else:
                patient_id = st.selectbox(
                    "المريض*",
                    patients['id'].tolist(),
                    format_func=lambda x: patients[patients['id'] == x]['name'].iloc[0]
                )
                amount = st.number_input("المبلغ (ج.م)*", min_value=0.0, step=10.0)
                
                st.warning("⚠️ دفعة بدون موعد - ستذهب 100% للعيادة")
            
            payment_date = st.date_input("تاريخ الدفع", value=date.today())
        
        with col2:
            payment_method = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة ائتمان", "تحويل بنكي", "شيك"])
            notes = st.text_area("ملاحظات")
        
        if st.button("تسجيل الدفعة", type="primary", use_container_width=True):
            if amount > 0:
                try:
                    crud.create_payment(
                        appointment_id, patient_id, amount,
                        payment_method, payment_date.isoformat(), notes
                    )
                    st.success("✅ تم تسجيل الدفعة بنجاح!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")
            else:
                st.warning("الرجاء إدخال مبلغ صحيح")
    else:
        st.warning("يجب إضافة مرضى أولاً")

def render_doctor_earnings():
    """عرض أرباح الأطباء"""
    st.markdown("#### 💼 أرباح الأطباء")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today() - timedelta(days=30), key="doc_earnings_start")
    with col2:
        end_date = st.date_input("إلى تاريخ", value=date.today(), key="doc_earnings_end")
    
    doctors = crud.get_all_doctors()
    
    if not doctors.empty:
        earnings_data = []
        
        for _, doctor in doctors.iterrows():
            earnings = crud.get_doctor_earnings(
                doctor['id'], 
                start_date.isoformat(), 
                end_date.isoformat()
            )
            
            if not earnings.empty and earnings.iloc[0]['total_earnings'] is not None:
                earnings_data.append({
                    'الطبيب': doctor['name'],
                    'التخصص': doctor['specialization'],
                    'عدد المدفوعات': int(earnings.iloc[0]['payment_count'] or 0),
                    'إجمالي الأرباح': float(earnings.iloc[0]['total_earnings'] or 0),
                    'متوسط النسبة': float(earnings.iloc[0]['avg_percentage'] or 0)
                })
        
        if earnings_data:
            earnings_df = pd.DataFrame(earnings_data)
            st.dataframe(earnings_df, use_container_width=True, hide_index=True)
            
            # رسم بياني
            fig = px.bar(
                earnings_df,
                x='الطبيب',
                y='إجمالي الأرباح',
                color='التخصص',
                title='أرباح الأطباء'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد بيانات للفترة المحددة")
