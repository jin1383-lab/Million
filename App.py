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

st.markdown('<div class="brand-title">Pixeling Trending ⚡</div><div style="color:#9CA3AF;font-size:9pt;">YouTube Realtime Trending v3 Engine</div><br>', unsafe_allow_html=True)

try: API_KEY = st.secrets["YOUTUBE_API_KEY"]
except: API_KEY = st.sidebar.text_input("API KEY", type="password")

@st.cache_data(ttl=600)  # 급상승 피드 특성 반영 시각 단축 (10분 캐시)
def fetch_trending_youtube_data(days, cc, fmt):
    if not API_KEY: return pd.DataFrame()
    url = "https://www.googleapis.com/youtube/v3/videos"
    data = []
    next_page_token = None
    
    # 숏폼 필터링 선택 시 트렌딩 풀에서 누락되지 않도록 4페이지(200개) 스캔 가동
    max_loops = 4 if fmt == "숏폼 전용" else 2
    
    for _ in range(max_loops):
        # chart="mostPopular"는 구글 API 공식 인기 급상승(Trending) 차트를 의미합니다.
        p = {
            "part": "id,snippet,contentDetails,statistics",
            "chart": "mostPopular",
            "regionCode": cc,
            "maxResults": 50,
            "key": API_KEY
        }
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
    
    # 트렌딩 중복 채널 디노이징 후 실시간 가중 스케일 정렬
    df = df.drop_duplicates(subset=["handle"]).sort_values(by="view", ascending=False).reset_index(drop=True)
    return df.head(20)

st.sidebar.markdown("### ⚡ TRENDING CONTROL")
media_filter = st.sidebar.selectbox("FORMAT", ["전체 통합", "롱폼 전용", "숏폼 전용"])
period_label = st.sidebar.select_slider("PERIOD", options=["1D", "7D", "30D"])
days_param = 7 if period_label == "7D" else (30 if period_label == "30D" else 1)

nations = ["South Korea (KR)", "United States (US)"]
selected_nation = st.sidebar.selectbox("NATION", nations)
country_code = "US" if "US" in selected_nation else "KR"
run_engine = st.sidebar.button("RUN TRENDING ENGINE", type="primary", use_container_width=True)

if run_engine and API_KEY:
    with st.spinner("⚡ 실시간 급상승 트렌딩 데이터 정밀 필터링 중..."): 
        df = fetch_trending_youtube_data(days_param, country_code, media_filter)
        
    if not df.empty:
        st.markdown(f'<div class="url-wrapper">🔥 TRENDING ACTIVE | 실시간 급상승 차트 매트릭스 가동 중 ({country_code})</div>', unsafe_allow_html=True)
        
        # 👑 1위 MVP 대형 단독 레이아웃
        m = df.iloc[0]
        c = "color:#F87171;" if m['type'] == "Shorts" else "color:#60A5FA;"
        st.markdown(f"""<div class="mvp-hero-card"><div style="display:flex;justify-content:space-between;font-size:9pt;font-weight:600;"><span style="color:#FF0055;">🔥 HOT TREND NO.1</span><span style="{c}">{m['type']}</span></div><div style="display:flex;align-items:center;gap:15px;margin-top:10px;"><img src="{m['img']}" style="width:100px;height:70px;border-radius:6px;object-fit:cover;"><div style="flex-grow:1;"><div style="font-size:14pt;font-weight:800;color:#FFF;">{m['name']}</div><div style="color:#9CA3AF;font-size:9pt;">{m['handle']}</div></div><div><div class="metric-box"><span style="color:#9CA3AF;">트렌딩 뷰:</span> <b>{m['view']:,}회</b></div><div class="metric-box"><span style="color:#34D399;">추정수익:</span> <b style="color:#34D399;">₩{m['rev']:,}</b></div></div></div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"<h5 style='font-weight:700;color:#E5E7EB;margin-bottom:15px;'>👥 TOP 2 - {len(df)} TRENDING LEADERS</h5>", unsafe_allow_html=True)
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
        st.warning("⚠️ 급상승 차트에서 조건에 맞는 실시간 데이터를 충분히 로드하지 못했습니다.")
else: 
    st.info("💡 사이드바 설정 후 [RUN TRENDING ENGINE]을 돌리면 실시간 급상승 1~20위 레이아웃이 빌드됩니다.")
