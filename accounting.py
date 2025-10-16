import streamlit as st
import pandas as pd
from datetime import date, datetime
from database.crud import crud
from utils.helpers import format_currency, show_success_message, show_error_message

def show_accounting():
    st.title("🧮 المحاسبة اليومية")
    
    tab1, tab2, tab3, tab4 = st.tabs(["إدخال معاملة", "المدفوعات", "المصروفات", "الكشوفات"])
    
    with tab1:
        add_transaction()
    
    with tab2:
        manage_payments()
    
    with tab3:
        manage_expenses()
    
    with tab4:
        show_account_statements()

def add_transaction():
    """إضافة معاملة جديدة"""
    st.subheader("➕ إضافة معاملة جديدة")
    
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_type = st.selectbox(
                "نوع المعاملة",
                ["إيراد", "مصروف"]
            )
            
            amount = st.number_input("المبلغ (ج.م)", min_value=0.0, step=50.0)
            
            transaction_date = st.date_input("تاريخ المعاملة", value=date.today())
        
        with col2:
            if transaction_type == "إيراد":
                category = st.selectbox(
                    "فئة الإيراد",
                    ["جلسة علاج", "كشف", "أشعة", "تحاليل", "أخرى"]
                )
                description = st.text_input("وصف الإيراد")
            else:
                category = st.selectbox(
                    "فئة المصروف",
                    ["رواتب", "إيجار", "مرافق", "مستلزمات", "صيانة", "أخرى"]
                )
                description = st.text_input("وصف المصروف")
            
            payment_method = st.selectbox(
                "طريقة الدفع",
                ["نقدي", "تحويل بنكي", "بطاقة ائتمان", "شيك"]
            )
        
        notes = st.text_area("ملاحظات")
        
        if st.form_submit_button("💾 حفظ المعاملة"):
            try:
                if transaction_type == "إيراد":
                    # حفظ كإيراد
                    pass
                else:
                    # حفظ كمصروف
                    expense_id = crud.create_expense(
                        category=category,
                        description=description,
                        amount=amount,
                        expense_date=transaction_date,
                        payment_method=payment_method,
                        notes=notes
                    )
                    show_success_message(f"تم إضافة المصروف بنجاح (المعرف: {expense_id})")
                
            except Exception as e:
                show_error_message(f"خطأ في حفظ المعاملة: {str(e)}")

def manage_payments():
    """إدارة المدفوعات"""
    st.subheader("💳 إدارة المدفوعات")
    
    try:
        payments_df = crud.get_all_payments()
        
        if not payments_df.empty:
            st.dataframe(
                payments_df,
                use_container_width=True,
                hide_index=True
            )
            
            # إحصائيات سريعة
            col1, col2, col3 = st.columns(3)
            with col1:
                total_payments = payments_df['amount'].sum()
                st.metric("إجمالي المدفوعات", format_currency(total_payments))
            
            with col2:
                cash_payments = payments_df[payments_df['payment_method'] == 'نقدي']['amount'].sum()
                st.metric("المدفوعات النقدية", format_currency(cash_payments))
            
            with col3:
                bank_payments = payments_df[payments_df['payment_method'] == 'تحويل بنكي']['amount'].sum()
                st.metric("التحويلات البنكية", format_currency(bank_payments))
        else:
            st.info("لا توجد مدفوعات مسجلة")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل المدفوعات: {str(e)}")

def manage_expenses():
    """إدارة المصروفات"""
    st.subheader("🧾 إدارة المصروفات")
    
    try:
        expenses_df = crud.get_all_expenses()
        
        if not expenses_df.empty:
            st.dataframe(
                expenses_df,
                use_container_width=True,
                hide_index=True
            )
            
            # إحصائيات المصروفات
            expenses_by_category = expenses_df.groupby('category')['amount'].sum()
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("### توزيع المصروفات حسب الفئة")
                for category, amount in expenses_by_category.items():
                    st.write(f"- **{category}**: {format_currency(amount)}")
            
            with col2:
                total_expenses = expenses_df['amount'].sum()
                avg_expense = expenses_df['amount'].mean()
                st.metric("إجمالي المصروفات", format_currency(total_expenses))
                st.metric("متوسط المصروف", format_currency(avg_expense))
        else:
            st.info("لا توجد مصروفات مسجلة")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل المصروفات: {str(e)}")

def show_account_statements():
    """عرض الكشوفات المالية"""
    st.subheader("📋 الكشوفات المالية")
    
    # فلترة التاريخ
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=date.today().replace(day=1), key="stmt_start")
    with col2:
        end_date = st.date_input("إلى تاريخ", value=date.today(), key="stmt_end")
    
    try:
        payments_df = crud.get_all_payments()
        expenses_df = crud.get_all_expenses()
        
        if not payments_df.empty:
            payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date']).dt.date
            filtered_payments = payments_df[
                (payments_df['payment_date'] >= start_date) & 
                (payments_df['payment_date'] <= end_date)
            ]
        
        if not expenses_df.empty:
            expenses_df['expense_date'] = pd.to_datetime(expenses_df['expense_date']).dt.date
            filtered_expenses = expenses_df[
                (expenses_df['expense_date'] >= start_date) & 
                (expenses_df['expense_date'] <= end_date)
            ]
        
        # حساب الإجماليات
        total_revenue = filtered_payments['amount'].sum() if not filtered_payments.empty else 0
        total_expenses = filtered_expenses['amount'].sum() if not filtered_expenses.empty else 0
        net_income = total_revenue - total_expenses
        
        # عرض النتائج
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي الإيرادات", format_currency(total_revenue))
        with col2:
            st.metric("إجمالي المصروفات", format_currency(total_expenses))
        with col3:
            st.metric("صافي الدخل", format_currency(net_income))
        
        # كشف مفصل
        st.subheader("كشف مفصل")
        
        if not filtered_payments.empty:
            st.write("### الإيرادات")
            st.dataframe(filtered_payments, use_container_width=True)
        
        if not filtered_expenses.empty:
            st.write("### المصروفات")
            st.dataframe(filtered_expenses, use_container_width=True)
    
    except Exception as e:
        show_error_message(f"خطأ في إنشاء الكشف: {str(e)}")

if __name__ == "__main__":
    show_accounting()
