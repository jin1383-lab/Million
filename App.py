import streamlit as st
import pandas as pd
import requests
import isodate
import datetime

# 1. 글로벌 페이지 인프라 및 다크 테마 빌드
st.set_page_config(
    page_title="Pixeling Pro - Dark Matrix",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🚀 글로벌 CSS 오버라이드 (완벽한 All Dark Mode 에코시스템 구축)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* 메인 스트림릿 가상 배경 전체를 다크하게 강제 오버라이드 */
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
