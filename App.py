import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Pixeling Style - YouTube Discovery",
    page_icon="🚀",
    layout="wide"
)

# UI 디자인 스타일 시트 (CSS)
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
st.markdown('<div class="discovery-subheader">조회수, 구독자 성장률, 추정 수익 리포트를 기반으로 필터링된 실시간 트렌드 네트워크</div>', unsafe_allow_html=True)

# 2. [가상 디스커버리 엔진] 국가(KR/US) 분기 연산 기능이 완전 탑재된 함수
@st.cache_data
def fetch_discovery_data(sort, order, days, country):
    np.random.seed(days + len(sort) + len(country))
    
    # 국가 파라미터에 따른 글로벌 채널 셋 및 단가(RPM) 분기
    if country == "US":
        channels = [
            ("MrBeast Style", "Long-form", "@mrbeast_style"),
            ("Zach King Vids", "Shorts", "@zachking_clone"),
            ("Tech Reviewer US", "Long-form", "@us_tech"),
            ("Daily US Shorts", "Shorts", "@daily_us"),
            ("Hollywood Behind", "Long-form", "@hollywood_cube"),
            ("Gaming Zone US", "Long-form", "@us_gaming"),
            ("NYC Vlog Diary", "Shorts", "@nyc_vlog")
        ]
        rpm_long, rpm_shorts = 9000, 110  # 미국의 고단가 가중치 적용
    else:
        channels = [
            ("김프로 KIMPRO", "Shorts", "@kimpro"),
            ("구래 CuRe", "Shorts", "@cure"),
            ("승비니 seungbini", "Shorts", "@seungbini"),
            ("슈카월드 스타일", "Long-form", "@syuka"),
            ("IT섭 ITSUB", "Long-form", "@itsub"),
            ("경제 읽어주는 남자", "Long-form", "@economy"),
            ("급상승 예능 숏", "Shorts", "@trending_short")
        ]
        rpm_long, rpm_shorts = 4500, 55

    data = []
    for i, (name, m_type, handle) in enumerate(channels * 3):
        base_views = np.random.randint(2000000, 20000000) if m_type == "Shorts" else np.random.randint(200000, 4000000)
        daily_view = int(base_views * days * np.random.uniform(0.8, 1.2))
        subscribers = np.random.randint(1000000, 50000000) if m_type == "Shorts" else np.random.randint(500000, 10000000)
        
        # 지정된 국가별 분류 단가 대입
        rpm = rpm_shorts if m_type == "Shorts" else rpm_long
        revenue = int((daily_view / 1000) * rpm)
        
        profile_img = f"https://picsum.photos/id/{(i+35)%100}/100/100.jpg"
        
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
    
    ascending_opt = True if order == "asc" else False
    df = df.sort_values(by=sort, ascending=ascending_opt)
        
    return df.head(15).reset_index(drop=True)

# 3. [프론트엔드] 사이드바 필터 파라미터 구조
st.sidebar.header("🎛️ Query Parameters")

country_opt = st.sidebar.selectbox("국가 선택 (country)", ["대한민국 (KR)", "미국 (US)"])
country_code = "US" if "미국" in country_opt else "KR"

days_opt = st.sidebar.radio("분석 기간 (days)", [1, 3, 7, 30], format_func=lambda x: f"{x}일 기준")

sort_opt = st.sidebar.selectbox("정렬 지표 (sort)", ["daily_view", "subscribers", "estimated_revenue"])
order_opt = st.sidebar.radio("정렬 순서 (order)", ["desc", "asc"])

st.sidebar.markdown("---")
search_button = st.sidebar.button("⚡ 디스커버리 파이프라인 구동", type="primary", use_container_width=True)

# 4. 결과 출력
if search_button:
    df_discovery = fetch_discovery_data(sort=sort_opt, order=order_opt, days=days_opt, country=country_code)
    
    current_url = f"https://app.pixeling.io/discovery/channels?sort={sort_opt}&order={order_opt}&days={days_opt}&country={country_code}"
    st.code(f"🔗 API Endpoint Status: {current_url}", language="bash")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    for index, row in df_discovery.iterrows():
        rank = index + 1
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
    st.info("💡 왼쪽 사이드바의 쿼리 매개변수를 설정하고 **[⚡ 디스커버리 파이프라인 구동]** 버튼을 누르면 픽셀링 규격의 데이터 피드가 활성화됩니다.")
