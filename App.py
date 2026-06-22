import streamlit as st
import pandas as pd
import requests
import isodate

# 1. 페이지 테마 설정
st.set_page_config(page_title="Pixeling Pro - Top 20 Matrix", page_icon="🌙", layout="wide")

# 🚀 경량 다크모드 인젝션
st.markdown("""
    <style>
    .stApp { background-color: #0B0F19 !important; color: #E5E7EB; }
    .brand-title { font-size: 26pt; font-weight: 800; background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .url-wrapper { background-color: #161D30; border-radius: 10px; padding: 12px; border: 1px solid #24314D; font-family: monospace; color: #34D399; font-size: 9.5pt; margin-bottom: 20px; }
    .mvp-hero-card { background: linear-gradient(135deg, #131B2E, #1A2338); border-radius: 16px; padding: 25px; margin-bottom: 25px; border: 1px solid #34D399; }
    .grid-card { background: #131B2E; border-radius: 12px; border: 1px solid #212B41; padding: 20px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .grid-card:hover { border-color: #3B82F6; }
    .badge-mvp { background: #FF1E27; color: white; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 8pt; }
    .badge-rank { background: #1F2937; color: #F3F4F6; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 8pt; }
    .metric-box { background: #1A2338; border-radius: 8px; padding: 10px; margin-top: 8px; border: 1px solid #24314D; }
    .lbl { font-size: 8pt; color: #9CA3AF; }
    .val { font-size: 11pt; font-weight: 700; color: #FFFFFF; }
    .val-rev { font-size: 11pt; font-weight: 700; color: #34D399; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand-container"><div class="brand-title">Pixeling Pro 🌙</div><div style="color:#9CA3AF; font-size:10pt;">YouTube Live v3 API Cyber Edition</div></div><br>', unsafe_allow_html=True)

# 2. API Key 보안 검증
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    API_KEY = st.sidebar.text_input("구글 API 키 입력", type="password")

# 3. 라이브 데이터 파이프라인
@st.cache_data(ttl=1200)
def fetch_premium_youtube_data(period_days, country_code, media_filter):
    if not API_KEY: return pd.DataFrame()
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {"part": "id,snippet,contentDetails,statistics", "chart": "mostPopular", "regionCode": country_code, "maxResults": 50, "key": API_KEY}
    try: response = requests.get(url, params=params).json()
    except Exception: return pd.DataFrame()
    if "error" in response: return pd.DataFrame()

    data = []
    if "items" in response:
        for item in response["items"]:
            v_id = item["id"]
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            duration_str = item["contentDetails"].get("duration", "PT0S")
            try: duration_secs = isodate.parse_duration(duration_str).total_seconds()
            except Exception: duration_secs = 0
            
            media_type = "Shorts" if duration_secs <= 60 else "Long-form"
            if media_filter == "롱폼 전용" and media_type != "Long-form": continue
            if media_filter == "숏폼 전용" and media_type != "Shorts": continue
                
            rpm = 110 if media_type == "Shorts" else 9000 if country_code == "US" else 4500
            real_views = int(stats.get("viewCount", 0))
            calculated_views = int(real_views * (1 if period_days == 1 else (period_days * 0.4)))
            
            data.append({
                "channel_name": snippet.get("channelTitle", "익명"),
                "handle": f"@{snippet.get('channelId')[:12]}",
                "media_type": media_type,
                "period_view": calculated_views,
                "likes": int(stats.get("likeCount", 0)),
                "estimated_revenue": int((calculated_views / 1000) * rpm),
                "profile_image": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            })
    df = pd.DataFrame(data)
    if not df.empty: df = df.sort_values(by="period_view", ascending=False).reset_index(drop=True)
    return df.head(20)

# 4. 사이드바 제어판
st.sidebar.markdown("### 🎛️ CYBER CONTROL")
media_filter = st.sidebar.selectbox("FORMAT", ["전체 통합", "롱폼 전용", "숏폼 전용"])
period_label = st.sidebar.select_slider("PERIOD", options=["일별 (1D)", "주별 (7D)", "달별 (30D)"])
days_param = 1 if "일별" in period_label else (
