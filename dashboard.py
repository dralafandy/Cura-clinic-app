import streamlit as st
import pandas as pd
from datetime import date
from database.crud import CRUDOperations
from utils.helpers import (
    format_currency, create_revenue_chart, create_expenses_pie_chart,
    create_appointments_status_chart, create_inventory_alert_chart,
    create_doctor_performance_chart, create_summary_cards
)

crud = CRUDOperations()

def show_dashboard():
    st.title("🏥 لوحة تحكم عيادة كورا")
    
    try:
        # Fetch data
        appointments_df = crud.get_all_appointments()
        payments_df = crud.get_all_payments()
        expenses_df = crud.get_all_expenses()
        inventory_df = crud.get_all_inventory()
        
        # Calculate metrics
        total_revenue = payments_df['amount'].sum() if not payments_df.empty else 0
        total_expenses = expenses_df['amount'].sum() if not expenses_df.empty else 0
        net_profit = total_revenue - total_expenses
        appointments_today = len(appointments_df[pd.to_datetime(appointments_df['appointment_date']).dt.date == date.today()])
        
        # Display summary cards
        create_summary_cards(total_revenue, total_expenses, net_profit, appointments_today)
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            revenue_chart = create_revenue_chart(payments_df)
            if revenue_chart:
                st.plotly_chart(revenue_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات إيرادات لعرضها")
            
            appointments_chart = create_appointments_status_chart(appointments_df)
            if appointments_chart:
                st.plotly_chart(appointments_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات مواعيد لعرضها")
        
        with col2:
            expenses_chart = create_expenses_pie_chart(expenses_df)
            if expenses_chart:
                st.plotly_chart(expenses_chart, use_container_width=True)
            else:
                st.info("لا توجد بيانات مصروفات لعرضها")
            
            inventory_chart = create_inventory_alert_chart(inventory_df)
            if inventory_chart:
                st.plotly_chart(inventory_chart, use_container_width=True)
            else:
                st.info("لا توجد تنبيهات مخزون")
        
        st.divider()
        st.subheader("📈 أداء الأطباء")
        doctor_performance_chart = create_doctor_performance_chart(appointments_df, payments_df)
        if doctor_performance_chart:
            st.plotly_chart(doctor_performance_chart, use_container_width=True)
        else:
            st.info("لا توجد بيانات أداء الأطباء")
    
    except Exception as e:
        st.error(f"خطأ في تحميل لوحة التحكم: {str(e)}")
