import streamlit as st
import requests
from datetime import datetime
import random

# ==============================================================================
# UI/UX 전문가 환경 설정: 웹 사이트 기본 탭 이름, 아이콘, 레이아웃 설정
# ==============================================================================
st.set_page_config(
    page_title="오늘의 메뉴 추천",     # 브라우저 탭에 표시될 이름
    page_icon="🍽️",                 # 브라우저 탭 아이콘
    layout="wide",                  # 넓은 레이아웃 사용 (Card UI 배치를 위해)
    initial_sidebar_state="expanded" # 사이드바 기본 펼침
)

# ==============================================================================
# 모바일 홈화면 (PWA) 아이콘 및 이름 커스터마이징 (스트림릿 기본 로고 지우기)
# ==============================================================================
import streamlit.components.v1 as components

components.html("""
<script>
    const doc = window.parent.document;
    
    // 1. 홈 화면에 저장될 때 보여질 앱 이름 (크롬/사파리 모두 적용)
    let metaName = doc.querySelector("meta[name='apple-mobile-web-app-title']");
    if (!metaName) {
        metaName = doc.createElement('meta');
        metaName.name = "apple-mobile-web-app-title";
        doc.head.appendChild(metaName);
    }
    metaName.content = "메뉴추천월드컵"; // 바탕화면에 뜰 이름

    // 2. 홈 화면용 고해상도 앱 아이콘 즉석 제작 (캔버스 활용)
    const canvas = doc.createElement('canvas');
    canvas.width = 192;
    canvas.height = 192;
    const ctx = canvas.getContext('2d');
    
    // 아름다운 앱 아이콘 배경 그라데이션
    const grad = ctx.createLinearGradient(0,0, 192, 192);
    grad.addColorStop(0, '#FF416C'); // 핫핑크
    grad.addColorStop(1, '#FF4B2B'); // 오렌지
    ctx.fillStyle = grad;
    
    // iOS 스타일 둥근 모서리 강제 적용
    ctx.beginPath();
    ctx.moveTo(40, 0); ctx.lineTo(152, 0); ctx.quadraticCurveTo(192, 0, 192, 40);
    ctx.lineTo(192, 152); ctx.quadraticCurveTo(192, 192, 152, 192);
    ctx.lineTo(40, 192); ctx.quadraticCurveTo(0, 192, 0, 152);
    ctx.lineTo(0, 40); ctx.quadraticCurveTo(0, 0, 40, 0);
    ctx.fill();
    
    // 가운데 텍스트(이모티콘) 삽입
    ctx.font = '100px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🍽️', 96, 106);
    
    const iconUrl = canvas.toDataURL('image/png');
    
    // 기존 Streamlit 기본 아이콘 날리기
    doc.querySelectorAll("link[rel*='icon']").forEach(e => e.remove());
    
    // 새로운 커스텀 아이콘 강제 주입
    const appleIcon = doc.createElement('link');
    appleIcon.rel = 'apple-touch-icon';
    appleIcon.href = iconUrl;
    doc.head.appendChild(appleIcon);
</script>
""", height=0)

# ==============================================================================
# 0. 데이터 준비 (Mock Data)
# 실제 서비스에서는 데이터베이스(DB)에서 가져오지만, 여기서는 리스트 형태로 준비합니다.
# 다양한 음식 객체(딕셔너리)를 리스트에 담아둡니다.
# ==============================================================================
import json
import os

# 외부 분리된 거대 데이터베이스(menu_data.json) 로드
json_path = os.path.join(os.path.dirname(__file__), "menu_data.json")
try:
    with open(json_path, "r", encoding="utf-8") as f:
        FOOD_DATA = json.load(f)
except FileNotFoundError:
    FOOD_DATA = []


# ==============================================================================
# CSS 스타일링 (UX/UI 향상을 위한 커스텀 스타일)
# HTML과 CSS를 주입하여 Card UI가 아름답게 보이도록 설정합니다.
# ==============================================================================
st.markdown("""
<style>
    /* ==============================================================================
       Streamlit 기본 UI/워터마크 완벽 제거 (앱을 더 네이티브하게 보이게 함)
    ============================================================================== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 1. 화면 맨 윗부분 텅 빈 여백 완전히 없애기 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* 프로필 및 전체적인 폰트 변경 구역 (옵션) */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* 음식을 보여줄 예쁜 카드 디자인 */
    .food-card {
        border-radius: 15px;                 /* 모서리를 둥글게 */
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); /* 약한 그림자 효과 부여 (입체감) */
        background-color: white;             /* 배경색 흰색 */
        padding: 15px;                       /* 카드 안쪽 여백 */
        margin-bottom: 20px;                 /* 카드 아래 여백 */
        transition: transform 0.2s, box-shadow 0.2s; /* 마우스 오버(hover) 시 애니메이션 시간 속성 */
        height: 100%;                        /* 카드 높이를 균일하게 유지 */
    }
    .food-card:hover {
        transform: translateY(-5px);         /* 마우스를 올리면 위로 살짝 올라가는 효과 */
        box-shadow: 0 8px 20px rgba(0,0,0,0.15); /* 마우스를 올리면 그림자가 더 진해지는 효과 */
    }
    
    /* 카드 내 이미지 디자인 */
    .food-img {
        border-radius: 10px;                 /* 이미지 모서리 둥글게 */
        width: 100%;                         /* 카드 가로폭에 꽉 차게 */
        height: 200px;                       /* 세로 높이는 200px로 고정 */
        object-fit: cover;                   /* 비율이 깨지지 않고 꽉 차게 자르기 */
    }
    
    /* 사진 준비중 임시 박스 디자인 */
    .food-placeholder {
        border-radius: 10px;
        width: 100%;
        height: 200px;
        background-color: #f1f3f5;           /* 밝고 부드러운 회색 배경 */
        color: #adb5bd;                      /* 차분한 회색 텍스트 */
        font-size: 24px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* 카드 내 음식 이름 */
    .food-title {
        font-size: 22px;                     /* 글씨 크기 */
        font-weight: 700;                    /* 굵게 */
        color: #2C3E50;                      /* 텍스트 색상 (짙은 파랑계열 회색) */
        margin: 15px 0 5px 0;                /* 마진(여백): 위 15px, 아래 5px */
    }
    
    /* 카드 내 음식 설명 */
    .food-desc {
        font-size: 14px;                     /* 설명 글씨 크기 */
        color: #7F8C8D;                      /* 텍스트 색상 (연한 회색) */
        margin-bottom: 15px;                 /* 아래 여백 */
        min-height: 40px;                    /* 두 줄 정도의 설명이 들어가도록 최소 높이 지정 */
    }
    
    /* 건강 정보 박스 디자인 */
    .health-info {
        font-size: 12px;                     
        background-color: #F8F9F9;           /* 아주 연한 회색 배경 */
        padding: 10px;                       /* 안쪽 여백 */
        border-radius: 8px;                  /* 모서리 둥글게 */
        border-left: 4px solid #3498DB;      /* 왼쪽에 파란색 테두리 포인트 */
        color: #34495E;                      /* 텍스트 색상 */
    }
    
    /* 상단 상태 표시 알림창 디자인 */
    .status-banner {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53); /* 그라데이션 컬러 (주황~빨강) */
        color: white;                        /* 글자색 흰색 */
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. 자동 감지 기능 함수 (모바일 위치, 날씨 & 시간)
# ==============================================================================
@st.cache_data(ttl=3600)  # 동일 좌표면 캐싱
def get_user_location_and_weather_by_coords(lat, lon):
    """실제 GPS 위도/경도를 바탕으로 동 지명, 날씨 정보를 반환합니다."""
    location = "정확한 위치 📍"
    weather = "날씨 정보 없음 ☁️"
    try:
        # 빅데이터클라우드 무료 Geocoding API (한국어 지원, 제한 없음)
        geo_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=ko"
        geo_res = requests.get(geo_url, timeout=3).json()
        city = geo_res.get('city', '')
        if not city: city = geo_res.get('locality', '알 수 없는 지역')
        country = geo_res.get('countryName', '한국')
        
        if country and city:
            location = f"{country}, {city} 📍"
            
        # Open-Meteo 무료 API
        weather_resp = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true', timeout=3)
        if weather_resp.status_code == 200:
            w_data = weather_resp.json()
            if 'current_weather' in w_data:
                temp = w_data['current_weather']['temperature']
                code = w_data['current_weather']['weathercode']
                
                if code == 0: icon = "☀️"
                elif 1 <= code <= 3: icon = "⛅"
                elif 45 <= code <= 48: icon = "🌫️"
                elif 51 <= code <= 67: icon = "🌧️"
                elif 71 <= code <= 77: icon = "❄️"
                elif 80 <= code <= 99: icon = "⛈️"
                else: icon = "☁️"
                
                weather = f"{temp}℃ {icon}"
    except Exception:
        pass
    return location, weather

def get_current_time_info(tz_name=None):
    """현지 시간(Timezone)을 기반으로 시간대를 판별합니다."""
    now = datetime.now()
    if tz_name:
        try:
            import zoneinfo
            now = datetime.now(zoneinfo.ZoneInfo(tz_name))
        except:
            pass
    current_hour = now.hour
    
    if 5 <= current_hour < 11: return "아침 🌅"
    elif 11 <= current_hour < 16: return "점심 ☀️"
    elif 16 <= current_hour < 21: return "저녁 🌆"
    else: return "야식 🌙"

# ==============================================================================
# 2. 메인 UI 화면 그리기
# ==============================================================================

def get_dynamic_placeholder(food, height="200px"):
    cat = food.get("category", "기타")
    if cat == "한식": bg, emoji = "linear-gradient(135deg, #ff9a44 0%, #fc6076 100%)", "🥘"
    elif cat == "일식": bg, emoji = "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)", "🍣"
    elif cat == "중식": bg, emoji = "linear-gradient(135deg, #ff0844 0%, #ffb199 100%)", "🥟"
    elif cat == "양식": bg, emoji = "linear-gradient(135deg, #f6d365 0%, #fda085 100%)", "🍝"
    else: bg, emoji = "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)", "🌮"
    
    return f'<div style="background: {bg}; border-radius: 10px; height: {height}; display: flex; align-items: center; justify-content: center; font-size: 64px; margin-bottom: 15px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);">{emoji}</div>'

# 타이틀 출력
st.title("🍽️ 맞춤 메뉴 추천")
st.markdown("당신의 상황과 취향을 분석하여 완벽한 식사를 추천해 드릴게요!")

# 상단 상태 알림 배너 (위치, 날씨, 시간)
location, weather = "위치 동의 대기중 📍", "날씨 조회 대기중 ☁️"
time_context = "시간 확인 중 ⏳"

try:
    from streamlit_js_eval import get_geolocation, streamlit_js_eval
    
    # 1. 브라우저 내부 시간대 가져오기 (권한 필요 없음)
    tz_name = streamlit_js_eval(js_expressions='Intl.DateTimeFormat().resolvedOptions().timeZone', key='tz')
    time_context = get_current_time_info(tz_name if tz_name else None)
        
    # 2. 브라우저 GPS 위치 권한 요청 및 날씨/지역 획득
    loc_data = get_geolocation()
    if loc_data and 'coords' in loc_data:
        lat = loc_data['coords']['latitude']
        lon = loc_data['coords']['longitude']
        location, weather = get_user_location_and_weather_by_coords(lat, lon)
    else:
        location = "위치 팝업 창 정보 허용을 눌러주세요 📍"

except ImportError:
    location = "GPS 라이브러리가 없습니다 📍"
    time_context = get_current_time_info()

st.markdown(f"""
<div class="status-banner">
    현재 상태 👉 {location} | 날씨: {weather} | 시간대: {time_context}
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# ==============================================================================
# 3. 메인 탭 구성 (조건별 추천 vs 월드컵)
# ==============================================================================
tab_recommend, tab_worldcup = st.tabs(['💡 조건별 메뉴 추천', '🏆 메뉴 이상형 월드컵 (16강)'])

with tab_recommend:
    # ==============================================================================
    # 기존 3. 사용자 선택 필터
    # ==============================================================================

    # 화면을 3개의 세로 열(Column)로 나눕니다.
    col1, col2, col3 = st.columns(3)

    with col1:
        # 카테고리 선택 타일(버튼형)
        opts = ["전체", "한식", "일식", "중식", "양식", "기타"]
        if getattr(st, "pills", None):
            selected_category = st.pills("국가/문화권", opts, default="전체")
            if not selected_category: selected_category = "전체" # None 방지
        else:
            selected_category = st.radio("국가/문화권", opts, horizontal=True)

    with col2:
        # 맛 타입 선택 타일(버튼형)
        opts = ["전체", "매콤한", "담백한", "달콤한", "기름진"]
        if getattr(st, "pills", None):
            selected_taste = st.pills("맛의 프로필", opts, default="전체")
            if not selected_taste: selected_taste = "전체"
        else:
            selected_taste = st.radio("맛의 프로필", opts, horizontal=True)

    with col3:
        # 온도 선택 타일(버튼형)
        opts = ["전체", "뜨거운", "차가운", "상온"]
        if getattr(st, "pills", None):
            selected_temp = st.pills("음식의 온도", opts, default="전체")
            if not selected_temp: selected_temp = "전체"
        else:
            selected_temp = st.radio("음식의 온도", opts, horizontal=True)

    # ==============================================================================
    # 4. 필터링 로직 및 결과 도출
    # ==============================================================================

    # [메뉴 추천받기 / 다른 메뉴 보기] 기능 처리
    # 버튼을 클릭하면 스트림릿 화면이 리로드(새로고침) 되면서 랜덤 아이템이 다시 뽑히게 됩니다.
    # 빈 공간을 활용하여 버튼을 가운데 정렬 느낌으로 배치
    btn_col1, btn_col2, btn_col3 = st.columns([1,2,1])
    with btn_col2:
        # st.button()은 버튼이 눌리면 True를 반환합니다.
        clicked = st.button("✨ 선별된 스마트 추천 메뉴 보기 ✨", use_container_width=True, type="primary")

    # 조건 필터링 함수
    def filter_foods(category, taste, temp):
        filtered = []
        # 미리 준비된 FOOD_DATA를 하나씩 확인합니다.
        for food in FOOD_DATA:
            # 조건 비교 (전체이거나, 선택한 값과 일치하면 통과)
            match_category = (category == "전체") or (food["category"] == category)
            match_taste = (taste == "전체") or (food["taste"] == taste)
            match_temp = (temp == "전체") or (food["temp"] == temp)

            # 3가지 조건이 모두 True라면 필터링 목록에 담습니다.
            if match_category and match_taste and match_temp:
                filtered.append(food)

        return filtered

    # 화면 하단: 추천 결과 출력 파트
    st.write("---") # 구분선
    # 자동 스크롤을 위한 기준점 앵커(Anchor) 투입
    st.markdown("<div id='recommendation-anchor'></div>", unsafe_allow_html=True)
    st.subheader("💡 추천 메뉴")

    # 조건을 적용하여 음식 목록 걸러내기
    filtered_food_list = filter_foods(selected_category, selected_taste, selected_temp)

    # 걸러낸 목록에서 최대 무작위로 5개를 뽑습니다.
    # 만약 조건에 맞는 음식이 5개가 안 될 수도 있으니, min(5, 음식개수)를 사용합니다.
    if len(filtered_food_list) > 0:
        num_to_select = min(5, len(filtered_food_list))
        # random.sample()을 통해 중복 없이 무작위로 N개를 뽑습니다.
        recommended_foods = random.sample(filtered_food_list, num_to_select)

        # 갯수가 5개 미만인 경우 알림 메시지 (UX 고려)
        if num_to_select < 5:
            st.info("선택하신 조건에 딱 맞는 메뉴가 적어서 있는 결과만 보여드려요! 필터를 '전체'로 넓혀보시는 것은 어떨까요?")

        # 화면을 추천받은 음식 개수에 맞게 N개의 열로 쪼갭니다.
        # 예: 5개면 5분할, 3개면 3분할
        cols = st.columns(num_to_select)

        # 각 열에 Card UI를 렌더링합니다. (zip() 함수로 열 객체와 음식 데이터를 하나씩 매칭합니다)
        for col, food in zip(cols, recommended_foods):
            with col:
                # 아까 생성해둔 CSS 클래스를 사용해 개별 음식 카드를 HTML 문법으로 찍어냅니다.
                card_html = f"""<div class="food-card">
{get_dynamic_placeholder(food, "200px")}

<!-- 제목, 카테고리 태그 -->
<div class="food-title">{food['name']} <span style="font-size:12px; color:#999; font-weight:normal;">({food['category']})</span></div>

<!-- 맛있는 설명 -->
<div class="food-desc">{food['desc']}</div>

<!-- 건장 정보 디자인 박스 -->
<div class="health-info">
🔥 <b>칼로리</b>: {food['calories']} kcal<br>
🍬 <b>당류</b>: {food['sugar']} g<br>
🩸 <b>콜레스테롤</b>: {food['cholesterol']} mg
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        # 필터 조건에 맞는 음식이 하나도 없을 경우 에러 메시지
        st.warning("앗! 선택하신 까다로운 조건에 맞는 메뉴가 아직 데이터에 없습니다. 필터를 조금만 완화해 보세요. 🥲")

    # 하단 '다른 메뉴 보기' 버튼 (버튼 클릭시 앱이 리로드되면서 랜덤 추출이 다시 수행됨)
    st.write("")
    st.write("")
    if st.button("🔄 조건은 그대로, 다른 메뉴 추천받기", use_container_width=False, key="btn_refresh"):
        # 버튼이 눌렸을 때 자바스크립트를 주입해 자연스럽게 메뉴 영역으로 스크롤 업 (모바일 배려)
        st.components.v1.html("""
        <script>
            const target = window.parent.document.getElementById('recommendation-anchor');
            if (target) {
                target.scrollIntoView({behavior: 'smooth', block: 'start'});
            } else {
                window.parent.scrollTo({top: 0, behavior: 'smooth'});
            }
        </script>
        """, height=0)


with tab_worldcup:
    st.subheader("🏆 당신의 궁극의 메뉴를 찾아보세요! (16강)")
    st.write("아래 두 메뉴 중 **오늘 안 끌리는(탈락시킬) 메뉴의 버튼**을 눌러주세요!")
    
    # Session state 초기화
    if 'wc_started' not in st.session_state:
        st.session_state.wc_started = False
        st.session_state.wc_round = 16
        st.session_state.wc_matches = []
        st.session_state.wc_winners = []
        st.session_state.wc_match_idx = 0
    
    # 월드컵 리셋 함수
    def reset_worldcup():
        st.session_state.wc_started = True
        st.session_state.wc_round = 16
        st.session_state.wc_winners = []
        st.session_state.wc_match_idx = 0
        import random
        candidates = random.sample(FOOD_DATA, 16)
        matches = [(candidates[i], candidates[i+1]) for i in range(0, 16, 2)]
        st.session_state.wc_matches = matches

    def eliminate(loser_idx): 
        match = st.session_state.wc_matches[st.session_state.wc_match_idx]
        winner = match[1 if loser_idx == 0 else 0]
        st.session_state.wc_winners.append(winner)
        st.session_state.wc_match_idx += 1
        
        if st.session_state.wc_match_idx >= len(st.session_state.wc_matches):
            if len(st.session_state.wc_winners) == 1:
                st.session_state.wc_round = 1 # 우승
            else:
                st.session_state.wc_round = len(st.session_state.wc_winners)
                new_w = st.session_state.wc_winners
                st.session_state.wc_matches = [(new_w[i], new_w[i+1]) for i in range(0, len(new_w), 2)]
                st.session_state.wc_winners = []
                st.session_state.wc_match_idx = 0

    if not st.session_state.wc_started:
        st.button("🚀 이상형 월드컵 시작하기!", on_click=reset_worldcup, use_container_width=True, type="primary")
    else:
        if st.session_state.wc_round == 1:
            st.balloons()
            st.success("🎉 최종 우승 메뉴가 선정되었습니다!")
            winner_food = st.session_state.wc_winners[0]
            
            st.markdown(f'''
            <div style="text-align: center; margin-bottom: 20px;">
                <h3>👑 최후의 메뉴: {winner_food['name']}</h3>
            </div>
            ''', unsafe_allow_html=True)
            
            card_html = f'''<div class="food-card" style="max-width: 400px; margin: 0 auto;">
{get_dynamic_placeholder(winner_food, "230px")}
<div class="food-title">{winner_food['name']} <span style="font-size:12px; color:#999; font-weight:normal;">({winner_food['category']})</span></div>
<div class="food-desc">{winner_food['desc']}</div>
<div class="health-info">
🔥 <b>칼로리</b>: {winner_food['calories']} kcal<br>
🍬 <b>당류</b>: {winner_food['sugar']} g<br>
🩸 <b>콜레스테롤</b>: {winner_food['cholesterol']} mg
</div>
</div>'''
            st.markdown(card_html, unsafe_allow_html=True)
            st.write("")
            st.button("🔄 월드컵 다시 하기", on_click=reset_worldcup, use_container_width=True)

        else:
            round_name = "결승전" if st.session_state.wc_round == 2 else f"{st.session_state.wc_round}강"
            match_idx = st.session_state.wc_match_idx
            total_matches = len(st.session_state.wc_matches)
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2b5876 0%, #4e4376 100%); color: white; padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin: 0; font-size: 26px; font-weight: 900;">🏆 {round_name}</h2>
                <p style="margin: 5px 0 0 0; font-size: 16px; opacity: 0.9;">현재 <b>{match_idx + 1}</b> / {total_matches} 번째 매치 통과중</p>
            </div>
            """, unsafe_allow_html=True)
            st.progress((match_idx) / total_matches)
            
            match = st.session_state.wc_matches[match_idx]
            food_a, food_b = match[0], match[1]
            
            def render_compact_card(food_item):
                cat = food_item.get("category", "기타")
                if cat == "한식": bg, emoji = "linear-gradient(135deg, #ff9a44 0%, #fc6076 100%)", "🥘"
                elif cat == "일식": bg, emoji = "linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%)", "🍣"
                elif cat == "중식": bg, emoji = "linear-gradient(135deg, #ff0844 0%, #ffb199 100%)", "🥟"
                elif cat == "양식": bg, emoji = "linear-gradient(135deg, #f6d365 0%, #fda085 100%)", "🍝"
                else: bg, emoji = "linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)", "🌮"

                return f"""
                <div style="display: flex; align-items: center; background: #fff; padding: 12px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin-bottom: 5px;">
                    <div style="background: {bg}; border-radius: 10px; min-width: 65px; height: 65px; display: flex; align-items: center; justify-content: center; font-size: 35px; margin-right: 15px; box-shadow: inset 0 0 5px rgba(0,0,0,0.1);">
                        {emoji}
                    </div>
                    <div style="flex-grow: 1; overflow: hidden;">
                        <h4 style="margin: 0; font-size: 18px; color: #2C3E50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{food_item['name']}</h4>
                        <p style="margin: 4px 0 0 0; font-size: 13px; color: #7F8C8D; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{food_item['desc']}</p>
                    </div>
                </div>
                """

            st.markdown(render_compact_card(food_a), unsafe_allow_html=True)
            st.button(f"👆 위에 있는 '{food_a['name']}' ❌ 탈락시키기", key=f"drop_a_{st.session_state.wc_round}_{match_idx}", on_click=eliminate, args=(0,), use_container_width=True)
            
            st.markdown("<div style='text-align:center; font-size:24px; font-weight:900; margin: 15px 0; color:#E74C3C;'>VS</div>", unsafe_allow_html=True)

            st.markdown(render_compact_card(food_b), unsafe_allow_html=True)
            st.button(f"👆 위에 있는 '{food_b['name']}' ❌ 탈락시키기", key=f"drop_b_{st.session_state.wc_round}_{match_idx}", on_click=eliminate, args=(1,), use_container_width=True)

# ==============================================================================
# 앱 하단: 바로가기 설치 안내 버튼
# ==============================================================================
st.write("---")
if st.button("📲 홈 화면에 바로가기 앱으로 설치하기", use_container_width=True):
    st.success("""
    **💡 10초 만에 홈 화면에 설치하는 방법**  
    스토어를 거치지 않고 바로 내 폰 바탕화면에 추가할 수 있습니다!
    
    🍎 **아이폰(Safari):**  
    화면 맨 아래쪽 중앙의 **[공유]**(네모 위 화살표) 버튼을 누르고, 메뉴를 내려서 **[홈 화면에 추가]**를 선택하세요.
    
    🤖 **안드로이드(Chrome):**  
    화면 우측 상단의 **[⋮]**(점 3개) 버튼을 누르고, **[홈 화면에 추가]**를 선택하세요.
    """)
