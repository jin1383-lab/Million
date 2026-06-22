import streamlit as st
import pandas as pd
import requests
import isodate
from datetime import datetime, timezone

st.set_page_config(page_title="Pixeling Pro", page_icon="🌙", layout="wide")

st.markdown("""<style>
    .stApp { background-color: #0B0F19 !important; color: #E5E7EB; }
    .brand-title { font-size: 24pt; font-weight: 800; background: linear-gradient(135deg, #FF0055, #4FACFE); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .url-wrapper { background: #161D30; border-radius: 8px; padding: 10px; border: 1px solid #24314D; color: #34D399; font-family: monospace; font-size: 9pt; margin-bottom: 15px; }
    .mvp-hero-card { background: linear-gradient(135deg, #1A1225, #131B2E); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #FF3366; }
    .grid-card { background: #131B2E; border-radius: 10px; border: 1px solid #212B41; padding: 15px; margin-bottom: 20px; height: auto; }
    .metric-box { background: #1A2338; border-radius: 6px; padding: 8px; margin-top: 5px; border: 1px solid #24314D; font-size: 9pt; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="brand-title">Pixeling Advanced Matrix ⚡</div><div style="color:#9CA3AF;font-size:9pt;">YouTube Daily-Average Based Analytics Engine</div><br>', unsafe_allow_html=True)

try: API_KEY = st.secrets["YOUTUBE_API_KEY"]
except: API_KEY = st.sidebar.text_input("API KEY", type="password")

CATEGORY_MAP = {
    "전체 (All)": None, "영화 & 애니메이션": "1", "자동차 & 탈것": "2", "음악": "10", 
    "반려동물 & 동물": "15", "스포츠": "17", "여행 & 이벤트": "19", "게임": "20", 
    "인물 & 블로그": "22", "코미디": "23", "엔터테인먼트": "24", "뉴스 & 정치": "25", 
    "노하우 & 스타일": "26", "교육": "27", "과학 & 기술": "28"
}

@st.cache_data(ttl=600)
def fetch_advanced_trending_data(days, cc, fmt, cat_id):
    if not API_KEY: return pd.DataFrame()
    url = "https://www.googleapis.com/youtube/v3/videos"
    data = []
    next_page_token = None
    max_loops = 4 if fmt == "숏폼 전용" else 2
    
    now = datetime.now(timezone.utc)
    
    for _ in range(max_loops):
        p = {"part": "id,snippet,contentDetails,statistics", "chart": "mostPopular", "regionCode": cc, "maxResults": 50, "key": API_KEY}
        if cat_id: p["videoCategoryId"] = cat_id
        if next_page_token: p["pageToken"] = next_page_token
            
        try: res = requests.get(url, params=p).json()
        except: break
        if "error" in res or "items" not in res: break

        for item in res["items"]:
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            
            # 1. 숏폼/롱폼 시간 분류
            try: secs = isodate.parse_duration(item["contentDetails"].get("duration", "PT0S")).total_seconds()
            except: secs = 0
            m_type = "Shorts" if secs <= 60 else "Long-form"
            if (fmt == "롱폼 전용" and m_type != "Long-form") or (fmt == "숏폼 전용" and m_type != "Shorts"): continue
            
            # 2. 고도화 핵심: 업로드 경과 일수(Age) 계산
            published_at_str = snippet.get("publishedAt")
            try:
                published_at = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                elapsed_days = (now - published_at).days + (now - published_at).seconds / 86400.0
                if elapsed_days < 0.1: elapsed_days = 0.1 # 오늘 막 올라온 영상 분모 예외 처리
            except:
                elapsed_days = 1.0
            
            # 3. 1일 평균 조회수 추출 및 설정 기간(days)별 스케일링
            total_views = int(stats.get("viewCount", 0))
            daily_avg_view = total_views / elapsed_days
            calculated_period_view = int(daily_avg_view * days)
            
            # 4. 수익 산정
            rpm = 110 if m_type == "Shorts" else 9000 if cc == "US" else 4500
            estimated_revenue = int((calculated_period_view / 1000) * rpm)
            
            data.append({
                "name": snippet.get("channelTitle", "익명"),
                "handle": f"@{snippet.get('channelId')[:12]}",
                "type": m_type, 
                "view": calculated_period_view, # 선택 기간에 정비례하는 수치
                "rev": estimated_revenue,
                "img": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
            })
            
        next_page_token = res.get("nextPageToken")
        if not next_page_token: break

    df = pd.DataFrame(data)
    if df.empty: return df
    
    # 1일 평균 기준으로 스케일링된 조회수 상위 20위 정렬
    df = df.drop_duplicates(subset=["handle"]).sort_values(by="view", ascending=False).reset_index(drop=True)
    return df.head(20)

st.sidebar.markdown("### ⚡ ADVANCED CONTROL")
selected_cat_label = st.sidebar.selectbox("CATEGORY", list(CATEGORY_MAP.keys()))
target_cat_id = CATEGORY_MAP[selected_cat_label]

media_filter = st.sidebar.selectbox("FORMAT", ["전체 통합", "롱폼 전용", "숏폼 전용"])
period_label = st.sidebar.select_slider("PERIOD", options=["1D", "7D", "30D"])
days_param = 7 if period_label == "7D" else (30 if period_label == "30D" else 1)

nations = ["South Korea (KR)", "United States (US)"]
selected_nation = st.sidebar.selectbox("NATION", nations)
country_code = "US" if "US" in selected_nation else "KR"
run_engine = st.sidebar.button("RUN ADVANCED ENGINE", type="primary", use_container_width=True)

if run_engine and API_KEY:
    with st.spinner(f"⚡ 1일 평균 조회수 기반 트렌딩 매트릭스 연산 중..."): 
        df = fetch_advanced_trending_data(days_param, country_code, media_filter, target_cat_id)
        
    if not df.empty:
        st.markdown(f'<div class="url-wrapper">🔗 ENGINE ACTIVE | {period_label} 기간 예측 수치 출력 적용됨 ({country_code})</div>', unsafe_allow_html=True)
        
        # 👑 1위 MVP 대형 단독 레이아웃
        m = df.iloc[0]
        c = "color:#F87171;" if m['type'] == "Shorts" else "color:#60A5FA;"
        st.markdown(f"""<div class="mvp-hero-card"><div style="display:flex;justify-content:space-between;font-size:9pt;font-weight:600;"><span style="color:#FF0055;">🔥 {period_label} GROWTH NO.1</span><span style="{c}">{m['type']}</span></div><div style="display:flex;align-items:center;gap:15px;margin-top:10px;"><img src="{m['img']}" style="width:100px;height:70px;border-radius:6px;object-fit:cover;"><div style="flex-grow:1;"><div style="font-size:14pt;font-weight:800;color:#FFF;">{m['name']}</div><div style="color:#9CA3AF;font-size:9pt;">{m['handle']}</div></div><div><div class="metric-box"><span style="color:#9CA3AF;">{period_label} 환산 조회수:</span> <b>{m['view']:,}회</b></div><div class="metric-box"><span style="color:#34D399;">{period_label} 예측수익:</span> <b style="color:#34D399;">₩{m['rev']:,}</b></div></div></div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"<h5 style='font-weight:700;color:#E5E7EB;margin-bottom:15px;'>👥 TOP 2 - {len(df)} PERIOD TREND LEADERS</h5>", unsafe_allow_html=True)
        g_data = df.iloc[1:].reset_index(drop=True)
        
        total_rows = (len(g_data) + 2) // 3
        grid_rows = [st.columns(3) for _ in range(total_rows)]
        
        for idx in range(len(g_data)):
            row_pos = idx // 3
            col_pos = idx % 3
            item = g_data.iloc[idx]
            tc = "color:#F87171;" if item['type'] == "Shorts" else "color:#60A5FA;"
            
            with grid_rows[row_pos][col_pos]:
                st.markdown(f"""<div class="grid-card">
                    <div>
                        <div style="display:flex;justify-content:space-between;font-size:8pt;"><b>TOP {idx+2}</b><span style="{tc}">{item['type']}</span></div>
                        <img src="{item['img']}" style="width:100%;height:120px;border-radius:6px;object-fit:cover;margin:8px 0;border:1px solid #24314D;">
                        <div style="font-size:10.5pt;font-weight:700;color:#FFF;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{item['name']}</div>
                        <div style="color:#9CA3AF;font-size:8.5pt;margin-bottom:8px;">{item['handle']}</div>
                    </div>
                    <div>
                        <div class="metric-box"><span style="color:#9CA3AF;">{period_label} 뷰:</span> <b>{item['view']:,}</b></div>
                        <div class="metric-box"><span style="color:#34D399;">예상수익:</span> <b style="color:#34D399;">₩{item['rev']:,}</b></div>
                    </div>
                </div>""", unsafe_allow_html=True)
    else: 
        st.warning("⚠️ 카테고리 내에서 조건에 맞는 트렌딩 연산 데이터를 확보하지 못했습니다.")
else: 
    st.info("💡 사이드바 필터 조정 후 [RUN ADVANCED ENGINE]을 작동시켜 주세요.")
