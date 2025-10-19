import streamlit as st

# قائمة بجميع أزرار التنقل الإضافية التي قد تظهر ضمن صفحة "المزيد"
MORE_PAGES = [
    {'id': 'doctors', 'label': 'الأطباء', 'icon': '👨‍⚕️'},
    {'id': 'treatments', 'label': 'العلاجات', 'icon': '💊'},
    {'id': 'suppliers', 'label': 'الموردين', 'icon': '🚚'},
    {'id': 'expenses', 'label': 'المصروفات', 'icon': '💸'},
    {'id': 'reports', 'label': 'التقارير', 'icon': '📈'},
    {'id': 'activity_log', 'label': 'السجل', 'icon': '📜'}
]

def load_custom_css():
    st.markdown(
        """
        <style>
        /* ======================================= */
        /* 1. إخفاء الشريط الجانبي الافتراضي */
        /* ======================================= */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* إخفاء زر القائمة (البرغر) */
        button[data-testid="baseButton-header"] {
            display: none !important;
        }

        /* ======================================= */
        /* 2. تنسيق شريط التنقل السفلي (الهواتف) */
        /* ======================================= */
        
        /* الحاوية الرئيسية للشريط السفلي */
        .mobile-nav-container {
            position: fixed; 
            bottom: 0;      
            left: 0;
            right: 0;
            z-index: 1000;  
            background-color: #ffffff; /* خلفية بيضاء */
            padding: 5px 0;
            border-top: 1px solid #e0e0e0;
            box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.05);
        }
        
        /* تنسيق الأزرار داخل الشريط السفلي */
        .mobile-nav-container button {
            background: none;
            border: none;
            cursor: pointer;
            color: #7f8c8d; /* لون الأيقونات والنص الافتراضي (رمادي) */
            text-align: center;
            padding: 5px 0;
            transition: color 0.3s ease, transform 0.2s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            line-height: 1.2;
            font-size: 10px; /* حجم خط النص أسفل الأيقونة */
        }

        /* تأثير الزر النشط */
        .mobile-nav-container button:focus,
        .mobile-nav-container button:active {
            outline: none;
            box-shadow: none;
        }

        /* تنسيق الزر النشط */
        .mobile-nav-container button[data-testid^="stButton"]:has(.active) {
            color: #3498db !important; /* لون نشط (أزرق) */
            font-weight: bold;
            transform: translateY(-2px);
        }

        /* تطبيق لون الأيقونة */
        .mobile-nav-container button div[data-testid="stMarkdownContainer"] {
            font-size: 20px;
        }
        
        /* ======================================= */
        /* 3. تنسيق الشريط العلوي للإحصائيات */
        /* ======================================= */
        .top-stats-bar {
            padding: 10px 0;
            margin-bottom: 10px;
        }
        
        /* ضمان وجود مساحة أسفل المحتوى لمنع الشريط السفلي من حجب النص */
        .stApp {
            padding-bottom: 70px; /* مسافة كافية للشريط السفلي */
        }

        </style>
        """,
        unsafe_allow_html=True
    )

def render_more_pages():
    """عرض قائمة الصفحات الإضافية في قائمة منبثقة أو صفحة منفصلة (عند النقر على أيقونة المزيد)"""
    st.title("☰ المزيد من وحدات النظام")
    st.write("اختر الوحدة التي تريد التنقل إليها:")
    
    # استخدام st.columns لإنشاء شبكة من الأزرار
    cols_per_row = 3
    num_pages = len(MORE_PAGES)
    
    for i in range(0, num_pages, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < num_pages:
                page = MORE_PAGES[idx]
                with cols[j]:
                    # استخدام زر Streamlit لتغيير حالة التنقل
                    if st.button(f"{page['icon']} {page['label']}", key=f"more_nav_{page['id']}", use_container_width=True):
                        st.session_state.current_page = page['id']
                        st.rerun()

# إذا كانت الصفحة الحالية هي 'settings' (الإعدادات)، فعرض المزيد من الخيارات
def render_settings_or_more():
    if st.session_state.get('current_page') == 'settings':
        # نستخدم صفحة 'settings' كـ "المزيد" لعرض الخيارات الأخرى
        render_more_pages()
    else:
        # إذا كانت أي صفحة أخرى، نستخدم الدالة الأصلية
        pass 
