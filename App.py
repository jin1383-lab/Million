import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 기본 설정 및 스타일 정의
st.set_page_config(
    page_title="유튜브 트렌드 분석 및 예상수익 대시보드",
    page_icon="📊",
    layout="wide"
)

# 디자인 패딩 및 스타일 입히기
st.markdown("""
    <style>
    .main-title { font-size: 26pt; font-weight: bold; color: #1F4E78; margin-bottom: 5px; }
    .sub-title { font-size: 11pt; color: #5A5A5A; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 YouTube Trend & Revenue Finder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">GitHub와 Streamlit을 활용한 데이터 필터링 및 1일/3일/1주일/1달 랭킹 대시보드 시스템</div>', unsafe_allow_html=True)

# 2. [백엔드 시뮬레이션] 대량의 가상 채널 데이터셋 생성 엔진
@st.cache_data
def load_initial_youtube_data():
    np.random.seed(42)
    # 가상 채널 정보와 함께 이동할 가상 유튜브 핸들명(URL용) 추가
    channel_templates = [
        ("김프로 KIMPRO", "Shorts", "@kimpro"), ("구래 CuRe", "Shorts", "@cure"), ("승비니 seungbini", "Shorts", "@seungbini"),
        ("급상승 예능쇼", "Shorts", "@trending_show"), ("숏폼 마스터", "Shorts", "@short_master"), ("이슈 디렉터", "Shorts", "@issue_director"),
        ("애니메이션 밈", "Shorts", "@anim_meme"), ("글로벌 댄스 챌린지", "Shorts", "@dance_challenge"), ("도전 먹방", "Shorts", "@mukbang_challenge"),
        ("인기 급상승 클립", "Shorts", "@hot_clip"), ("IT 테크 지니어스", "Long-form", "@tech_genius"), ("슈카월드 스타일", "Long-form", "@syuka_style"),
        ("경제 읽어주는 남자", "Long-form", "@economy_man"), ("지식 보관소", "Long-form", "@knowledge_archive"), ("브이로그 다이어리", "Long-form", "@vlog_diary"),
        ("영화 비하인드 큐브", "Long-form", "@movie_cube"), ("쿠킹 클래스 스튜디오", "Long-form", "@cooking_studio"), ("게임 하이라이트", "Long-form", "@game_highlight"),
        ("음악 스트리밍 라운지", "Long-form", "@music_lounge"), ("피트니스 가이드", "Long-form", "@fitness_guide"), ("여행의 모든 것", "Long-form", "@travel_all"),
        ("역사 비하인드", "Long-form", "@history_behind"), ("동물 일기", "Long-form", "@animal_diary"), ("시사 뉴스 브리핑", "Long-form", "@news_briefing")
    ]
    
    data = []
    for i, (name, media_type, handle) in enumerate(channel_templates * 2):
        base_views = np.random.randint(1000000, 15000000) if media_type == "Shorts" else np.random.randint(80000, 1500000)
        
        views_1d = base_views
        views_3d = int(base_views * np.random.uniform(2.5, 3.2))
        views_7d = int(base_views * np.random.uniform(5.5, 7.2))
        views_30d = int(base_views * np.random.uniform(22.0, 29.0))
        
        rpm = np.random.randint(40, 85) if media_type == "Shorts" else np.random.randint(3500, 7500)
        
        # 난수를 섞어 고유한 채널명과 실제 연결될 수 있는 유튜브 기본 주소(또는 가상 주소) 매핑
        unique_name = f"{name} #{np.random.randint(10,99)}"
        # 테스트용 실제 연결 주소 (실제 서비스 시에는 API에서 받아온 채널 고유 URL 대입)
        youtube_url = f"https://www.youtube.com/{handle}"
        
        data.append({
            "채널 ID": f"CH_{i+1:03d}",
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
    # 데이터 필터링 분기
    if media_filter == "롱폼 (Long-form)":
        df_filtered = df_raw[df_raw["콘텐츠 분류"] == "Long-form"].copy()
    elif media_filter == "숏폼 (Shorts)":
        df_filtered = df_raw[df_raw["콘텐츠 분류"] == "Shorts"].copy()
    else:
        df_filtered = df_raw.copy()

    # 기간 매핑
    period_column_map = {
        "1일": "1일 조회수",
        "3일": "3일 조회수",
        "1주일": "1주일 조회수",
        "1달": "1달 조회수"
    }
    selected_views_col = period_column_map[period_filter]

    # 수익 연산 파이프라인
    df_filtered["기준 조회수"] = df_filtered[selected_views_col]
    df_filtered["예상 최소수익(원)"] = ((df_filtered["기준 조회수"] / 1000) * df_filtered["적용 RPM(원)"] * 0.85).astype(int)
    df_filtered["예상 최대수익(원)"] = ((df_filtered["기준 조회수"] / 1000) * df_filtered["적용 RPM(원)"] * 1.15).astype(int)

    # 정렬 처리
    if sort_target == "조회수 순":
        df_sorted = df_filtered.sort_values(by="기준 조회수", ascending=False)
    else:
        df_sorted = df_filtered.sort_values(by="예상 최대수익(원)", ascending=False)

    # 1~20위 출력 제한 슬라이싱
    df_top20 = df_sorted.head(20).reset_index(drop=True)
    df_top20.index = df_top20.index + 1

    # 5. [프론트엔드 - 결과 출력]
    st.subheader(f"🏆 {media_filter} - {period_filter} 기준 트렌드 순위 (Top 20)")

    # 핵심 수정: 데이터프레임에 하이퍼링크로 작동할 주소 컬럼을 그대로 유지합니다.
    display_df = pd.DataFrame({
        "채널명(이동)": df_top20["채널 링크"],  # 실제 링크 주소가 들어가지만 화면에는 예쁘게 라벨링됩니다.
        "표시이름": df_top20["채널명"],        # 링크에 덮어씌울 텍스트 명칭
        "미디어 타입": df_top20["콘텐츠 분류"],
        f"선택 기간 조회수 ({period_filter})": df_top20["기준 조회수"].map('{:,}'.format),
        "예상 최소 수익": df_top20["예상 최소수익(원)"].map('₩{:,}'.format),
        "예상 최대 수익": df_top20["예상 최대수익(원)"].map('₩{:,}'.format),
        "추정 평균 RPM": df_top20["적용 RPM(원)"].map('₩{:,}'.format)
    })

    # ⭐ 핵심 설정을 통해 첫 번째 컬럼을 클릭 가능한 링크 컬럼(LinkColumn)으로 변경합니다.
    st.dataframe(
        display_df,
        use_container_width=True,
        height=735,
        column_config={
            "채널명(이동)": st.column_config.LinkColumn(
                label="채널명 (클릭 시 이동)",
                display_text=r"^https://www.youtube.com/(.*)$" # URL 대신 뒷부분 핸들명이나 지정한 명칭이 표에 깔끔하게 노출되도록 정규식 매핑
            ),
            "표시이름": None # 링크의 뼈대가 되었으므로 화면에서 숨김 처리
        }
    )

    # 요약 지표 카드
    st.markdown("---")
    st.markdown("### 📈 현재 화면 요약 통계 지표")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label=f"20위 내 최고 조회수 ({period_filter})", value=f"{df_top20['기준 조회수'].max():,} 회")
    with col2:
        st.metric(label="최고 예상 일일 수익 채널", value=f"₩{df_top20['예상 최대수익(원)'].max():,}")
    with col3:
        st.metric(label="분석된 활성 채널 풀 개수", value=f"{len(df_filtered)}개 채널")

else:
    st.info("💡 왼쪽 사이드바에서 원하는 검색 조건을 설정한 후 **[🔍 검색시작]** 버튼을 누르면 실시간 분석 랭킹 데이터가 출력됩니다.")
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80", caption="원하는 필터를 선택하고 검색을 시작해 보세요.", use_container_width=True)
