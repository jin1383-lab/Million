import streamlit as st
import pandas as pd
import numpy as np

# 1. 페이지 기본 설정
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
st.markdown('<div class="sub-title">GitHub와 Streamlit을 활용한 데이터 필터링 및 랭킹 대시보드 시스템</div>', unsafe_allow_html=True)

# 2. [백엔드 데이터] 안전하고 확실한 다이렉트 이미지 URL 매핑
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
        
        # 100% 렌더링이 보장되는 고정 규격 단독 이미지 URL (표 내부용 1개)
        main_thumb = f"https://picsum.photos/id/{i+10}/120/90.jpg"
        
        # 아래 피드 영역에 뿌려줄 최신 영상 4개의 단독 이미지 배열
        sub_thumbs = [
            f"https://picsum.photos/id/{i+11}/300/200.jpg",
            f"https://picsum.photos/id/{i+12}/300/200.jpg",
            f"https://picsum.photos/id/{i+13}/300/200.jpg",
            f"https://picsum.photos/id/{i+14}/300/200.jpg"
        ]
        
        data.append({
            "순위": 0,
            "대표 썸네일": main_thumb,
            "최신 썸네일 리스트": sub_thumbs,
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

# 3. 사이드바 제어부
st.sidebar.header("🔍 고급 검색 필터 시스템")
media_filter = st.sidebar.radio("미디어 포맷 선택", ["전체 보기", "롱폼 (Long-form)", "숏폼 (Shorts)"])
period_filter = st.sidebar.selectbox("조회수 및 수익 기준 기간", ["1일", "3일", "1주일", "1달"])
sort_target = st.sidebar.radio("정렬 기준 선택", ["조회수 순", "예상 수익 순"])

search_button = st.sidebar.button("🔍 검색시작", type="primary", use_container_width=True)

if search_button:
    if media_filter == "롱폼 (Long-form)":
        df_filtered = df_raw[df_raw["콘텐츠 분류"] == "Long-form"].copy()
    elif media_filter == "숏폼 (Shorts)":
        df_filtered = df_raw[df_raw["콘텐츠 분류"] == "Shorts"].copy()
    else:
        df_filtered = df_raw.copy()

    period_column_map = {"1일": "1일 조회수", "3일": "3일 조회수", "1주일": "1주일 조회수", "1달": "1달 조회수"}
    selected_views_col = period_column_map[period_filter]

    df_filtered["기준 조회수"] = df_filtered[selected_views_col]
    df_filtered["예상 최소수익(원)"] = ((df_filtered["기준 조회수"] / 1000) * df_filtered["적용 RPM(원)"] * 0.85).astype(int)
    df_filtered["예상 최대수익(원)"] = ((df_filtered["기준 조회수"] / 1000) * df_filtered["적용 RPM(원)"] * 1.15).astype(int)

    if sort_target == "조회수 순":
        df_sorted = df_filtered.sort_values(by="기준 조회수", ascending=False)
    else:
        df_sorted = df_filtered.sort_values(by="예상 최대수익(원)", ascending=False)

    df_top20 = df_sorted.head(20).reset_index(drop=True)
    df_top20["순위"] = df_top20.index + 1

    # 4. [출력부] 상단 메인 표 레이아웃 (대표 썸네일 1개 지정)
    st.subheader(f"🏆 {media_filter} - {period_filter} 기준 분석 결과 (Top 20)")

    display_df = pd.DataFrame({
        "순위": df_top20["순위"],
        "썸네일": df_top20["대표 썸네일"],
        "채널명(이동)": df_top20["채널 링크"],
        "표시이름": df_top20["채널명"],
        "미디어 타입": df_top20["콘텐츠 분류"],
        f"조회수 ({period_filter})": df_top20["기준 조회수"].map('{:,}'.format),
        "예상 최소 수익": df_top20["예상 최소수익(원)"].map('₩{:,}'.format),
        "예상 최대 수익": df_top20["예상 최대수익(원)"].map('₩{:,}'.format)
    })

    # 정밀한 ImageColumn 설정을 통해 1번 컬럼의 대표 이미지를 확실하게 그립니다.
    st.dataframe(
        display_df,
        use_container_width=True,
        height=550,
        column_config={
            "순위": st.column_config.NumberColumn(width="small"),
            "썸네일": st.column_config.ImageColumn(label="채널 썸네일"),
            "채널명(이동)": st.column_config.LinkColumn(label="채널명 (클릭 이동)", display_text=r"^https://www.youtube.com/(.*)$"),
            "표시이름": None
        },
        hide_index=True
    )

    # ⭐ 5. [핵심 업그레이드] 표 하단에 최신 영상 4개 썸네일 피드 그리드 전개
    st.markdown("---")
    st.subheader("📸 상위 랭킹 채널별 최근 업로드 영상 피드 (최신순 4개)")
    
    # 1위부터 3위까지 주요 채널의 최신 영상 4개를 시각적으로 크게 나열
    for idx in range(min(3, len(df_top20))):
        channel_info = df_top20.iloc[idx]
        st.markdown(f"#### **Top {idx+1}. {channel_info['채널명']} 채널의 최신 피드**")
        
        # 4개의 컬럼을 가로로 쪼개어 큰 이미지 배치
        img_cols = st.columns(4)
        for img_idx, sub_thumb_url in enumerate(channel_info["최신 썸네일 리스트"]):
            with img_cols[img_idx]:
                st.image(sub_thumb_url, caption=f"최신 영상 {img_idx+1}", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

else:
    st.info("💡 왼쪽 사이드바에서 원하는 검색 조건을 설정한 후 **[🔍 검색시작]** 버튼을 누르면 실시간 분석 랭킹 데이터가 출력됩니다.")
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80", caption="원하는 필터를 선택하고 검색을 시작해 보세요.", use_container_width=True)
