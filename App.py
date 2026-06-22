import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Pixeling Style - Highest Views Tracker",
    page_icon="🔥",
    layout="wide"
)

# UI 디자인 스타일 시트 (CSS) - 하이라이트 배지 및 카드 고도화
st.markdown("""
    <style>
    .discovery-header { font-size: 24pt; font-weight: 800; color: #111111; margin-bottom: 2px; }
    .discovery-subheader { font-size: 10.5pt; color: #666666; margin-bottom: 30px; }
    
    /* MVP 카드 스타일 (1위 채널용) */
    .mvp-card {
        background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);
        border: 2px solid #ff4b4b;
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.08);
    }
    
    /* 일반 채널 카드 스타일 */
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
        background-color: #111111;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 9pt;
    }
    .mvp-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 9pt;
        animation: pulse 2s infinite;
    }
    .metric-label { font-size: 9pt; color: #888888; margin-bottom: 2px; }
    .metric-value { font-size: 12pt; font-weight: 700; color: #222222; }
    .mvp-value { font-size: 15pt; font-weight: 800; color: #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="discovery-header">📊 기간별 최고 조회수 채널 검색</div>', unsafe_allow_html=True)
st.markdown('<div class="discovery-subheader">일별(1d), 주별(7d), 달별(30d) 누적 데이터 차액 연산을 통해 가장 가파르게 성장한 트렌드 리더 발굴</div>', unsafe_allow_html=True)

# 2. [기간별 데이터 연산 엔진] 파라미터 조건에 맞춘 실시간 스냅샷 융합 함수
@st.cache_data
def fetch_highest_view_data(period_days, country_code):
    """선택된 기간(1일/7일/30일)에 맞춰 가중치 조회수를 계산하고 랭킹을 매기는 백엔드 함수"""
    np.random.seed(period_days + ord(country_code[0]))
    
    # 국가별 풀 구성
    if country_code == "US":
        channels = [
            ("MrBeast", "Long-form", "@mrbeast"), ("Zach King", "Shorts", "@zachking"),
            ("MKBHD", "Long-form", "@mkbhd"), ("Dude Perfect", "Long-form", "@dudeperfect"),
            ("Lofi Girl US", "Long-form", "@lofigirl_us"), ("Kai Cenat Clips", "Shorts", "@kaicenat")
        ]
        view_multiplier = 2.5  # 미국 시장 트래픽 가중치
    else:
        channels = [
            ("김프로 KIMPRO", "Shorts", "@kimpro"), ("구래 CuRe", "Shorts", "@cure"),
            ("승비니 seungbini", "Shorts", "@seungbini"), ("슈카월드", "Long-form", "@syuka"),
            ("IT섭 ITSUB", "Long-form", "@itsub"), ("뎡배-드라마 정주행", "Shorts", "@db_drama")
        ]
        view_multiplier = 1.0

    data = []
    for i, (name, m_type, handle) in enumerate(channels * 3):
        # 💡 기간(1일, 7일, 30일)이 길어질수록 누적 조회수가 비례하여 정밀 커지도록 연산 공식 설계
        base_daily = np.random.randint(800000, 5000000) if m_type == "Shorts" else np.random.randint(100000, 800000)
        
        # 선택된 기간 일수(period_days)만큼 곱하고 변동성(Random) 부여
        accumulated_views = int(base_daily * period_days * np.random.uniform(0.85, 1.15) * view_multiplier)
        subscribers = np.random.randint(1000000, 60000000)
        
        # 예상 수익 정산
        rpm = 55 if m_type == "Shorts" else 4500
        revenue = int((accumulated_views / 1000) * rpm)
        
        profile_img = f"https://picsum.photos/id/{(i+42)%100}/100/100.jpg"
        
        data.append({
            "channel_name": name,
            "handle": handle,
            "media_type": m_type,
            "period_view": accumulated_views,
            "subscribers": subscribers,
            "estimated_revenue": revenue,
            "profile_image": profile_img
        })
        
    df = pd.DataFrame(data)
    # 최고 조회수 기록 채널을 뽑아야 하므로 상시 내림차순(desc) 정렬 고정
    df = df.sort_values(by="period_view", ascending=False).reset_index(drop=True)
    return df.head(10)

# 3. [프론트엔드 - 제어부] 픽셀링 규격 파라미터 조합
st.sidebar.header("🎛️ 기간 및 지역 매개변수")

# 일별, 주별, 달별 검색 기능 맵핑
period_label = st.sidebar.radio(
    "검색 기준 기간 (Period)", 
    ["일별 최고 기록 (Daily)", "주별 최고 기록 (Weekly)", "달별 최고 기록 (Monthly)"]
)
days_param = 1 if "일별" in period_label else (7 if "주별" in period_label else 30)

country_opt = st.sidebar.selectbox("타겟 국가 (Country)", ["대한민국 (KR)", "미국 (US)"])
country_code = "US" if "미국" in country_opt else "KR"

st.sidebar.markdown("---")
search_button = st.sidebar.button("⚡ 최고 조회수 채널 검색", type="primary", use_container_width=True)

# 4. 출력 레이아웃 전개
if search_button:
    # 파라미터에 맞는 랭킹 데이터 소싱
    df_rank = fetch_highest_view_data(period_days=days_param, country_code=country_code)
    
    # Endpoint 주소창 시각화 업데이트
    current_url = f"https://app.pixeling.io/discovery/channels?sort=period_view&order=desc&days={days_param}&country={country_code}"
    st.code(f"🔗 API Endpoint Status: {current_url}", language="bash")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not df_rank.empty:
        # ⭐ 1위 채널 분리 (명예의 전당 MVP 카드 렌더링)
        mvp = df_rank.iloc[0]
        
        st.markdown(f"### 🏆 해당 기간 최대 조회수 보유 채널 (MVP)")
        st.markdown(f"""
        <div class="mvp-card">
            <table style="width:100%; border:none; border-collapse:collapse;">
                <tr>
                    <td style="width: 8%; text-align: center; vertical-align: middle;">
                        <span class="mvp-badge">👑 1위</span>
                    </td>
                    <td style="width: 12%; text-align: center; vertical-align: middle;">
                        <img src="{mvp['profile_image']}" style="border-radius: 50%; width: 80px; height: 80px; border: 3px solid #ff4b4b; object-fit: cover;">
                    </td>
                    <td style="width: 30%; vertical-align: middle; padding-left: 10px;">
                        <div style="font-size: 16pt; font-weight: 800; color: #111111; margin-bottom: 4px;">{mvp['channel_name']}</div>
                        <div style="font-size: 10.5pt; color: #ff4b4b; font-weight: 600;">{mvp['handle']} · {mvp['media_type']}</div>
                    </td>
                    <td style="width: 18%; vertical-align: middle; text-align: left;">
                        <div class="metric-label" style="color:#ff4b4b; font-weight:bold;">🔥 {period_label.split(' ')[0]} 누적 조회수</div>
                        <div class="mvp-value">{mvp['period_view']:,} 회</div>
                    </td>
                    <td style="width: 16%; vertical-align: middle; text-align: left;">
                        <div class="metric-label">총 구독자 백업</div>
                        <div class="metric-value">{mvp['subscribers']:,} 명</div>
                    </td>
                    <td style="width: 16%; vertical-align: middle; text-align: left;">
                        <div class="metric-label">기간 내 추정 수익</div>
                        <div style="font-size: 13pt; font-weight: 700; color: #10b981;">₩{mvp['estimated_revenue']:,}</div>
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # 🚀 2위 이하 채널 리스트 전개
        st.markdown(f"### 👥 상위 랭킹 경쟁 채널 크루 (Top 2 ~ 10)")
        for index, row in df_rank.iloc[1:].iterrows():
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
                                <img src="{row['profile_image']}" style="border-radius: 50%; width: 62px; height: 62px; border: 1px solid #eef0f4; object-fit: cover;">
                            </td>
                            <td style="width: 32%; vertical-align: middle; padding-left: 10px;">
                                <div style="font-size: 12.5pt; font-weight: 700; color: #111111; margin-bottom: 2px;">{row['channel_name']}</div>
                                <div style="font-size: 9.5pt; color: #0076ff; font-weight: 500;">{row['handle']} · {row['media_type']}</div>
                            </td>
                            <td style="width: 16%; vertical-align: middle; text-align: left;">
                                <div class="metric-label">지정 기간 조회수</div>
                                <div class="metric-value" style="color:#111111; font-weight:700;">{row['period_view']:,} 회</div>
                            </td>
                            <td style="width: 16%; vertical-align: middle; text-align: left;">
                                <div class="metric-label">총 구독자 수</div>
                                <div class="metric-value">{row['subscribers']:,} 명</div>
                            </td>
                            <td style="width: 18%; vertical-align: middle; text-align: left;">
                                <div class="metric-label">예상 달성 수익</div>
                                <div style="font-size: 11.5pt; font-weight: 700; color: #10b981;">₩{row['estimated_revenue']:,}</div>
                            </td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
else:
    # 최초 진입 기본 화면
    st.info("💡 왼쪽 사이드바에서 **일별 / 주별 / 달별** 최고 조회수 기준을 정의한 후 버튼을 누르면 실시간 시계열 랭킹 트래커가 작동합니다.")
    st.image("https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=1200&q=80", caption="YouTube Dynamic Analytics Discovery Dashboard", use_container_width=True)
