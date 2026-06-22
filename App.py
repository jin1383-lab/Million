import streamlit as st
import pandas as pd
import requests
import isodate

st.set_page_config(page_title="Pixeling Pro", page_icon="🌙", layout="wide")

# 🚀 다크 모드 스타일 레이어
st.markdown("""<style>
    .stApp { background-color: #0B0F19 !important; color: #E5E7EB; }
    .brand-title { font-size: 24pt; font-weight: 800; background: linear-gradient(135deg, #00F2FE, #4FACFE); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .url-wrapper { background: #161D30; border-radius: 8px; padding: 10px; border: 1px solid #24314D; color: #34D399; font-family: monospace; font-size: 9pt; margin-bottom: 15px; }
    .mvp-hero-card { background: linear-gradient(135deg, #131B2E, #1A2338); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #34D399; }
    .grid-card { background: #131B2E; border-radius: 10px; border: 1px solid #212B41; padding: 15px; height: 100%; display: flex; flex-direction: column; justify-content: space-between; }
    .metric-box { background: #1A2338; border-radius: 6px; padding: 8px; margin-top: 5px; border: 1px solid #24314D; font-size: 9pt; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="brand-title">Pixeling Pro 🌙</div><div style="color:#9CA3AF;font-size:9pt;">YouTube Live v3 API Cyber Edition</div><br>', unsafe_allow_html=True)

try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
except:
    API_KEY = st.sidebar.text_input("API KEY", type="password")

@st.cache_data(ttl=1200)
def fetch_premium_youtube_data(days, cc, fmt):
    if not API_KEY: return pd.DataFrame()
    url = "https://www.googleapis.com/youtube/v3/videos"
    p = {"part": "id,snippet,contentDetails,statistics", "chart": "mostPopular", "regionCode": cc, "maxResults": 50, "key": API_KEY}
    try: res = requests.get(url, params=p).json()
    except: return pd.DataFrame()
    if "error" in res or "items" not in res: return pd.DataFrame()

    data = []
    for item in res["items"]:
        stats = item.get("statistics", {})
        try: secs = isodate.parse_duration(item["contentDetails"].get("duration", "PT0S")).total_seconds()
        except: secs = 0
        m_type = "Shorts" if secs <= 60 else "Long-form"
        if (fmt == "롱폼 전용" and m_type != "Long-form") or (fmt == "숏폼 전용" and m_type != "Shorts"): continue
        
        rpm = 110 if m_type == "Shorts" else 9000 if cc == "US" else 4500
        v_count = int(stats.get("viewCount", 0))
        p_view = int(v_count * (1 if days == 1 else days * 0.4))
        
        data.append({
            "name": item["snippet"].get("channelTitle", "익명"),
            "handle": f"@{item['snippet'].get('channelId')[:12]}",
            "type": m_type, "view": p_view,
            "rev": int((p_view / 1000) * rpm),
