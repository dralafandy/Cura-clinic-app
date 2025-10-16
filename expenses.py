import streamlit as st
import pandas as pd
from datetime import date
from database.crud import CRUDOperations
from utils.helpers import show_success_message, show_error_message, format_currency

crud = CRUDOperations()

def show_expenses():
    st.title("💸 إدارة المصروفات")
    
    st.sidebar.subheader("خيارات المصروفات")
    action = st.sidebar.radio(
        "اختر العملية",
        ["عرض المصروفات", "إضافة مصروف جديد", "تعديل مصروف", "حذف مصروف"]
    )
    
    if action == "عرض المصروفات":
        show_expenses_list()
    elif action == "إضافة مصروف جديد":
        add_expense()
    elif action == "تعديل مصروف":
        edit_expense()
    elif action == "حذف مصروف":
        delete_expense()

def show_expenses_list():
    """Display list of expenses"""
    st.subheader("📋 قائمة المصروفات")
    
    try:
        expenses_df = crud.get_all_expenses()
        
        if expenses_df.empty:
            st.info("لا توجد مصروفات لعرضها")
            return
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox(
                "فلترة حسب الفئة",
                ["الكل"] + list(expenses_df['category'].unique())
            )
        with col2:
            date_filter = st.date_input("فلترة حسب التاريخ", value=None)
        
        # Apply filters
        filtered_df = expenses_df
        if category_filter != "الكل":
            filtered_df = filtered_df[filtered_df['category'] == category_filter]
        if date_filter:
            filtered_df = filtered_df[pd.to_datetime(filtered_df['date']).dt.date == date_filter]
        
        if filtered_df.empty:
            st.info("لا توجد مصروفات تطابق المعايير المحددة")
            return
        
        # Display summary
        total_expenses = filtered_df['amount'].sum()
        st.metric("💸 إجمالي المصروفات", format_currency(total_expenses))
        
        # Display expenses table
        st.dataframe(
            filtered_df[['date', 'category', 'amount', 'description']],
            column_config={
                'date': st.column_config.DateColumn('التاريخ', format="YYYY-MM-DD"),
                'category': 'الفئة',
                'amount': st.column_config.NumberColumn('المبلغ', format="%.2f ج.م"),
                'description': 'الوصف'
            },
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        show_error_message(f"خطأ في عرض المصروفات: {str(e)}")

def add_expense():
    """Add a new expense"""
    st.subheader("➕ إضافة مصروف جديد")
    
    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("تاريخ المصروف *", value=date.today())
            category = st.text_input("الفئة *", max_chars=100, placeholder="مثال: إيجار، رواتب")
        with col2:
            amount = st.number_input("المبلغ (ج.م) *", min_value=0.0, step=10.0)
            description = st.text_area("الوصف")
        
        submitted = st.form_submit_button("💾 إضافة المصروف")
        
        if submitted:
            if not category or not amount:
                show_error_message("يجب ملء الحقول المطلوبة (الفئة والمبلغ)")
            else:
                try:
                    expense_id = crud.create_expense(
                        date=date_input,
                        category=category,
                        amount=amount,
                        description=description
                    )
                    show_success_message(f"تم إضافة المصروف رقم {expense_id} بنجاح")
                    st.rerun()
                except Exception as e:
                    show_error_message(f"خطأ في إضافة المصروف: {str(e)}")

def edit_expense():
    """Edit an existing expense"""
    st.subheader("✏️ تعديل مصروف")
    
    try:
        expenses_df = crud.get_all_expenses()
        if expenses_df.empty:
            st.info("لا توجد مصروفات لتعديلها")
            return
        
        expense_options = {row['id']: f"{row['category']} - {format_currency(row['amount'])} - {row['date']}" for _, row in expenses_df.iterrows()}
        selected_expense_id = st.selectbox(
            "اختر المصروف للتعديل",
            options=list(expense_options.keys()),
            format_func=lambda x: expense_options[x]
        )
        
        if selected_expense_id:
            expense = crud.get_expense_by_id(selected_expense_id)
            if not expense.empty:
                with st.form(f"edit_expense_form_{selected_expense_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        date_input = st.date_input("تاريخ المصروف *", value=pd.to_datetime(expense['date']).date())
                        category = st.text_input("الفئة *", value=expense['category'], max_chars=100)
                    with col2:
                        amount = st.number_input("المبلغ (ج.م) *", min_value=0.0, value=float(expense['amount']), step=10.0)
                        description = st.text_area("الوصف", value=expense['description'] or "")
                    
                    submitted = st.form_submit_button("💾 حفظ التعديلات")
                    
                    if submitted:
                        if not category or not amount:
                            show_error_message("يجب ملء الحقول المطلوبة (الفئة والمبلغ)")
                        else:
                            crud.update_expense(
                                expense_id=selected_expense_id,
                                date=date_input,
                                category=category,
                                amount=amount,
                                description=description
                            )
                            show_success_message("تم تعديل المصروف بنجاح")
                            st.rerun()
    
    except Exception as e:
        show_error_message(f"خطأ في تعديل المصروف: {str(e)}")

def delete_expense():
    """Delete an expense"""
    st.subheader("🗑️ حذف مصروف")
    
    try:
        expenses_df = crud.get_all_expenses()
        if expenses_df.empty:
            st.info("لا توجد مصروفات لحذفها")
            return
        
        expense_options = {row['id']: f"{row['category']} - {format_currency(row['amount'])} - {row['date']}" for _, row in expenses_df.iterrows()}
        selected_expense_id = st.selectbox(
            "اختر المصروف للحذف",
            options=list(expense_options.keys()),
            format_func=lambda x: expense_options[x]
        )
        
        if st.button("🗑️ حذف المصروف"):
            try:
                crud.delete_expense(selected_expense_id)
                show_success_message("تم حذف المصروف بنجاح")
                st.rerun()
            except Exception as e:
                show_error_message(f"خطأ في حذف المصروف: {str(e)}")
    
    except Exception as e:
        show_error_message(f"خطأ في تحميل المصروفات: {str(e)}")

if __name__ == "__main__":
    show_expenses()
