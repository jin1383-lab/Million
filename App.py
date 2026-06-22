import streamlit as st
import pandas as pd
import requests
import isodate

st.set_page_config(page_title="Pixeling Pro", page_icon="🌙", layout="wide")

st.markdown("""<style>
    .stApp { background-color: #0B0F19 !important; color: #E5E7EB; }
    .brand-title { font-size: 24pt; font-weight: 800; background: linear-gradient(135deg, #FF0055, #4FACFE); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .url-wrapper { background: #161D30; border-radius: 8px; padding: 10px; border: 1px solid #24314D; color: #FF3366; font-family: monospace; font-size: 9pt; margin-bottom: 15px; }
    .mvp-hero-card { background: linear-gradient(135deg, #1A1225, #131B2E); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #FF3366; }
    .grid-card { background: #131B2E; border-radius: 10px; border: 1px solid #212B41; padding: 15px; margin-bottom: 20px; height: auto; }
    .metric-box { background: #1A2338; border-radius: 6px; padding: 8px; margin-top: 5px; border: 1px solid #24314D; font-size: 9pt; }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="brand-title">Pixeling Categorized ⚡</div><div style="color:#9CA3AF;font-size:9pt;">YouTube Category Realtime Trending Engine</div><br>', unsafe_allow_html=True)

try: API_KEY = st.secrets["YOUTUBE_API_KEY"]
except: API_KEY = st.sidebar.text_input("API KEY", type="password")

# 🎯 유튜브 표준 15대 카테고리 맵핑 데이터베이스
CATEGORY_MAP = {
    "전체 (All)": None,
    "영화 & 애니메이션 (Film & Animation)": "1",
    "자동차 & 탈것 (Autos & Vehicles)": "2",
    "음악 (Music)": "10",
    "반려동물 & 동물 (Pets & Animals)": "15",
    "스포츠 (Sports)": "17",
    "여행 & 이벤트 (Travel & Events)": "19",
    "게임 (Gaming)": "20",
    "인물 & 블로그 (People & Blogs)": "22",
    "코미디 (Comedy)": "23",
    "엔터테인먼트 (Entertainment)": "24",
    "뉴스 & 정치 (News & Politics)": "25",
    "노하우 & 스타일 (Howto & Style)": "26",
    "교육 (Education)": "27",
    "과학 & 기술 (Science & Technology)": "28",
    "비영리 & 사회운동 (Nonprofits & Activism)": "29"
}

@st.cache_data(ttl=600)
def fetch_trending_youtube_data(days, cc, fmt, cat_id):
    if not API_KEY: return pd.DataFrame()
    url = "https://www.googleapis.com/youtube/v3/videos"
    data = []
    next_page_token = None
    
    # 카테고리 필터가 작동할 때 숏폼 샘플 풀을 유지하기 위해 고대역폭 4루프 유지
    max_loops = 4 if fmt == "숏폼 전용" else 2
    
    for _ in range(max_loops):
        p = {
            "part": "id,snippet,contentDetails,statistics",
            "chart": "mostPopular",
            "regionCode": cc,
            "maxResults": 50,
            "key": API_KEY
        }
        # 선택된 카테고리 고유 ID가 존재하면 매트릭스 주입
        if cat_id:
            p["videoCategoryId"] = cat_id
        if next_page_token:
            p["pageToken"] = next_page_token
            
        try: res = requests.get(url, params=p).json()
        except: break
        if "error" in res or "items" not in res: break

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
                "img": item["snippet"].get("thumbnails", {}).get("high", {}).get("url", "")
            })
            
        next_page_token = res.get("nextPageToken")
        if not next_page_token: break

    df = pd.DataFrame(data)
    if df.empty: return df
    
    df = df.drop_duplicates(subset=["handle"]).sort_values(by="view", ascending=False).reset_index(drop=True)
    return df.head(20)

st.sidebar.markdown("### ⚡ CATEGORY CONTROL")
# 15대 카테고리 셀렉트박스 추가
selected_cat_label = st.sidebar.selectbox("CATEGORY", list(CATEGORY_MAP.keys()))
target_cat_id = CATEGORY_MAP[selected_cat_label]

media_filter = st.sidebar.selectbox("FORMAT", ["전체 통합", "롱폼 전용", "숏폼 전용"])
period_label = st.sidebar.select_slider("PERIOD", options=["1D", "7D", "30D"])
days_param = 7 if period_label == "7D" else (30 if period_label == "30D" else 1)

nations = ["South Korea (KR)", "United States (US)"]
selected_nation = st.sidebar.selectbox("NATION", nations)
country_code = "US" if "US" in selected_nation else "KR"
run_engine = st.sidebar.button("RUN TRENDING ENGINE", type="primary", use_container_width=True)

if run_engine and API_KEY:
    with st.spinner(f"⚡ [{selected_cat_label}] 카테고리 실시간 데이터 매핑 중..."): 
        df = fetch_trending_youtube_data(days_param, country_code, media_filter, target_cat_id)
        
    if not df.empty:
        st.markdown(f'<div class="url-wrapper">🔥 MATRIX ACTIVE | {selected_cat_label} > {media_filter} ({country_code})</div>', unsafe_allow_html=True)
        
        # 👑 1위 MVP 대형 단독 레이아웃
        m = df.iloc[0]
        c = "color:#F87171;" if m['type'] == "Shorts" else "color:#60A5FA;"
        st.markdown(f"""<div class="mvp-hero-card"><div style="display:flex;justify-content:space-between;font-size:9pt;font-weight:600;"><span style="color:#FF0055;">🔥 CATEGORY NO.1</span><span style="{c}">{m['type']}</span></div><div style="display:flex;align-items:center;gap:15px;margin-top:10px;"><img src="{m['img']}" style="width:100px;height:70px;border-radius:6px;object-fit:cover;"><div style="flex-grow:1;"><div style="font-size:14pt;font-weight:800;color:#FFF;">{m['name']}</div><div style="color:#9CA3AF;font-size:9pt;">{m['handle']}</div></div><div><div class="metric-box"><span style="color:#9CA3AF;">트렌딩 뷰:</span> <b>{m['view']:,}회</b></div><div class="metric-box"><span style="color:#34D399;">추정수익:</span> <b style="color:#34D399;">₩{m['rev']:,}</b></div></div></div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"<h5 style='font-weight:700;color:#E5E7EB;margin-bottom:15px;'>👥 TOP 2 - {len(df)} CATEGORY LEADERS</h5>", unsafe_allow_html=True)
        g_data = df.iloc[1:].reset_index(drop=True)
        
        # 3열 고정 컨테이너 안정 풀 빌드
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
                        <div class="metric-box"><span style="color:#9CA3AF;">트렌딩 뷰:</span> <b>{item['view']:,}</b></div>
                        <div class="metric-box"><span style="color:#34D399;">예상수익:</span> <b style="color:#34D399;">₩{item['rev']:,}</b></div>
                    </div>
                </div>""", unsafe_allow_html=True)
    else: 
        st.warning("⚠️ 해당 카테고리 피드에서 조건에 맞는 실시간 트렌딩 데이터를 충분히 확보하지 못했습니다.")
else: 
    st.info("💡 카테고리와 설정을 세팅 후 [RUN TRENDING ENGINE]을 돌려주세요.")
