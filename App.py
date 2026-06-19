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
st.markdown('<div class="sub-title">각 채널별 최신 영상 썸네일 멀티 그리드 및 수익 연산 대시보드</div>', unsafe_allow_html=True)

# 2. [백엔드 시뮬레이션] 채널당 4개의 가상 최신 썸네일 리스트를 생성하는 엔진
@st.cache_data
def load_initial_youtube_data():
    np.random.seed(42)
    channel_templates = [
        ("김프로 KIMPRO", "Shorts", "@kimpro"), ("구래 CuRe", "Shorts", "@cure"), ("승비니 seungbini", "Shorts", "@seungbini"),
        ("급상승 예능쇼", "Shorts", "@trending_show"), ("숏폼 마스터", "Shorts", "@short_master"), ("이슈 디렉터", "Shorts", "@issue_director"),
        ("IT 테크 지니어스", "Long-form", "@tech_genius"), ("슈카월드 스타일", "Long-form", "@syuka_style"),
        ("경제 읽어주는 남자", "Long-form", "@economy_man"), ("지식 보관소", "Long-form", "@knowledge_archive"), 
        ("브이로그 다이어리", "Long-form", "@vlog_diary"), ("영화 비하인드 큐브", "Long-form", "@movie_cube")
    ]
    
    data = []
    for i, (name, media_type, handle) in enumerate(channel_templates * 3):
        base_views = np.random.randint(1000000, 15000000) if media_type == "Shorts" else np.random.randint(80000, 1500000)
        
        views_1d = base_views
        views_3d = int(base_views * np.random.uniform(2.5, 3.2))
        views_7d = int(base_views * np.random.uniform(5.5, 7.2))
        views_30d = int(base_views * np.random.uniform(22.0, 29.0))
        
        rpm = np.random.randint(40, 85) if media_type == "Shorts" else np.random.randint(3500, 7500)
        unique_name = f"{name} #{np.random.randint(10,99)}"
        youtube_url = f"https://www.youtube.com/{handle}"
        
        # ⭐ 핵심 변형: 채널당 최신 영상 4개의 썸네일 URL을 리스트(배열) 구조로 백엔드 데이터에 주입
        # 실제 API 환경에서는 각 채널의 최근 업로드 비디오 목록에서 4개의 'thumbnail.url'을 추출해 리스트로 채우게 됩니다.
        thumbnails_list = [
            f"https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=100&h=75&q=80&sig={i}1",
            f"https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?auto=format&fit=crop&w=100&h=75&q=80&sig={i}2",
            f"https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=100&h=75&q=80&sig={i}3",
            f"https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=100&h=75&q=80&sig={i}4"
        ]
        
        data.append({
            "채널 ID": f"CH_{i+1:03d}",
            "최신 썸네일 목록": thumbnails_list,
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

# 3. [프론트엔드 - 제어부] 사이드바 컴포넌트
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

# 4. 버튼 제어 흐름
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

    # 1~20위 슬라이싱
    df_top20 = df_sorted.head(20).reset_index(drop=True)
    df_top20.index = df_top20.index + 1

    # 5. [프론트엔드 - 결과 출력]
    st.subheader(f"🏆 {media_filter} - {period_filter} 기준 트렌드 순위 (Top 20)")

    # 데이터프레임 구조 구성
    display_df = pd.DataFrame({
        "최신 영상 썸네일 (4개)": df_top20["최신 썸네일 목록"], # 리스트 데이터 통째로 맵핑
        "채널명(이동)": df_top20["채널 링크"],
        "표시이름": df_top20["채널명"],
        "미디어 타입": df_top20["콘텐츠 분류"],
        f"선택 기간 조회수 ({period_filter})": df_top20["기준 조회수"].map('{:,}'.format),
        "예상 최소 수익": df_top20["예상 최소수익(원)"].map('₩{:,}'.format),
        "예상 최대 수익": df_top20["예상 최대수익(원)"].map('₩{:,}'.format)
    })

    # ⭐ 정밀 매핑 셋업: ListColumn 안에 ImageColumn 속성을 내포시켜 리스트 내 이미지들이 가로로 정렬 출력되도록 조율합니다.
    st.dataframe(
        display_df,
        use_container_width=True,
        height=820,
        column_config={
            "최신 영상 썸네일 (4개)": st.column_config.ListColumn(
                label="최근 업로드 영상 썸네일 (최신순)",
                help="해당 크리에이터가 채널에 가장 최근에 업로드한 영상 4개의 표지 이미지 배열입니다."
            ),
            "채널명(이동)": st.column_config.LinkColumn(
                label="채널명 (클릭 시 이동)",
                display_text=r"^https://www.youtube.com/(.*)$"
            ),
            "표시이름": None
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
