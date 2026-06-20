@st.cache_data
def fetch_discovery_data(sort, order, days, country):
    np.random.seed(days + len(sort) + len(country))
    
    # 🇺🇸 국가 파라미터에 따라 채널 풀(Pool)을 완전히 분기 처리
    if country == "US":
        channels = [
            ("MrBeast Style", "Long-form", "@mrbeast_style"),
            ("Zach King Vids", "Shorts", "@zachking_clone"),
            ("Tech Reviewer US", "Long-form", "@us_tech"),
            ("Daily US Shorts", "Shorts", "@daily_us"),
            ("Hollywood Behind", "Long-form", "@hollywood_cube")
        ]
        # 미국 시장은 단가(RPM)를 롱폼 9,000원, 숏폼 110원으로 더 높게 세팅
        rpm_long, rpm_shorts = 9000, 110
    else:
        # 기존 한국(KR) 데이터셋 유지
        channels = [
            ("김프로 KIMPRO", "Shorts", "@kimpro"),
            ("구래 CuRe", "Shorts", "@cure"),
            ("슈카월드 스타일", "Long-form", "@syuka"),
            ("IT섭 ITSUB", "Long-form", "@itsub")
        ]
        rpm_long, rpm_shorts = 4500, 55

    data = []
    for i, (name, m_type, handle) in enumerate(channels * 3):
        base_views = np.random.randint(2000000, 20000000) if m_type == "Shorts" else np.random.randint(300000, 5000000)
        daily_view = int(base_views * days * np.random.uniform(0.8, 1.2))
        subscribers = np.random.randint(1000000, 50000000) if m_type == "Shorts" else np.random.randint(500000, 20000000)
        
        # 지정된 국가별 단가 적용
        rpm = rpm_shorts if m_type == "Shorts" else rpm_long
        revenue = int((daily_view / 1000) * rpm)
        
        profile_img = f"https://picsum.photos/id/{(i+25)%100}/100/100.jpg"
        
        data.append({
            "channel_name": name, "handle": handle, "media_type": m_type,
            "daily_view": daily_view, "subscribers": subscribers,
            "estimated_revenue": revenue, "profile_image": profile_img
        })
        
    df = pd.DataFrame(data)
    ascending_opt = True if order == "asc" else False
    df = df.sort_values(by=sort, ascending=ascending_opt)
    return df.head(15).reset_index(drop=True)
