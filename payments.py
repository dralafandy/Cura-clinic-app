import streamlit as st
import pandas as pd
from datetime import date
from database.crud import CRUDOperations
from utils.helpers import show_success_message, show_error_message, format_currency

crud = CRUDOperations()

def show_payments():
    st.title("💰 إدارة المدفوعات")
    
    st.sidebar.subheader("خيارات المدفوعات")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المدفوعات", "إضافة مدفوعة جديدة", "تعديل مدفوعة", "حذف مدفوعة"]
    )
    
    if action == "عرض المدفوعات":
        show_payments_list()
    elif action == "إضافة مدفوعة جديدة":
        add_payment()
    elif action == "تعديل مدفوعة":
        edit_payment()
    elif action == "حذف مدفوعة":
        delete_payment()

def show_payments_list():
    """Display list of payments"""
    st.subheader("📋 قائمة المدفوعات")
    
    try:
        payments_df = crud.get_all_payments()
        
        if payments_df.empty:
            st.info("لا توجد مدفوعات لعرضها")
            return
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            patient_filter = st.text_input("البحث باسم المريض")
        with col2:
            date_filter = st.date_input("فلترة حسب التاريخ", value=None)
        
        # Apply filters
        filtered_df = payments_df
        if patient_filter:
            filtered_df = filtered_df[filtered_df['patient_name'].str.contains(patient_filter, case=False, na=False)]
        if date_filter:
            filtered_df = filtered_df[pd.to_datetime(filtered_df['payment_date']).dt.date == date_filter]
        
        if filtered_df.empty:
            st.info("لا توجد مدفوعات تطابق المعايير المحددة")
            return
        
        # Display summary
        total_payments = filtered_df['amount'].sum()
        st.metric("💰 إجمالي المدفوعات", format_currency(total_payments))
        
        # Display payments table
        st.dataframe(
            filtered_df[['payment_date', 'patient_name', 'amount', 'payment_method', 'appointment_id']],
            column_config={
                'payment_date': st.column_config.DateColumn('تاريخ الدفع', format="YYYY-MM-DD"),
                'patient_name': 'اسم المريض',
                'amount': st.column_config.NumberColumn('المبلغ', format="%.2f ج.م"),
                'payment_method': 'طريقة الدفع',
                'appointment_id': 'رقم الموعد'
            },
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        show_error_message(f"خطأ في عرض المدفوعات: {str(e)}")

def add_payment():
    """Add a new payment"""
    st.subheader("➕ إضافة مدفوعة جديدة")
    
    try:
        appointments_df = crud.get_all_appointments()
        if appointments_df.empty:
            st.info("لا توجد مواعيد متاحة لإضافة مدفوعة")
            return
        
        appointment_options = {
            row['id']: f"موعد #{row['id']} - {row['patient_name']} - {row['appointment_date']}"
            for _, row in appointments_df.iterrows()
        }
        
        with st.form("add_payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                appointment_id = st.selectbox(
                    "اختر الموعد *",
                    options=list(appointment_options.keys()),
                    format_func=lambda x: appointment_options[x]
                )
                payment_date = st.date_input("تاريخ الدفع *", value=date.today())
            with col2:
                amount = st.number_input("المبلغ (ج.م) *", min_value=0.0, step=10.0)
                payment_method = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة ائتمان", "تحويل بنكي"])
            
            submitted = st.form_submit_button("💾 إضافة المدفوعة")
            
            if submitted:
                if not appointment_id or not amount:
                    show_error_message("يجب ملء الحقول المطلوبة (الموعد والمبلغ)")
                else:
                    try:
                        payment_id = crud.create_payment(
                            appointment_id=appointment_id,
                            amount=amount,
                            payment_date=payment_date,
                            payment_method=payment_method
                        )
                        show_success_message(f"تم إضافة المدفوعة رقم {payment_id} بنجاح")
                        st.rerun()
                    except Exception as e:
                        show_error_message(f"خطأ في إضافة المدفوعة: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل المواعيد: {str(e)}")

def edit_payment():
    """Edit an existing payment"""
    st.subheader("✏️ تعديل مدفوعة")
    
    try:
        payments_df = crud.get_all_payments()
        if payments_df.empty:
            st.info("لا توجد مدفوعات لتعديلها")
            return
        
        payment_options = {
            row['id']: f"مدفوعة #{row['id']} - {row['patient_name']} - {format_currency(row['amount'])} - {row['payment_date']}"
            for _, row in payments_df.iterrows()
        }
        selected_payment_id = st.selectbox(
            "اختر المدفوعة للتعديل",
            options=list(payment_options.keys()),
            format_func=lambda x: payment_options[x]
        )
        
        if selected_payment_id:
            payment = crud.get_payment_by_id(selected_payment_id)
            if not payment.empty:
                appointments_df = crud.get_all_appointments()
                appointment_options = {
                    row['id']: f"موعد #{row['id']} - {row['patient_name']} - {row['appointment_date']}"
                    for _, row in appointments_df.iterrows()
                }
                
                with st.form(f"edit_payment_form_{selected_payment_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        appointment_id = st.selectbox(
                            "اختر الموعد *",
                            options=list(appointment_options.keys()),
                            index=list(appointment_options.keys()).index(payment['appointment_id']),
                            format_func=lambda x: appointment_options[x]
                        )
                        payment_date = st.date_input("تاريخ الدفع *", value=pd.to_datetime(payment['payment_date']).date())
                    with col2:
                        amount = st.number_input("المبلغ (ج.م) *", min_value=0.0, value=float(payment['amount']), step=10.0)
                        payment_method = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة ائتمان", "تحويل بنكي"], index=["نقدي", "بطاقة ائتمان", "تحويل بنكي"].index(payment['payment_method']))
                    
                    submitted = st.form_submit_button("💾 حفظ التعديلات")
                    
                    if submitted:
                        if not appointment_id or not amount:
                            show_error_message("يجب ملء الحقول المطلوبة (الموعد والمبلغ)")
                        else:
                            crud.update_payment(
                                payment_id=selected_payment_id,
                                appointment_id=appointment_id,
                                amount=amount,
                                payment_date=payment_date,
                                payment_method=payment_method
                            )
                            show_success_message("تم تعديل المدفوعة بنجاح")
                            st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في تعديل المدفوعة: {str(e)}")

def delete_payment():
    """Delete a payment"""
    st.subheader("🗑️ حذف مدفوعة")
    
    try:
        payments_df = crud.get_all_payments()
        if payments_df.empty:
            st.info("لا توجد مدفوعات لحذفها")
            return
        
        payment_options = {
            row['id']: f"مدفوعة #{row['id']} - {row['patient_name']} - {format_currency(row['amount'])} - {row['payment_date']}"
            for _, row in payments_df.iterrows()
        }
        selected_payment_id = st.selectbox(
            "اختر المدفوعة للحذف",
            options=list(payment_options.keys()),
            format_func=lambda x: payment_options[x]
        )
        
        if st.button("🗑️ حذف المدفوعة"):
            try:
                crud.delete_payment(selected_payment_id)
                show_success_message("تم حذف المدفوعة بنجاح")
                st.rerun()
            except Exception as e:
                show_error_message(f"خطأ في حذف المدفوعة: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل المدفوعات: {str(e)}")

if __name__ == "__main__":
    show_payments()
