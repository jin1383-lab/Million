import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 1. 페이지 기본 설정 (픽셀링 고유의 다크/화이트 혼합 모던 룩 지향)
st.set_page_config(
    page_title="Pixeling Style - YouTube Discovery",
    page_icon="🚀",
    layout="wide"
)

# 픽셀링 특유의 깔끔하고 고급스러운 UI 스타일 시트 (CSS) 적용
st.markdown("""
    <style>
    .discovery-header { font-size: 24pt; font-weight: 800; color: #111111; margin-bottom: 2px; }
    .discovery-subheader { font-size: 10.5pt; color: #666666; margin-bottom: 30px; }
    .channel-card {
        background-color: #ffffff;
        border: 1px solid #eef0f4;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .channel-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        border-color: #d1d5db;
    }
    .rank-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 9pt;
    }
    .metric-label { font-size: 9pt; color: #888888; margin-bottom: 2px; }
    .metric-value { font-size: 12pt; font-weight: 700; color: #222222; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="discovery-header">🚀 채널 디스커버리 (Discovery)</div>', unsafe_allow_html=True)
st.markdown('<div class="discovery-subheader">조회수, 구독자 성장률, 추정 수익 리포트를 기반으로 필터링된 실시간 대한민국 트렌드 네트워크</div>', unsafe_allow_html=True)

# 2. [가상 디스커버리 엔진] 주소창 파라미터 구조와 일치하는 정밀 시뮬레이터
@st.cache_data
def fetch_discovery_data(sort, order, days, country):
    """픽셀링 API 명세와 연동되는 가상 백엔드 파이프라인"""
    np.random.seed(days + len(sort)) # 파라미터 변화에 따라 데이터 셋 셔플
    
    channels = [
        ("김프로 KIMPRO", "Shorts", "@kimpro"), ("구래 CuRe", "Shorts", "@cure"), 
        ("승비니 seungbini", "Shorts", "@seungbini"), ("슈카월드 스타일", "Long-form", "@syuka"),
        ("IT섭 ITSUB", "Long-form", "@itsub"), ("경제 읽어주는 남자", "Long-form", "@economy"),
        ("급상승 예능 숏", "Shorts", "@trending_short"), ("지식 보관소", "Long-form", "@knowledge"),
        ("먹방 마스터", "Shorts", "@mukbang"), ("무비 큐브", "Long-form", "@movie_cube")
    ]
    
    data = []
    for i, (name, m_type, handle) in enumerate(channels * 3):
        # 파라미터 수치(days)에 상응하는 가중치 조회수 연산 적용
        base_views = np.random.randint(1000000, 10000000) if m_type == "Shorts" else np.random.randint(100000, 2000000)
        daily_view = int(base_views * days * np.random.uniform(0.8, 1.2))
        subscribers = np.random.randint(500000, 15000000) if m_type == "Shorts" else np.random.randint(200000, 5000000)
        
        # RPM 단가 연산
        rpm = 55 if m_type == "Shorts" else 4500
        revenue = int((daily_view / 1000) * rpm)
        
        # 프로필 이미지 및 대표 영상 링크 더미 생성
        profile_img = f"https://picsum.photos/id/{(i+15)%100}/100/100.jpg"
        
        data.append({
            "channel_name": name,
            "handle": handle,
            "media_type": m_type,
            "daily_view": daily_view,
            "subscribers": subscribers,
            "estimated_revenue": revenue,
            "profile_image": profile_img
        })
        
    df = pd.DataFrame(data)
    
    # 정렬(sort) 및 정렬 방향(order) 파라미터 제어 레이어
    ascending_opt = True if order == "asc" else False
    if sort == "daily_view":
        df = df.sort_values(by="daily_view", ascending=ascending_opt)
    elif sort == "subscribers":
        df = df.sort_values(by="subscribers", ascending=ascending_opt)
    else:
        df = df.sort_values(by="estimated_revenue", ascending=ascending_opt)
        
    return df.head(15).reset_index(drop=True)

# 3. [프론트엔드] 픽셀링 URL 쿼리 스트링 구조를 고스란히 담아낸 사이드바 필터
st.sidebar.header("🎛️ Query Parameters")

# country=KR
country_opt = st.sidebar.selectbox("국가 선택 (country)", ["대한민국 (KR)", "미국 (US)", "일본 (JP)"])
country_code = "KR" if "대한민국" in country_opt else "US"

# days=1
days_opt = st.sidebar.radio("분석 기간 (days)", [1, 3, 7, 30], format_func=lambda x: f"{x}일 기준")

# sort=daily_view
sort_opt = st.sidebar.selectbox(
    "정렬 지표 (sort)", 
    ["daily_view (조회수)", "subscribers (구독자)", "estimated_revenue (예상수익)"]
)
sort_param = sort_opt.split(" ")[0]

# order=desc
order_opt = st.sidebar.radio("정렬 순서 (order)", ["desc (내림차순)", "asc (오름차순)"])
order_param = order_opt.split(" ")[0]

st.sidebar.markdown("---")
search_button = st.sidebar.button("⚡ 디스커버리 파이프라인 구동", type="primary", use_container_width=True)

# 4. 데이터 렌더링 파이프라인
if search_button:
    # 파라미터를 그대로 넘겨 픽셀링 구조의 데이터 확보
    df_discovery = fetch_discovery_data(sort=sort_param, order=order_param, days=days_opt, country=country_code)
    
    # 📌 현재 쿼리 파라미터 주소 상태를 상단에 세련되게 바(Bar) 형태로 표기
    current_url = f"https://app.pixeling.io/discovery/channels?sort={sort_param}&order={order_param}&days={days_opt}&country={country_code}"
    st.code(f"🔗 API Endpoint Status: {current_url}", language="bash")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🌟 [디자인 핵심] 표(Table) 형식을 완전히 탈피하여 픽셀링 특유의 카드 피드 레이아웃 전개
    for index, row in df_discovery.iterrows():
        rank = index + 1
        
        # HTML과 Streamlit 레이아웃 혼합을 통한 카드 컴포넌트 렌더링
        with st.container():
            st.markdown(f"""
            <div class="channel-card">
                <table style="width:100%; border:none; border-collapse:collapse;">
                    <tr>
                        <td style="width: 8%; text-align: center; vertical-align: middle;">
                            <span class="rank-badge">Top {rank}</span>
                        </td>
                        <td style="width: 10%; text-align: center; vertical-align: middle;">
                            <img src="{row['profile_image']}" style="border-radius: 50%; width: 65px; height: 65px; border: 2px solid #f1f3f7; object-fit: cover;">
                        </td>
                        <td style="width: 32%; vertical-align: middle; padding-left: 10px;">
                            <div style="font-size: 13pt; font-weight: 800; color: #111111; margin-bottom: 2px;">{row['channel_name']}</div>
                            <div style="font-size: 9.5pt; color: #0076ff; font-weight: 500;">{row['handle']} · <span style="color:#555;">{row['media_type']}</span></div>
                        </td>
                        <td style="width: 16%; vertical-align: middle; text-align: left;">
                            <div class="metric-label">기간 내 조회수</div>
                            <div class="metric-value">{row['daily_view']:,} 회</div>
                        </td>
                        <td style="width: 16%; vertical-align: middle; text-align: left;">
                            <div class="metric-label">총 구독자 수</div>
                            <div class="metric-value">{row['subscribers']:,} 명</div>
                        </td>
                        <td style="width: 18%; vertical-align: middle; text-align: left;">
                            <div class="metric-label">추정 채널 파트너 수익</div>
                            <div style="font-size: 12pt; font-weight: 700; color: #10b981;">₩{row['estimated_revenue']:,}</div>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

else:
    # 최초 진입 화면 디자인 안내
    st.info("💡 왼쪽 사이드바의 쿼리 매개변수(Query Parameters)를 설정하고 **[⚡ 디스커버리 파이프라인 구동]** 버튼을 누르면 픽셀링 규격의 데이터 피드가 활성화됩니다.")
    st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80", caption="Pixeling API Architecture Interface Simulation", use_container_width=True)
