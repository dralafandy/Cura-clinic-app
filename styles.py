import streamlit as st

# قائمة الصفحات الإضافية التي تظهر في شاشة 'المزيد' (More)
MORE_PAGES = [
    {'id': 'doctors', 'label': 'إدارة الأطباء', 'icon_data': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-stethoscope"><path d="M11.3 4a2 2 0 0 0-1.26.68L8 7.37"/><path d="M7 11.35 5.37 9.72A2 2 0 0 0 4 8.74V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v4.74a2 2 0 0 0-.64 1.35z"/><path d="M12 18V9.74a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v1.5"/><path d="M12 18a2 2 0 0 0 2 2h2v-6"/><path d="M12 18a2 2 0 0 1-2 2h-2v-6"/><path d="M14 18h-4"/></svg>'},
    {'id': 'treatments', 'label': 'العلاجات والخدمات', 'icon_data': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pill"><path d="m10.5 20.5-9-9a2.83 2.83 0 1 1 4-4l9 9"/><path d="M8.27 16.27 19.5 5.04"/><path d="M18.83 7.76a3 3 0 0 1 3 3v.17a2.83 2.83 0 0 1-4 4L11.5 22.5"/><path d="m14 8-6 6"/></svg>'},
    {'id': 'suppliers', 'label': 'إدارة الموردين', 'icon_data': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-truck"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H5"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.5a1 1 0 0 0-1-1h-1.5"/><path d="M19 18v-5.5"/><circle cx="7.5" cy="18.5" r="1.5"/><circle cx="17.5" cy="18.5" r="1.5"/></svg>'},
    {'id': 'expenses', 'label': 'المصروفات', 'icon_data': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-receipt-text"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M15 11H9"/><path d="M15 15H9"/></svg>'},
    {'id': 'reports', 'label': 'التقارير والإحصاء', 'icon_data': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bar-chart-3"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>'},
    {'id': 'activity_log', 'label': 'سجل الأنشطة', 'icon_data': '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-history"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-1.39 1.67"/><path d="M12 7v5l4 2"/><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.2 8.6c.7 1.3 1.7 2.4 2.9 3.2"/><path d="M17 14.8c1.2-.8 2.2-1.9 2.9-3.2"/></svg>'},
]


def load_custom_css():
    """تطبيق الـ CSS اللازم لتثبيت الشريط السفلي وتنسيقات الأيقونات."""
    
    # CSS العام
    css_code = """
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
        
        /* ضمان وجود مساحة أسفل المحتوى لمنع الشريط السفلي من حجب النص */
        .stApp {
            padding-bottom: 70px; 
        }
        
        /* تنسيق زر Streamlit العادي ليصبح أيقونة */
        .mobile-nav-container button[data-testid^="stButton"] {
            background: none !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            height: auto !important;
        }

        /* محتوى الزر (الأيقونة + النص) */
        .mobile-nav-container .nav-button-content {
            color: #7f8c8d; /* اللون الافتراضي (رمادي) */
            transition: color 0.3s ease;
            width: 100%;
        }

        /* الأيقونة داخل الزر */
        .mobile-nav-container .nav-icon svg {
            width: 20px;
            height: 20px;
            margin-bottom: 2px;
            stroke-width: 2.2; /* لجعل الأيقونة أكثر وضوحاً */
            transition: stroke 0.3s ease;
        }

        /* النص تحت الأيقونة */
        .mobile-nav-container .nav-label {
            font-size: 10px;
            white-space: nowrap;
        }
        
        /* تنسيق الزر النشط */
        .mobile-nav-container .nav-button-content.active {
            color: #3498db; /* لون نشط (أزرق طبي) */
            font-weight: bold;
        }
        
        .mobile-nav-container .nav-button-content.active .nav-icon svg {
            stroke: #3498db; 
        }

        /* ======================================= */
        /* 3. تنسيق شريط الإحصائيات العلوي */
        /* ======================================= */
        .top-stats-bar {
            padding: 5px 0 15px 0;
            border-bottom: 1px solid #f0f0f0;
            margin-bottom: 20px;
        }
        
        .stat-card {
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin: 5px;
        }
        
        .stat-success { background-color: #e6f7ff; color: #1890ff; border: 1px solid #91d5ff; } /* أزرق فاتح */
        .stat-warning { background-color: #fffbe6; color: #faad14; border: 1px solid #ffe58f; } /* برتقالي فاتح */
        .stat-error { background-color: #fff1f0; color: #f5222d; border: 1px solid #ffa39e; } /* أحمر فاتح */
        .stat-info { background-color: #f9f9f9; color: #595959; border: 1px solid #d9d9d9; } /* رمادي فاتح */
        
        /* ======================================= */
        /* 4. تنسيق شاشة 'المزيد' (More Pages) */
        /* ======================================= */
        .more-pages-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        
        .more-page-button {
            background-color: #f7f7f7;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
            cursor: pointer;
            height: 100%;
        }
        
        .more-page-button:hover {
            background-color: #ffffff;
            border-color: #3498db;
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.1);
        }

        .more-page-button .icon-svg svg {
            width: 30px;
            height: 30px;
            color: #3498db;
            margin-bottom: 10px;
            stroke-width: 2;
        }
        
        .more-page-button .label {
            font-size: 14px;
            font-weight: 600;
            color: #333;
        }

        </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)


def render_more_pages():
    """تُعرض هذه الدالة عندما يختار المستخدم أيقونة 'المزيد'."""
    st.header("إعدادات وإدارة النظام")
    st.markdown("---")
    
    st.markdown("<div class='more-pages-grid'>", unsafe_allow_html=True)

    cols_per_row = 2 # عرض زرين في كل صف على الهاتف
    num_pages = len(MORE_PAGES)
    
    for i in range(0, num_pages, cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < num_pages:
                page = MORE_PAGES[idx]
                with cols[j]:
                    
                    # استخدام زر Streamlit لتغيير حالة التنقل
                    if st.button(
                        label=f"<div class='icon-svg'>{page['icon_data']}</div><div class='label'>{page['label']}</div>", 
                        key=f"more_nav_{page['id']}", 
                        use_container_width=True
                    ):
                        st.session_state.current_page = page['id']
                        st.rerun()

                    # تطبيق CSS على الزر عبر حقن HTML
                    st.markdown(
                        f"""
                        <script>
                        // لتطبيق الـ CSS بشكل صحيح على زر Streamlit
                        const button = document.querySelector('[data-testid="stButton"] button[key="more_nav_{page['id']}"]');
                        if (button) {{
                            button.parentElement.classList.add('more-page-button-container');
                            button.innerHTML = button.innerText; // استبدال محتوى الزر لتمكين HTML المخصص
                        }}
                        </script>
                        """, 
                        unsafe_allow_html=True
                    )
                    
                    st.markdown(
                        f"<div class='more-page-button'>{page['icon_data']}<div class='label'>{page['label']}</div></div>",
                        unsafe_allow_html=True
                    )
                    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # إضافة زر العودة للإعدادات الرئيسية
    st.markdown("---")
    if st.button("⚙️ إعدادات النظام المتقدمة", key="btn_actual_settings"):
        st.session_state.current_page = 'settings_actual'
        st.rerun()

    

