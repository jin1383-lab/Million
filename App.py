import streamlit as st
import pandas as pd
import requests
import isodate  # 영상 길이(ISO 8601 포맷) 파싱용 라이브러리

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
st.markdown('<div class="sub-title">공식 API 기반 대한민국 인기 급상승 차트 실시간 추적 및 수익 분석 시스템</div>', unsafe_allow_html=True)

# Secrets 프로텍션 및 API Key 로드
try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("⚠️ Streamlit Secrets에 'YOUTUBE_API_KEY'가 설정되지 않았습니다.")
    API_KEY = st.sidebar.text_input("구글 API 키 직접 입력", type="password")

# 2. [백엔드 API 연산부] 인기 급상승 차트 데이터 수집 엔진
def get_kr_trending_videos(max_results=50):
    """대한민국(regionCode=KR) 인기 급상승 차트 영상 메타데이터 실시간 수집"""
    url = (
        f"https://www.googleapis.com/youtube/v3/videos?"
        f"part=id,snippet,contentDetails,statistics&"
        f"chart=mostPopular&"
        f"regionCode=KR&"
        f"maxResults={max_results}&"
        f"key={API_KEY}"
    )
    response = requests.get(url).json()
    
    video_list = []
    if "items" in response:
        for item in response["items"]:
            v_id = item["id"]
            snippet = item["snippet"]
            content_details = item["contentDetails"]
            stats = item.get("statistics", {})
            
            # ISO 8601 재생시간 포맷(예: PT3M15S)을 초 단위로 정밀 파싱
            duration_str = content_details.get("duration", "PT0S")
            try:
                duration_secs = isodate.parse_duration(duration_str).total_seconds()
            except Exception:
                duration_secs = 0
                
            # 60초 이하는 숏츠, 초과는 롱폼으로 정밀 분류
            media_type = "Shorts" if duration_secs <= 60 else "Long-form"
            
            # 고화질 썸네일 안전하게 추출
            thumbnails = snippet.get("thumbnails", {})
            thumbnail_url = thumbnails.get("high", {}).get("url", thumbnails.get("default", {}).get("url", ""))
            
            video_list.append({
                "video_id": v_id,
                "썸네일": thumbnail_url,
                "영상 제목": snippet.get("title", ""),
                "채널명": snippet.get("channelTitle", ""),
                "채널 고유 ID": snippet.get("channelId", ""),
                "미디어 타입": media_type,
                "재생 시간(초)": int(duration_secs),
                "실시간 조회수": int(stats.get("viewCount", 0)),
                "좋아요 수": int(stats.get("likeCount", 0)),
                "댓글 수": int(stats.get("commentCount", 0))
            })
    return video_list

# 3. [프론트엔드 - 제어부] 사이드바 컴포넌트 구성 (텍스트 입력창 제거)
st.sidebar.header("🔍 트렌드 발굴 필터 시스템")
st.sidebar.info("💡 채널명을 치지 않아도 대한민국 유튜브 실시간 인기 차트를 조회수 기반으로 자동 추적합니다.")

media_filter = st.sidebar.radio("미디어 포맷 필터", ["전체 보기", "롱폼 (Long-form)", "숏폼 (Shorts)"])
sort_target = st.sidebar.radio("랭킹 정렬 기준", ["조회수 순", "예상 수익 순", "좋아요 순"])

search_button = st.sidebar.button("🚀 실시간 트렌드 채널 발굴하기", type="primary", use_container_width=True)

# 4. 메인 데이터 처리 파이프라인
if search_button and API_KEY:
    with st.spinner("🔄 유튜브 라이브 서버에서 현재 가장 핫한 인기 채널 데이터를 분석 중입니다..."):
        # 1단계: 한국 인기 급상승 영상 50개 확보
        raw_trends = get_kr_trending_videos(max_results=50)
        
        if not raw_trends:
            st.error("❌ 유튜브 트렌드 데이터를 가져오지 못했습니다. API 할당량이나 키 상태를 확인해 주세요.")
        else:
            df_trends = pd.DataFrame(raw_trends)
            
            # 2단계: 롱폼/숏폼 분류에 따른 정밀 RPM 수익 정산 모델 대입
            # 한국 시장 보정치: 롱폼 평균 4,500원 / 숏폼 평균 55원
            df_trends["예상 최소수익"] = df_trends.apply(
                lambda row: int((row["실시간 조회수"] / 1000) * (55 if row["미디어 타입"] == "Shorts" else 4500) * 0.85), axis=1
            )
            df_trends["예상 최대수익"] = df_trends.apply(
                lambda row: int((row["실시간 조회수"] / 1000) * (55 if row["미디어 타입"] == "Shorts" else 4500) * 1.15), axis=1
            )
            
            # 3단계: 프론트엔드 조건 필터링 작동
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
                
            # 4단계: 상위 20개 행 제한 슬라이싱 및 순위 매기기
            df_top20 = df_trends.head(20).reset_index(drop=True)
            df_top20.index = df_top20.index + 1
            
            # 5단계: 대시보드 렌더링
            st.success(f"✅ 실시간 분석 완료: 현재 가장 조회수가 높은 {len(df_top20)}개의 트렌드 데이터입니다.")
            
            # 가독성 변환 매핑 테이블 생성
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
                    "영상 썸네일": st.column_config.ImageColumn(label="실시간 썸네일"),
                    "채널명": st.column_config.TextColumn(label="크리에이터 채널", width="medium"),
                    "영상 제목(클릭 이동)": st.column_config.LinkColumn(label="링크", display_text=r"🎬 영상 보기"),
                    "실제 제목 텍스트": st.column_config.TextColumn(label="급상승 영상 제목", width="large")
                }
            )
            
            # 6단계: 실시간 원본 썸네일 그리드 피드 (상위 4개 대형 배치)
            st.markdown("---")
            st.subheader("📸 실시간 트렌드 최상위 영상 피드 (고화질)")
            feed_df = df_top20.head(4)
            
            img_cols = st.columns(4)
            for f_idx, (_, row) in enumerate(feed_df.iterrows()):
                with img_cols[f_idx]:
                    st.image(row["썸네일"], use_container_width=True)
                    st.markdown(f"**[{row['채널명']}]**")
                    st.markdown(f"<span style='font-size:10pt; color:#404040;'>{row['영상 제목'][:35]}...</span>", unsafe_allow_html=True)
                    st.caption(f"👀 {row['실시간 조회수']:,}회  |  ❤️ {row['좋아요 수']:,}개")

elif search_button and not API_KEY:
    st.warning("유튜브 Data API 키가 없습니다. 설정 파일이나 사이드바 확인이 필요합니다.")
else:
    # 대기 상태 홈 화면 안내
    st.info("💡 별도의 검색어 입력 없이, 왼쪽 사이드바의 필터를 정하고 **[🚀 실시간 트렌드 채널 발굴하기]** 버튼을 누르면 현재 유튜브 인기 급상승 차트를 분석합니다.")
    st.image("https://images.unsplash.com/photo-1516280440614-37939bbacd6a?auto=format&fit=crop&w=1200&q=80", caption="YouTube Real-time Most Popular Tracker", use_container_width=True)
