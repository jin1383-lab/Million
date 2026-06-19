import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 기본 설정 및 스타일 정의
st.set_page_config(
    page_title="유튜브 트렌드 분석 및 예상수익 대시보드",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 26pt; font-weight: bold; color: #1F4E78; margin-bottom: 5px; }
    .sub-title { font-size: 11pt; color: #5A5A5A; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 YouTube Trend & Revenue Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">GitHub와 Streamlit을 활용한 데이터 필터링 및 1일/3일/1주일/1달 랭킹 대시보드 시스템</div>', unsafe_allow_html=True)

# 2. [백엔드 시뮬레이션] 대량의 가상 채널 데이터셋 생성 엔진 (썸네일 주소 추가)
@st.cache_data
def load_initial_youtube_data():
    np.random.seed(42)
    # 가상 채널 정보, 핸들명, 그리고 테스트용 썸네일 이미지 키워드 매핑
    channel_templates = [
        ("김프로 KIMPRO", "Shorts", "@kimpro", "entertainment"), 
        ("구래 CuRe", "Shorts", "@cure", "comedy"), 
        ("승비니 seungbini", "Shorts", "@seungbini", "dance"),
        ("급상승 예능쇼", "Shorts", "@trending_show", "show"), 
        ("숏폼 마스터", "Shorts", "@short_master", "clip"), 
        ("이슈 디렉터", "Shorts", "@issue_director", "news"),
        ("IT 테크 지니어스", "Long-form", "@tech_genius", "tech"), 
        ("슈카월드 스타일", "Long-form", "@syuka_style", "finance"),
        ("경제 읽어주는 남자", "Long-form", "@economy_man", "business"), 
        ("지식 보관소", "Long-form", "@knowledge_archive", "book"), 
        ("브이로그 다이어리", "Long-form", "@vlog_diary", "travel"),
        ("영화 비하인드 큐브", "Long-form", "@movie_cube", "movie"), 
        ("쿠킹 클래스 스튜디오", "Long-form", "@cooking_studio", "food"), 
        ("게임 하이라이트", "Long-form", "@game_highlight", "gaming")
    ]
    
    data = []
    for i, (name, media_type, handle, category) in enumerate(channel_templates * 3):
        base_views = np.random.randint(1000000, 15000000) if media_type == "Shorts" else np.random.randint(80000, 1500000)
        
        views_1d = base_views
        views_3d = int(base_views * np.random.uniform(2.5, 3.2))
        views_7d = int(base_views * np.random.uniform(5.5, 7.2))
        views_30d = int(base_views * np.random.uniform(22.0, 29.0))
        
        rpm = np.random.randint(40, 85) if media_type == "Shorts" else np.random.randint(3500, 7500)
        unique_name = f"{name} #{np.random.randint(10,99)}"
        youtube_url = f"https://www.youtube.com/{handle}"
        
        # 실제 서비스 시 유튜브 API가 제공하는 각 영상/채널의 썸네일 이미지 URL이 들어가는 자리입니다.
        # 여기서는 Unsplash의 카테고리별 데이터 시각화용 가상 썸네일 주소를 매핑합니다.
        thumbnail_url = f"https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=120&h=90&q=80&sig={i}"
        
        data.append({
            "채널 ID": f"CH_{i+1:03d}",
            "썸네일": thumbnail_url,
            "채널명": unique_name,
            "채널 링크": youtube_url,
            "콘텐츠 분류": media_type,
            "1일 조회수": views_1d,
            "3일 조회수": views_3d,
            "1주일 조회수": views_7d,
            "1달 조회수": views_30d,
            "적용 RPM(원)": rpm
        })
    return pd.DataFrame(data)

df_raw = load_initial_youtube_data()

# 3. [프론트엔드 - 대시보드 제어부] 사이드바 컴포넌트 배치
st.sidebar.header("🔍 고급 검색 필터 시스템")

media_filter = st.sidebar.radio(
    "미디어 포맷 선택",
    ["전체 보기", "롱폼 (Long-form)", "숏폼 (Shorts)"]
)

period_filter = st.sidebar.selectbox(
    "조회수 및 수익 기준 기간",
    ["1일", "3일", "1주일", "1달"]
)

sort_target = st.sidebar.radio(
    "정렬 기준 선택",
    ["조회수 순", "예상 수익 순"]
)

search_button = st.sidebar.button("🔍 검색시작", type="primary", use_container_width=True)

# 4. 버튼 제어 흐름 처리
if search_button:
    if media_filter == "롱폼 (Long-form)":
        df_filtered = df_raw[df_raw["콘텐츠 분류"] == "Long-form"].copy()
    elif media_filter == "숏폼 (Shorts)":
        df_filtered = df_raw[df_raw["콘텐츠 분류"] == "Shorts"].copy()
    else:
        df_filtered = df_raw.copy()

    period_column_map = {
        "1일": "1일 조회수",
        "3일": "3일 조회수",
        "1주일": "1주일 조회수",
        "1달": "1달 조회수"
    }
    selected_views_col = period_column_map[period_filter]

    # 수익 연산
    df_filtered["기준 조회수"] = df_filtered[selected_views_col]
    df_filtered["예상 최소수익(원)"] = ((df_filtered["기준 조회수"] / 1000) * df_filtered["적용 RPM(원)"] * 0.85).astype(int)
    df_filtered["예상 최대수익(원)"] = ((df_filtered["기준 조회수"] / 1000) * df_filtered["적용 RPM(원)"] * 1.15).astype(int)

    # 정렬 처리
    if sort_target == "조회수 순":
        df_sorted = df_filtered.sort_values(by="기준 조회수", ascending=False)
    else:
        df_sorted = df_filtered.sort_values(by="예상 최대수익(원)", ascending=False)

    # 1~20위
