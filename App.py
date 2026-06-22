import streamlit as st
import pandas as pd
import requests
import isodate
import datetime

# 1. 글로벌 페이지 인프라 및 테마 빌드
st.set_page_config(
    page_title="Pixeling Pro - Intelligent YouTube Discovery",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🚀 글로벌 CSS 오버라이드 (Modern Dark-Mode Accent & Light Grid Mix)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #FAFAFB; }
    
    /* 헤더 디자인 파트 */
    .brand-container { padding: 10px 0px 20px 0px; }
    .brand-title { font-size: 28pt; font-weight: 800; letter-spacing: -1px; background: linear-gradient(135deg, #FF1E27 0%, #FE5858 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .brand-subtitle { font-size: 11pt; color: #6B7280; font-weight: 400; margin-top: 4px; }
    
    /* 🔗 Endpoint 상태 바 커스텀 */
    .url-wrapper { background-color: #111827; border-radius: 12px; padding: 14px 20px; border: 1px solid #1F2937; margin-bottom: 30px; font-family: monospace; color: #34D399; font-size: 10pt; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    
    /* 🔥 MVP 1위 독점 카드 디자인 */
    .mvp-hero-card {
        background: #111827;
        border-radius: 20px;
        padding: 30px;
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
        margin-bottom: 25px;
        border: 1px solid #374151;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    }
    .mvp-hero-card::after {
        content: ''; position: absolute; top: -50%; right: -20%; width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(255,30,39,0.15) 0%, rgba(0,0,0,0) 70%);
    }
    
    /* 👥 일반 랭킹 카드 컨테이너 (그리드 최적화) */
    .grid-card {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        padding: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.01);
    }
    .grid-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.04);
        border-color: #D1D5DB;
    }
    
    /* 🏷️ 정밀 배지 공통 */
    .badge-mvp { background: #FF1E27; color: white; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 8.5pt; text-transform: uppercase; }
    .badge-rank { background: #E5E7EB; color: #1F2937; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 8.5pt; }
    .tag-format-shorts { background: rgba(239, 68, 68, 0.1); color: #EF4444; padding: 2px 8px; border-radius: 6px; font-size: 8pt; font-weight: 600; }
    .tag-format-long { background: rgba(59, 130, 246, 0.1); color: #3B82F6; padding: 2px 8px; border-radius: 6px; font-size: 8pt; font-weight: 600; }
    
    /* 📈 데이터 폰트 스케일링 */
    .card-title { font-size: 13pt; font-weight: 700; color: #111827; margin: 10px 0px 2px 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .card-handle { font-size: 9.5pt; color: #9CA3AF; margin-bottom: 15px; }
    .metric-box { background: #F9FAFB; border-radius: 10px; padding: 12px; margin-top: 8px; border: 1px solid #F3F4F6; }
    .metric-box-dark { background: #1F2937; border-radius: 10px; padding: 12px; margin-top: 8px; }
    .lbl { font-size: 8.5pt; color: #6B7280; font-weight: 500; margin-bottom: 2px; }
    .lbl-dark { font-size: 8.5pt; color: #9CA3AF; font-weight: 500; margin-bottom: 2px; }
    .val { font-size: 13pt; font-weight: 700; color: #111827; }
    .val-dark { font-size: 13pt; font-weight: 700; color: #FFFFFF; }
    .val-revenue { font-size: 13pt; font-weight: 700; color: #10B981; }
    </style>
""", unsafe_allow_html=True)

# 메인 헤더 세팅
st.markdown("""
<div class="brand-container">
    <div class="brand-title">Pixeling Pro</div>
    <div class="brand-subtitle">공식 YouTube v3 Data API 기반 미디어 포맷별 실시간 성장 랭킹 매트릭스 시스템</div>
</div>
""", unsafe_allow_html=True)

# 2. API 인증 검증 및 보호 레이어
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("⚠️ Streamlit Secrets 내의 API 키 감지 실패")
    API_KEY = st.sidebar.text_input("구글 API 키 직접 주입", type="password")

# 3. [Real 백엔드 데이터 프로세서] 
@st.cache_data(ttl=1200)
def fetch_premium_youtube_data(period_days, country_code, media_filter):
    if not API_KEY: return pd.DataFrame()
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "id,snippet,contentDetails,statistics",
        "chart": "mostPopular",
        "regionCode": country_code,
        "maxResults": 50,
        "key": API_KEY
    }
    try: response = requests.get(url, params=params).json()
    except Exception: return pd.DataFrame()
    if "error" in response: return pd.DataFrame()

    data = []
    if "items" in response:
        for item in response["items"]:
            v_id = item["id"]
            snippet = item["snippet"]
            content_details = item["contentDetails"]
            stats = item.get("statistics", {})
            
            # ISO 8601 타
