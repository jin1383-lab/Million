# 🚀 글로벌 CSS 오버라이드 (완벽한 All Dark Mode 에코시스템 구축)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* 1. 메인 스트림릿 가상 배경 전체를 다크하게 강제 오버라이드 */
    .stApp { background-color: #0B0F19 !important; color: #E5E7EB; }
    header { background-color: rgba(11, 15, 25, 0.8) !important; }
    
    /* 헤더 타이틀 영역 */
    .brand-container { padding: 10px 0px 20px 0px; }
    .brand-title { font-size: 28pt; font-weight: 800; letter-spacing: -1px; background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .brand-subtitle { font-size: 11pt; color: #9CA3AF; font-weight: 400; margin-top: 4px; }
    
    /* 🔗 Dark Endpoint 상태 바 */
    .url-wrapper { background-color: #161D30; border-radius: 12px; padding: 14px 20px; border: 1px solid #24314D; margin-bottom: 30px; font-family: monospace; color: #34D399; font-size: 10pt; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
    
    /* 🔥 1위 MVP 프리미엄 블랙 홀 카드 */
    .mvp-hero-card {
        background: radial-gradient(circle at top right, rgba(79, 172, 254, 0.1), #131B2E);
        border-radius: 20px;
        padding: 30px;
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
        margin-bottom: 25px;
        border: 1px solid #24314D;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* 👥 하단 랭킹 그리드용 다크 카드 */
    .grid-card {
        background: #131B2E;
        border-radius: 16px;
        border: 1px solid #212B41;
        padding: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .grid-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
        border-color: #3B82F6;
    }
    
    /* 🏷️ 다크 전용 네온 배지 세트 */
    .badge-mvp { background: linear-gradient(135deg, #FF1E27 0%, #FE5858 100%); color: white; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 8.5pt; }
    .badge-rank { background: #1F2937; color: #F3F4F6; padding: 4px 10px; border-radius: 8px; font-weight: 700; font-size: 8.5pt; border: 1px solid #374151; }
    .tag-format-shorts { background: rgba(239, 68, 68, 0.15); color: #F87171; padding: 2px 8px; border-radius: 6px; font-size: 8pt; font-weight: 600; border: 1px solid rgba(239, 68, 68, 0.3); }
    .tag-format-long { background: rgba(59, 130, 246, 0.15); color: #60A5FA; padding: 2px 8px; border-radius: 6px; font-size: 8pt; font-weight: 600; border: 1px solid rgba(59, 130, 246, 0.3); }
    
    /* 📈 다크 전용 지표 박스 */
    .card-title { font-size: 13pt; font-weight: 700; color: #F3F4F6; margin: 10px 0px 2px 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .card-handle { font-size: 9.5pt; color: #9CA3AF; margin-bottom: 15px; }
    .metric-box { background: #1A2338; border-radius: 10px; padding: 12px; margin-top: 8px; border: 1px solid #24314D; }
    
    .lbl { font-size: 8.5pt; color: #9CA3AF; font-weight: 500; margin-bottom: 2px; }
    .val { font-size: 13pt; font-weight: 700; color: #FFFFFF; }
    .val-revenue { font-size: 13pt; font-weight: 700; color: #34D399; }
    </style>
""", unsafe_allow_html=True)  # 👈 바로 이 닫는 부분이 누락되었는지 체크해 주세요!
