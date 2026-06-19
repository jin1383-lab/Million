import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="유튜브 실시간 트렌드 디스커버리 대시보드",
    page_icon="🔥",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title { font-size: 26pt; font-weight: bold; color: #C00000; margin-bottom: 5px; }
    .sub-title { font-size: 11pt; color: #5A5A5A; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔥 YouTube Trend Discovery Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">시계열 데이터 스냅샷 엔진 기반 일자별/기간별 조회수 트렌드 분석 시스템</div>', unsafe_allow_html=True)

# 2. [시계열 백엔드 엔진] 사용자가 선택한 날짜에 맞춰 과거 스냅샷 데이터를 시뮬레이션 생성
@st.cache_data
def load_snapshot_data_by_date(selected_date):
    """
    선택한 날짜(seed 역할)에 따라 조회수와 랭킹이 완전히 다르게 변하는 
    시계열 데이터베이스 가상 시뮬레이터입니다.
    """
    # 날짜를 숫자로 변환하여 랜덤 시드로 활용 (날짜가 바뀌면 순위와 데이터가 완전히 바뀜)
    date_seed = int(selected_date.strftime("%Y%m%d"))
    np.random.seed(date_seed)
    
    channel_templates = [
        ("김프로 KIMPRO", "Shorts"), ("구래 CuRe", "Shorts"), ("승비니 seungbini", "Shorts"),
        ("급상승 예능쇼", "Shorts"), ("숏폼 마스터", "Shorts"), ("이슈 디렉터", "Shorts"),
        ("IT 테크 지니어스", "Long-form"), ("슈카월드 스타일", "Long-form"),
        ("경제 읽어주는 남자", "Long-form"), ("지식 보관소", "Long-form"), 
        ("브이로그 다이어리", "Long-form"), ("영화 비하인드 큐브", "Long-form"),
        ("요리 연구소", "Long-form"), ("게임 하이라이트", "Long-form"), ("뷰티 가이드", "Shorts")
    ]
    
    data = []
    for i, (name, media_type) in enumerate(channel_templates * 3):
        # 날짜별로 조회수가 다이나믹하게 변동하도록 설정
        base_views = np.random.randint(500000, 20000000) if media_type == "Shorts" else np.random.randint(50000, 3000000)
        likes = int(base_views * np.random.uniform(0.02, 0.07))
        
        # 실제 서비스 시 대입될 유튜브 고유 비디오 ID 및 썸네일 가상 매핑
        video_id = f"vid_{date_seed}_{i}"
        thumbnail_url = f"https://picsum.photos/id/{(i+date_seed)%100}/120/90.jpg"
        
        data.append({
            "video_id": video_id,
            "썸네일": thumbnail_url,
            "영상 제목": f"[{selected_date.strftime('%m/%d')} 핫트렌드] {name}의 급상승 인기 클립 #{np.random.randint(1,100)}",
            "채널명": name,
            "미디어 타입": media_type,
            "실시간 조회수": base_views,
            "좋아요 수": likes
        })
    return pd.DataFrame(data)

# 3. [프론트엔드 - 제어부] 사이드바 컴포넌트 구성 (날짜 기능 추가)
st.sidebar.header("🔍 트렌드 발굴 필터 시스템")

# ⭐ 핵심 기능: Streamlit 달력 위젯 추가
st.sidebar.subheader("📅 분석 기준 날짜 선택")
selected_date = st.sidebar.date_input(
    "조회하고자 하는 날짜를 지정하세요",
    value=datetime.date(2026, 6, 20),                     # 기본값 (현재 설정 시간 기준)
    min_value=datetime.date(2026, 1, 1),                  # 데이터 조회 최소 제한일
    max_value=datetime.date(2026, 12, 31)                 # 데이터 조회 최대 제한일
)

st.sidebar.markdown("---")
media_filter = st.sidebar.radio("미디어 포맷 필터", ["전체 보기", "롱폼 (Long-form)", "숏폼 (Shorts)"])
sort_target = st.sidebar.radio("랭킹 정렬 기준", ["조회수 순", "예상 수익 순", "좋아요 순"])

search_button = st.sidebar.button("🚀 지정 일자 트렌드 발굴하기", type="primary", use_container_width=True)

# 4. 메인 데이터 처리 파이프라인
if search_button:
    with st.spinner(f"🔄 시계열 DB에서 {selected_date.strftime('%Y년 %m월 %d일')} 자정 기준 스냅샷을 로드하는 중..."):
        
        # 1단계: 사용자가 지정한 날짜의 데이터 로드
        df_trends = load_snapshot_data_by_date(selected_date)
        
        # 2단계: 롱폼/숏폼 수익 정산 모델 대입
        df_trends["예상 최소수익"] = df_trends.apply(
            lambda row: int((row["실시간 조회수"] / 1000) * (55 if row["미디어 타입"] == "Shorts" else 4500) * 0.85), axis=1
        )
        df_trends["예상 최대수익"] = df_trends.apply(
            lambda row: int((row["실시간 조회수"] / 1000) * (55 if row["미디어 타입"] == "Shorts" else 4500) * 1.15), axis=1
        )
        
        # 3단계: 조건 필터링 작동
        if media_filter == "롱폼 (Long-form)":
            df_trends = df_trends[df_trends["미디어 타입"] == "Long-form"]
        elif media_filter == "숏폼 (Shorts)":
            df_trends = df_trends[df_trends["미디어 타입"] == "Shorts"]
            
        # 정렬 제어
        if sort_target == "조회수 순":
            df_trends = df_trends.sort_values(by="실시간 조회수", ascending=False)
        elif sort_target == "좋아요 순":
            df_trends = df_trends.sort_values(by="좋아요 수", ascending=False)
        else:
            df_trends = df_trends.sort_values(by="예상 최대수익", ascending=False)
            
        # 4단계: 상위 20개 행 제한 및 순위 매기기
        df_top20 = df_trends.head(20).reset_index(drop=True)
        df_top20.index = df_top20.index + 1
        
        # 5단계: 대시보드 결과 출력
        st.success(f"📊 {selected_date.strftime('%Y-%m-%d')} 기준 대한민국 인기 트렌드 분석 완료")
        
        # 가독성 표 데이터 가공
        display_df = pd.DataFrame({
            "영상 썸네일": df_top20["썸네일"],
            "채널명": df_top20["채널명"],
            "영상 제목(클릭 이동)": "https://www.youtube.com/watch?v=" + df_top20["video_id"],
            "실제 제목 텍스트": df_top20["영상 제목"],
            "포맷": df_top20["미디어 타입"],
            "조회수": df_top20["실시간 조회수"].map("{:,}회".format),
            "좋아요": df_top20["좋아요 수"].map("{:,}개".format),
            "예상 최소 수익": df_top20["예상 최소수익"].map("₩{:,}".format),
            "예상 최대 수익": df_top20["예상 최대수익"].map("₩{:,}".format)
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=720,
            column_config={
                "영상 썸네일": st.column_config.ImageColumn(label="스냅샷 썸네일"),
                "채널명": st.column_config.TextColumn(label="크리에이터 채널", width="medium"),
                "영상 제목(클릭 이동)": st.column_config.LinkColumn(label="링크", display_text=r"🎬 영상 보기"),
                "실제 제목 텍스트": st.column_config.TextColumn(label="당일 급상승 영상 제목", width="large")
            }
        )
        
        # 6단계: 실시간 원본 썸네일 그리드 피드 (선택 일자 상위 4개 대형 배치)
        st.markdown("---")
        st.subheader(f"📸 {selected_date.strftime('%m월 %d일')} 트렌드 최상위 영상 피드")
        feed_df = df_top20.head(4)
        
        img_cols = st.columns(4)
        for f_idx, (_, row) in enumerate(feed_df.iterrows()):
            with img_cols[f_idx]:
                st.image(row["썸네일"], use_container_width=True)
                st.markdown(f"**[{row['채널명']}]**")
                st.markdown(f"<span style='font-size:10pt; color:#404040;'>{row['영상 제목']}</span>", unsafe_allow_html=True)
                st.caption(f"👀 {row['실시간 조회수']:,}회  |  ❤️ {row['좋아요 수']:,}개")

else:
    # 대기 상태 홈 화면 안내
    st.info("💡 왼쪽 사이드바에서 **[원하는 분석 날짜]** 및 필터를 지정하고 **[🚀 지정 일자 트렌드 발굴하기]** 버튼을 누르면 해당 날짜의 시계열 트렌드 기록을 추적합니다.")
    st.image("https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format&fit=crop&w=1200&q=80", caption="Time-series Snapshot Trend Tracker", use_container_width=True)
