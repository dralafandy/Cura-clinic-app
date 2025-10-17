import streamlit as st

def load_custom_css():
    """تحميل الأنماط المخصصة"""
    st.markdown("""
    <style>
        /* تحسين الخط العربي */
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Cairo', sans-serif;
        }
        
        /* البطاقات */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .metric-card.success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        
        .metric-card.warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        
        .metric-card.info {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        
        .metric-card.danger {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .metric-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        /* ========== الشريط الجانبي ========== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        }
        
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p {
            color: white !important;
        }
        
        /* أزرار القائمة الجانبية */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background-color: rgba(255, 255, 255, 0.1);
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 15px;
            font-weight: 500;
            text-align: right;
            direction: rtl;
            transition: all 0.3s ease;
            margin: 5px 0;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background-color: rgba(102, 126, 234, 0.8);
            border-color: rgba(102, 126, 234, 1);
            color: #ffffff !important;
            transform: translateX(-5px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        [data-testid="stSidebar"] .stButton > button:active,
        [data-testid="stSidebar"] .stButton > button:focus {
            background-color: rgba(102, 126, 234, 1);
            border-color: rgba(102, 126, 234, 1);
            color: #ffffff !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
        }
        
        [data-testid="stSidebar"] .element-container div[data-testid="stMarkdownContainer"] p {
            color: white !important;
        }
        
        [data-testid="stSidebar"] .stAlert {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        [data-testid="stSidebar"] .stSuccess {
            background-color: rgba(56, 239, 125, 0.2) !important;
            color: #38ef7d !important;
            border: 1px solid rgba(56, 239, 125, 0.4);
        }
        
        [data-testid="stSidebar"] .stWarning {
            background-color: rgba(255, 193, 7, 0.2) !important;
            color: #ffc107 !important;
            border: 1px solid rgba(255, 193, 7, 0.4);
        }
        
        [data-testid="stSidebar"] .stError {
            background-color: rgba(220, 53, 69, 0.2) !important;
            color: #ff6b6b !important;
            border: 1px solid rgba(220, 53, 69, 0.4);
        }
        
        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.2);
        }
        
        [data-testid="stSidebar"] * {
            color: #ffffff;
        }
        
        [data-testid="stSidebar"] button span {
            color: #ffffff !important;
        }
        
        /* الأزرار العادية */
        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        /* العنوان الرئيسي */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        /* تقرير المريض */
        .patient-report {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        
        .report-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .report-section {
            border-left: 4px solid #667eea;
            padding-left: 15px;
            margin: 20px 0;
        }
        
        .report-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        
        .report-table th {
            background-color: #f8f9fa;
            padding: 10px;
            text-align: right;
            border-bottom: 2px solid #dee2e6;
        }
        
        .report-table td {
            padding: 10px;
            border-bottom: 1px solid #dee2e6;
        }
        
        /* تحسين المدخلات */
        .stTextInput>div>div>input, .stSelectbox>div>div>select {
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            padding: 10px;
        }
        
        .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
    </style>
    """, unsafe_allow_html=True)
