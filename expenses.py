import streamlit as st
from datetime import date
from database.crud import crud

def render():
    """صفحة إدارة المصروفات"""
    st.markdown("### 💸 إدارة المصروفات")
    
    tab1, tab2 = st.tabs(["📋 جميع المصروفات", "➕ مصروف جديد"])
    
    with tab1:
        render_all_expenses()
    
    with tab2:
        render_add_expense()

def render_all_expenses():
    """عرض جميع المصروفات"""
    expenses = crud.get_all_expenses()
    if not expenses.empty:
        # فلترة حسب الفئة
        categories = expenses['category'].unique().tolist()
        category_filter = st.selectbox("فلترة حسب الفئة", ["الكل"] + categories)
        
        if category_filter != "الكل":
            expenses = expenses[expenses['category'] == category_filter]
        
        st.dataframe(
            expenses[['id', 'category', 'description', 'amount', 'expense_date', 
                     'payment_method', 'receipt_number']],
            use_container_width=True,
            hide_index=True
        )
        
        # الإحصائيات
        total = expenses['amount'].sum()
        st.error(f"💸 إجمالي المصروفات: {total:,.2f} ج.م")
    else:
        st.info("لا توجد مصروفات")

def render_add_expense():
    """نموذج إضافة مصروف جديد"""
    st.markdown("#### إضافة مصروف جديد")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox("التصنيف*", [
            "رواتب", "إيجار", "كهرباء ومياه", "صيانة", 
            "مستلزمات", "تسويق", "ضرائب", "تأمين", "أخرى"
        ])
        description = st.text_input("الوصف*")
        amount = st.number_input("المبلغ (ج.م)*", min_value=0.0, step=10.0)
        expense_date = st.date_input("تاريخ المصروف", value=date.today())
    
    with col2:
        payment_method = st.selectbox("طريقة الدفع", ["نقدي", "تحويل بنكي", "شيك", "بطاقة ائتمان"])
        receipt_number = st.text_input("رقم الإيصال")
        approved_by = st.text_input("تمت الموافقة من قبل", placeholder="اختياري")
        is_recurring = st.checkbox("مصروف دوري")
    
    notes = st.text_area("ملاحظات")
    
    if st.button("تسجيل المصروف", type="primary", use_container_width=True):
        if description and amount > 0:
            try:
                crud.create_expense(
                    category, description, amount,
                    expense_date.isoformat(), payment_method,
                    receipt_number, notes, approved_by, is_recurring
                )
                st.success("✅ تم تسجيل المصروف بنجاح!")
                st.rerun()
            except Exception as e:
                st.error(f"حدث خطأ: {str(e)}")
        else:
            st.warning("الرجاء ملء الحقول المطلوبة")
