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
# 0. 데이터 준비 (Mock Data)
# 실제 서비스에서는 데이터베이스(DB)에서 가져오지만, 여기서는 리스트 형태로 준비합니다.
# 다양한 음식 객체(딕셔너리)를 리스트에 담아둡니다.
# ==============================================================================
FOOD_DATA = [
    # 한식 (30개)
    {"name": "김치찌개", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 450, "sugar": 8, "cholesterol": 15, "desc": "얼큰하고 진한 국물이 일품인 한국인의 소울푸드", "img_url": "https://images.unsplash.com/photo-1590301157890-4810ed352733?q=80&w=600"},
    {"name": "비빔냉면", "category": "한식", "taste": "매콤한", "temp": "차가운", "calories": 550, "sugar": 30, "cholesterol": 5, "desc": "매콤새콤한 양념장에 쫄깃하게 비벼낸 시원한 면발", "img_url": "https://images.unsplash.com/photo-1582228558552-32a7ec71fb7b?q=80&w=600"},
    {"name": "설렁탕", "category": "한식", "taste": "담백한", "temp": "뜨거운", "calories": 400, "sugar": 0, "cholesterol": 30, "desc": "뽀얗게 우러난 깊은 맛의 사골국물에 파 송송", "img_url": "https://images.unsplash.com/photo-1605287661555-520593f6630b?q=80&w=600"},
    {"name": "치즈 떡볶이", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 550, "sugar": 35, "cholesterol": 10, "desc": "매콤달콤 소스에 쫀득한 떡과 고소한 치즈가 듬뿍", "img_url": "https://images.unsplash.com/photo-1649911910243-7f21b7ebd2df?q=80&w=600"},
    {"name": "소갈비찜", "category": "한식", "taste": "달콤한", "temp": "뜨거운", "calories": 800, "sugar": 25, "cholesterol": 70, "desc": "달짝지근한 간장 양념에 푹 쪄낸 부드러운 갈비", "img_url": "https://images.unsplash.com/photo-1600289031464-74d374b64991?q=80&w=600"},
    {"name": "삼겹살 구이", "category": "한식", "taste": "기름진", "temp": "뜨거운", "calories": 1000, "sugar": 2, "cholesterol": 80, "desc": "지글지글 불판에 구워먹는 고소한 한국인의 고기 반찬", "img_url": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?q=80&w=600"},
    {"name": "궁중 떡볶이", "category": "한식", "taste": "달콤한", "temp": "뜨거운", "calories": 500, "sugar": 20, "cholesterol": 10, "desc": "간장 베이스로 볶아내어 맵지 않고 달콤한 옛날식 떡볶이", "img_url": "https://images.unsplash.com/photo-1628172421295-89db3a13f619?q=80&w=600"},
    {"name": "콩국수", "category": "한식", "taste": "담백한", "temp": "차가운", "calories": 450, "sugar": 5, "cholesterol": 0, "desc": "진하고 고소한 콩물에 쫄깃한 소면을 말아먹는 별미", "img_url": "https://images.unsplash.com/photo-1618366436440-87a46ab8ef29?q=80&w=600"},
    {"name": "육회 비빔밥", "category": "한식", "taste": "담백한", "temp": "상온", "calories": 500, "sugar": 10, "cholesterol": 30, "desc": "신선한 육회와 다양한 나물이 어우러진 건강한 한 끼", "img_url": "https://images.unsplash.com/photo-1548684610-85f8c65076a0?q=80&w=600"},
    {"name": "제육볶음", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 600, "sugar": 15, "cholesterol": 40, "desc": "불맛 가득하게 매콤달콤 볶아낸 돼지고기", "img_url": "https://loremflickr.com/400/300/spicy?random=1"},
    {"name": "순댓국", "category": "한식", "taste": "담백한", "temp": "뜨거운", "calories": 550, "sugar": 2, "cholesterol": 60, "desc": "따뜻하고 든든하게 속을 채워주는 뽀얀 국밥", "img_url": "https://loremflickr.com/400/300/soup?random=1"},
    {"name": "뼈해장국", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 700, "sugar": 5, "cholesterol": 45, "desc": "푹 고아낸 돼지 등뼈와 우거지의 깊은 맛", "img_url": "https://loremflickr.com/400/300/soup?random=2"},
    {"name": "부대찌개", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 800, "sugar": 10, "cholesterol": 50, "desc": "햄과 소시지, 라면 사리가 듬뿍 들어간 찌개", "img_url": "https://loremflickr.com/400/300/stew?random=1"},
    {"name": "된장찌개", "category": "한식", "taste": "담백한", "temp": "뜨거운", "calories": 300, "sugar": 3, "cholesterol": 0, "desc": "구수한 된장과 두부, 호박이 어우러진 구수한 맛", "img_url": "https://loremflickr.com/400/300/stew?random=2"},
    {"name": "물냉면", "category": "한식", "taste": "담백한", "temp": "차가운", "calories": 400, "sugar": 15, "cholesterol": 5, "desc": "가슴속까지 시원해지는 살얼음 동동 냉면", "img_url": "https://loremflickr.com/400/300/noodle?random=1"},
    {"name": "칼국수", "category": "한식", "taste": "담백한", "temp": "뜨거운", "calories": 500, "sugar": 5, "cholesterol": 10, "desc": "진한 바지락 육수와 쫄깃한 수타면", "img_url": "https://loremflickr.com/400/300/noodle?random=2"},
    {"name": "잔치국수", "category": "한식", "taste": "담백한", "temp": "뜨거운", "calories": 350, "sugar": 5, "cholesterol": 5, "desc": "깔끔한 멸치 육수에 고명이 예쁘게 올라간 국수", "img_url": "https://loremflickr.com/400/300/noodle?random=3"},
    {"name": "오징어 볶음", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 450, "sugar": 12, "cholesterol": 150, "desc": "매콤한 양념에 쫄깃하게 볶아낸 밥도둑", "img_url": "https://loremflickr.com/400/300/spicy?random=2"},
    {"name": "갈치조림", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 400, "sugar": 10, "cholesterol": 60, "desc": "부드러운 갈치살과 매콤하게 졸여진 밥도둑 무", "img_url": "https://loremflickr.com/400/300/fish?random=1"},
    {"name": "고등어 구이", "category": "한식", "taste": "기름진", "temp": "뜨거운", "calories": 450, "sugar": 0, "cholesterol": 70, "desc": "겉은 바삭 속은 촉촉하게 구운 국민 생선", "img_url": "https://loremflickr.com/400/300/fish?random=2"},
    {"name": "삼계탕", "category": "한식", "taste": "담백한", "temp": "뜨거운", "calories": 900, "sugar": 2, "cholesterol": 80, "desc": "인삼과 대추를 넣고 푹 곤 든든한 보양식", "img_url": "https://loremflickr.com/400/300/chicken?random=1"},
    {"name": "간장 찜닭", "category": "한식", "taste": "달콤한", "temp": "뜨거운", "calories": 750, "sugar": 25, "cholesterol": 65, "desc": "단짠단짠의 정석 간장 소스와 쫀득한 당면", "img_url": "https://loremflickr.com/400/300/chicken?random=2"},
    {"name": "감자탕", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 800, "sugar": 8, "cholesterol": 55, "desc": "포슬포슬한 감자와 고기가 어우러진 얼큰한 진국", "img_url": "https://loremflickr.com/400/300/stew?random=4"},
    {"name": "소곱창 구이", "category": "한식", "taste": "기름진", "temp": "뜨거운", "calories": 950, "sugar": 2, "cholesterol": 120, "desc": "고소한 곱이 입안 가득 퍼지는 소곱창 구이", "img_url": "https://loremflickr.com/400/300/meat?random=1"},
    {"name": "참치 김밥", "category": "한식", "taste": "담백한", "temp": "상온", "calories": 450, "sugar": 8, "cholesterol": 15, "desc": "마요네즈에 버무린 고소한 참치가 가득 들어간 김밥", "img_url": "https://loremflickr.com/400/300/kimbap?random=1"},
    {"name": "돈까스 김밥", "category": "한식", "taste": "기름진", "temp": "상온", "calories": 550, "sugar": 10, "cholesterol": 20, "desc": "바삭한 돈까스가 통으로 들어가 든든한 한 줄", "img_url": "https://loremflickr.com/400/300/kimbap?random=2"},
    {"name": "해물 파전", "category": "한식", "taste": "기름진", "temp": "뜨거운", "calories": 400, "sugar": 5, "cholesterol": 30, "desc": "비 오는 날 생각나는 바삭하고 고소한 파전", "img_url": "https://loremflickr.com/400/300/pancake?random=1"},
    {"name": "김치전", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 380, "sugar": 8, "cholesterol": 10, "desc": "잘 익은 신김치로 바삭하게 부쳐낸 간식", "img_url": "https://loremflickr.com/400/300/pancake?random=2"},
    {"name": "족발", "category": "한식", "taste": "기름진", "temp": "상온", "calories": 750, "sugar": 15, "cholesterol": 90, "desc": "야들야들하고 쫀득한 콜라겐 덩어리 족발", "img_url": "https://loremflickr.com/400/300/meat?random=2"},
    {"name": "돌솥 비빔밥", "category": "한식", "taste": "매콤한", "temp": "뜨거운", "calories": 480, "sugar": 12, "cholesterol": 5, "desc": "타닥타닥 소리가 일품인 따뜻하고 바삭한 비빔밥", "img_url": "https://loremflickr.com/400/300/bibimbap?random=1"},

    # 일식 (20개)
    {"name": "초밥 10피스", "category": "일식", "taste": "담백한", "temp": "차가운", "calories": 350, "sugar": 5, "cholesterol": 10, "desc": "신선한 해산물과 식초 밥의 완벽한 조화", "img_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?q=80&w=600"},
    {"name": "매운 돈코츠 라멘", "category": "일식", "taste": "매콤한", "temp": "뜨거운", "calories": 600, "sugar": 5, "cholesterol": 40, "desc": "칼칼하고 깊은 국물 맛의 일본식 라멘", "img_url": "https://images.unsplash.com/photo-1557872943-16a5ac26437e?q=80&w=600"},
    {"name": "수제 돈까스", "category": "일식", "taste": "기름진", "temp": "뜨거운", "calories": 750, "sugar": 15, "cholesterol": 40, "desc": "바삭하게 튀겨낸 겉바속촉 두툼한 돼지고기 돈까스", "img_url": "https://images.unsplash.com/photo-1598514982205-f36b96d1e8d4?q=80&w=600"},
    {"name": "텐동 (튀김덮밥)", "category": "일식", "taste": "기름진", "temp": "뜨거운", "calories": 850, "sugar": 15, "cholesterol": 35, "desc": "바삭한 모둠 튀김이 밥 위에 가득 올라간 덮밥", "img_url": "https://images.unsplash.com/photo-1617196034183-421b4917c92d?q=80&w=600"},
    {"name": "냉소바", "category": "일식", "taste": "달콤한", "temp": "차가운", "calories": 400, "sugar": 12, "cholesterol": 0, "desc": "살얼음 동동 띄운 달큰한 간장 육수와 메밀면", "img_url": "https://images.unsplash.com/photo-1552611052-33e04de081de?q=80&w=600"},
    {"name": "우동", "category": "일식", "taste": "담백한", "temp": "뜨거운", "calories": 450, "sugar": 8, "cholesterol": 5, "desc": "가쓰오부시로 우려낸 맑은 국물과 통통한 면발", "img_url": "https://images.unsplash.com/photo-1618889482923-38250401a84e?q=80&w=600"},
    {"name": "오코노미야키", "category": "일식", "taste": "달콤한", "temp": "뜨거운", "calories": 600, "sugar": 20, "cholesterol": 30, "desc": "달콤한 소스와 마요네즈가 듬뿍 뿌려진 일본식 부침개", "img_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?q=80&w=600"},
    {"name": "가츠동", "category": "일식", "taste": "달콤한", "temp": "뜨거운", "calories": 700, "sugar": 15, "cholesterol": 40, "desc": "촉촉한 계란과 특제 소스가 스며든 돈까스 덮밥", "img_url": "https://loremflickr.com/400/300/katsudon?random=1"},
    {"name": "사케동", "category": "일식", "taste": "담백한", "temp": "차가운", "calories": 500, "sugar": 8, "cholesterol": 45, "desc": "두툼하고 신선한 연어가 듬뿍 올라간 생연어 덮밥", "img_url": "https://loremflickr.com/400/300/salmon?random=1"},
    {"name": "규카츠", "category": "일식", "taste": "기름진", "temp": "뜨거운", "calories": 800, "sugar": 5, "cholesterol": 50, "desc": "겉은 바삭 속은 레어로 개인 화로에 구워먹는 소고기 튀김", "img_url": "https://loremflickr.com/400/300/meat?random=3"},
    {"name": "장어덮밥", "category": "일식", "taste": "달콤한", "temp": "뜨거운", "calories": 650, "sugar": 20, "cholesterol": 60, "desc": "달짝지근한 타레 소스를 넉넉히 발라 구운 보양 장어", "img_url": "https://loremflickr.com/400/300/eel?random=1"},
    {"name": "타코야키", "category": "일식", "taste": "달콤한", "temp": "뜨거운", "calories": 300, "sugar": 10, "cholesterol": 15, "desc": "가쓰오부시가 춤추고 달달한 소스가 덮인 문어빵", "img_url": "https://loremflickr.com/400/300/takoyaki?random=1"},
    {"name": "나가사키 짬뽕", "category": "일식", "taste": "담백한", "temp": "뜨거운", "calories": 600, "sugar": 5, "cholesterol": 40, "desc": "돼지뼈와 해산물로 우려낸 뽀야면서도 칼칼한 국물", "img_url": "https://loremflickr.com/400/300/noodle?random=4"},
    {"name": "스키야키", "category": "일식", "taste": "달콤한", "temp": "뜨거운", "calories": 700, "sugar": 25, "cholesterol": 45, "desc": "간장 육수에 소고기를 끓여 생계란에 찍어먹는 요리", "img_url": "https://loremflickr.com/400/300/sukiyaki?random=1"},
    {"name": "가라아게", "category": "일식", "taste": "기름진", "temp": "뜨거운", "calories": 550, "sugar": 5, "cholesterol": 30, "desc": "바삭하고 짭조름하게 튀겨낸 일본식 마늘 치킨", "img_url": "https://loremflickr.com/400/300/friedchicken?random=1"},
    {"name": "야키토리 모둠", "category": "일식", "taste": "달콤한", "temp": "뜨거운", "calories": 350, "sugar": 10, "cholesterol": 40, "desc": "다양한 부위를 숯불에 구워낸 닭꼬치 구이", "img_url": "https://loremflickr.com/400/300/yakitori?random=1"},
    {"name": "모츠나베", "category": "일식", "taste": "기름진", "temp": "뜨거운", "calories": 800, "sugar": 8, "cholesterol": 90, "desc": "고소한 대창과 부추가 듬뿍 들어간 후쿠오카 명물 전골", "img_url": "https://loremflickr.com/400/300/stew?random=5"},
    {"name": "명란 마요 덮밥", "category": "일식", "taste": "기름진", "temp": "상온", "calories": 500, "sugar": 5, "cholesterol": 120, "desc": "짭조름한 명란과 고소한 마요네즈가 밥 위에 듬뿍", "img_url": "https://loremflickr.com/400/300/rice?random=1"},
    {"name": "새우튀김 소바", "category": "일식", "taste": "담백한", "temp": "차가운", "calories": 450, "sugar": 10, "cholesterol": 10, "desc": "커다란 새우튀김을 얹은 시원하고 깔끔한 메밀 국수", "img_url": "https://loremflickr.com/400/300/soba?random=1"},
    {"name": "카레라이스", "category": "일식", "taste": "매콤한", "temp": "뜨거운", "calories": 600, "sugar": 8, "cholesterol": 15, "desc": "진하고 부드럽게 끓여낸 정통 일본식 카레", "img_url": "https://loremflickr.com/400/300/curry?random=1"},

    # 중식 (15개)
    {"name": "마라탕", "category": "중식", "taste": "매콤한", "temp": "뜨거운", "calories": 700, "sugar": 10, "cholesterol": 50, "desc": "직접 고른 재료로 즐기는 얼얼하게 매운 국물 요리", "img_url": "https://images.unsplash.com/photo-1585238342024-78d387f4a707?q=80&w=600"},
    {"name": "탕수육", "category": "중식", "taste": "달콤한", "temp": "뜨거운", "calories": 800, "sugar": 40, "cholesterol": 60, "desc": "새콤달콤한 특제 소스와 바삭한 돼지고기 튀김", "img_url": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?q=80&w=600"},
    {"name": "고추잡채", "category": "중식", "taste": "매콤한", "temp": "뜨거운", "calories": 550, "sugar": 15, "cholesterol": 20, "desc": "아삭한 피망과 볶은 고기를 꽃빵에 싸먹는 요리", "img_url": "https://images.unsplash.com/photo-1580959458925-5028aa829293?q=80&w=600"},
    {"name": "짜장면", "category": "중식", "taste": "달콤한", "temp": "뜨거운", "calories": 750, "sugar": 25, "cholesterol": 20, "desc": "달콤짭짤한 춘장 소스에 볶아낸 국민 배달 음식", "img_url": "https://images.unsplash.com/photo-1616801946051-5b7fb71c4c1a?q=80&w=600"},
    {"name": "유린기", "category": "중식", "taste": "달콤한", "temp": "상온", "calories": 650, "sugar": 20, "cholesterol": 40, "desc": "바삭한 닭고기 튀김에 상큼한 간장 소스를 곁들인 요리", "img_url": "https://images.unsplash.com/photo-1616801946288-511bbdb999cc?q=80&w=600"},
    {"name": "중국식 냉면", "category": "중식", "taste": "담백한", "temp": "차가운", "calories": 500, "sugar": 15, "cholesterol": 10, "desc": "땅콩 소스가 들어가 고소하고 새콤시원한 여름 별미", "img_url": "https://images.unsplash.com/photo-1552611052-33e04de081de?q=80&w=600"},
    {"name": "군만두", "category": "중식", "taste": "기름진", "temp": "뜨거운", "calories": 600, "sugar": 5, "cholesterol": 25, "desc": "기름에 튀기듯 구워내어 겉바속촉의 진수를 보여주는 만두", "img_url": "https://images.unsplash.com/photo-1496116218417-1a781b1c416c?q=80&w=600"},
    {"name": "해물 짬뽕", "category": "중식", "taste": "매콤한", "temp": "뜨거운", "calories": 650, "sugar": 10, "cholesterol": 50, "desc": "얼큰하고 시원한 해물 육수와 불맛이 가득한 국물", "img_url": "https://loremflickr.com/400/300/spicynoodle?random=1"},
    {"name": "게살 볶음밥", "category": "중식", "taste": "기름진", "temp": "뜨거운", "calories": 700, "sugar": 5, "cholesterol": 40, "desc": "고슬고슬하게 웍에 볶아 짜장 소스와 곁들이는 중식 볶음밥", "img_url": "https://loremflickr.com/400/300/friedrice?random=1"},
    {"name": "깐풍기", "category": "중식", "taste": "매콤한", "temp": "뜨거운", "calories": 750, "sugar": 20, "cholesterol": 35, "desc": "매콤달콤한 소스에 마늘향이 가미된 닭고기 튀김", "img_url": "https://loremflickr.com/400/300/chicken?random=3"},
    {"name": "마라샹궈", "category": "중식", "taste": "매콤한", "temp": "뜨거운", "calories": 800, "sugar": 12, "cholesterol": 55, "desc": "각종 재료를 마라 소스에 볶아낸 알싸한 밥도둑", "img_url": "https://loremflickr.com/400/300/spicy?random=3"},
    {"name": "크림새우", "category": "중식", "taste": "기름진", "temp": "뜨거운", "calories": 650, "sugar": 30, "cholesterol": 70, "desc": "바삭한 큼직한 새우 튀김을 달콤하고 부드러운 크림소스에 버무림", "img_url": "https://loremflickr.com/400/300/shrimp?random=1"},
    {"name": "마파두부 덮밥", "category": "중식", "taste": "매콤한", "temp": "뜨거운", "calories": 450, "sugar": 8, "cholesterol": 10, "desc": "부드러운 연두부와 매콤한 두반장 소스가 밥과 비벼지는 맛", "img_url": "https://loremflickr.com/400/300/tofu?random=1"},
    {"name": "류산슬", "category": "중식", "taste": "담백한", "temp": "뜨거운", "calories": 500, "sugar": 5, "cholesterol": 30, "desc": "해삼, 새우, 버섯을 걸쭉하게 볶아낸 부드러운 고급 요리", "img_url": "https://loremflickr.com/400/300/seafood?random=1"},
    {"name": "양꼬치", "category": "중식", "taste": "기름진", "temp": "뜨거운", "calories": 600, "sugar": 2, "cholesterol": 50, "desc": "빙글빙글 돌아가는 기계에서 쯔란에 찍어먹는 고소한 양고기", "img_url": "https://loremflickr.com/400/300/meat?random=4"},

    # 양식 (20개)
    {"name": "토마토 바질 파스타", "category": "양식", "taste": "담백한", "temp": "뜨거운", "calories": 450, "sugar": 12, "cholesterol": 10, "desc": "신선한 토마토 소스로 맛을 낸 정통 이탈리안 파스타", "img_url": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?q=80&w=600"},
    {"name": "페퍼로니 피자", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 900, "sugar": 15, "cholesterol": 40, "desc": "짭조름한 페퍼로니와 치즈가 듬뿍 올라간 화덕 피자", "img_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e?q=80&w=600"},
    {"name": "클럽 샌드위치", "category": "양식", "taste": "담백한", "temp": "상온", "calories": 400, "sugar": 5, "cholesterol": 15, "desc": "베이컨, 치즈, 토마토가 겹겹이 쌓인 든든한 샌드위치", "img_url": "https://images.unsplash.com/photo-1528735602780-2552fd46c7af?q=80&w=600"},
    {"name": "크림 까르보나라", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 750, "sugar": 8, "cholesterol": 60, "desc": "베이컨과 크림이 들어가 꾸덕하고 고소한 파스타", "img_url": "https://images.unsplash.com/photo-1612874683151-8bc4aa9a5c89?q=80&w=600"},
    {"name": "스테이크", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 800, "sugar": 2, "cholesterol": 90, "desc": "육즙이 가득한 두툼한 소고기 철판 구이", "img_url": "https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=600"},
    {"name": "바베큐 폭립", "category": "양식", "taste": "달콤한", "temp": "뜨거운", "calories": 950, "sugar": 30, "cholesterol": 70, "desc": "달달한 바베큐 소스를 발라 뼈째 뜯어먹는 돼지 등갈비", "img_url": "https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?q=80&w=600"},
    {"name": "에그 베네딕트", "category": "양식", "taste": "담백한", "temp": "상온", "calories": 550, "sugar": 6, "cholesterol": 80, "desc": "잉글리시 머핀 위에 수란과 홀랜다이즈 소스를 얹은 브런치", "img_url": "https://images.unsplash.com/photo-1608039829572-78524f79c4c7?q=80&w=600"},
    {"name": "수제 버거", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 850, "sugar": 15, "cholesterol": 60, "desc": "육즙 가득 소고기 패티와 신선한 야채가 들어간 수제 버거", "img_url": "https://loremflickr.com/400/300/burger?random=1"},
    {"name": "알리오 올리오", "category": "양식", "taste": "담백한", "temp": "뜨거운", "calories": 450, "sugar": 2, "cholesterol": 5, "desc": "매콤한 페페론치노와 마늘의 풍미로 즐기는 오일 파스타", "img_url": "https://loremflickr.com/400/300/pasta?random=1"},
    {"name": "라자냐", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 700, "sugar": 10, "cholesterol": 40, "desc": "진한 라구 소스와 넓은 면이 층층이 쌓인 오븐 구이", "img_url": "https://loremflickr.com/400/300/lasagna?random=1"},
    {"name": "로제 파스타", "category": "양식", "taste": "달콤한", "temp": "뜨거운", "calories": 600, "sugar": 15, "cholesterol": 30, "desc": "상큼한 토마토와 부드러운 크림이 매력적으로 결합된 소스", "img_url": "https://loremflickr.com/400/300/pasta?random=2"},
    {"name": "피쉬 앤 칩스", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 800, "sugar": 5, "cholesterol": 45, "desc": "겉은 바삭 속은 촉촉한 대구살 튀김과 감자튀김", "img_url": "https://loremflickr.com/400/300/fish?random=3"},
    {"name": "트러플 뇨끼", "category": "양식", "taste": "담백한", "temp": "뜨거운", "calories": 500, "sugar": 8, "cholesterol": 20, "desc": "트러플 오일 향이 가득한 쫄깃하고 부드러운 감자 수제비", "img_url": "https://loremflickr.com/400/300/pasta?random=3"},
    {"name": "미트볼 스파게티", "category": "양식", "taste": "매콤한", "temp": "뜨거운", "calories": 650, "sugar": 12, "cholesterol": 55, "desc": "두꺼운 미트볼이 잔뜩 올라간 새콤매콤 스파게티", "img_url": "https://loremflickr.com/400/300/pasta?random=4"},
    {"name": "버섯 크림 리조또", "category": "양식", "taste": "담백한", "temp": "뜨거운", "calories": 550, "sugar": 5, "cholesterol": 25, "desc": "풍부한 크림 향과 쫄깃한 버섯이 어우러진 부드러운 쌀 요리", "img_url": "https://loremflickr.com/400/300/risotto?random=1"},
    {"name": "콥 샐러드", "category": "양식", "taste": "담백한", "temp": "차가운", "calories": 400, "sugar": 10, "cholesterol": 20, "desc": "베이컨, 아보카도, 계란을 정갈하게 담아낸 푸짐한 다이어트식", "img_url": "https://loremflickr.com/400/300/salad?random=1"},
    {"name": "시카고 딥디쉬 피자", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 1100, "sugar": 20, "cholesterol": 80, "desc": "부드러운 치즈가 폭포수처럼 쏟아지는 파이 같은 피자", "img_url": "https://loremflickr.com/400/300/pizza?random=1"},
    {"name": "핫도그", "category": "양식", "taste": "기름진", "temp": "상온", "calories": 450, "sugar": 10, "cholesterol": 30, "desc": "폭신한 빵 사이에 육즙 가득 소시지와 머스타드, 케첩 듬뿍", "img_url": "https://loremflickr.com/400/300/hotdog?random=1"},
    {"name": "프렌치 토스트", "category": "양식", "taste": "달콤한", "temp": "뜨거운", "calories": 400, "sugar": 25, "cholesterol": 40, "desc": "계란물에 적셔 버터에 구운 후 메이플 시럽을 얹은 빵", "img_url": "https://loremflickr.com/400/300/toast?random=1"},
    {"name": "감바스 알 아히요", "category": "양식", "taste": "기름진", "temp": "뜨거운", "calories": 600, "sugar": 2, "cholesterol": 50, "desc": "오동통한 새우를 마늘향 가득한 올리브유에 익힌 스페인 요리", "img_url": "https://loremflickr.com/400/300/shrimp?random=2"},

    # 기타 및 아시안/디저트 (15개)
    {"name": "아보카도 연어 샐러드", "category": "기타", "taste": "담백한", "temp": "차가운", "calories": 250, "sugar": 8, "cholesterol": 5, "desc": "건강하고 가볍게 즐기는 신선하고 푸짐한 샐러드", "img_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=600"},
    {"name": "새우 팟타이", "category": "기타", "taste": "달콤한", "temp": "뜨거운", "calories": 500, "sugar": 20, "cholesterol": 15, "desc": "새콤달콤한 맛이 매력적인 태국식 볶음 쌀국수", "img_url": "https://images.unsplash.com/photo-1559314809-0d155014e29e?q=80&w=600"},
    {"name": "인도 치킨 마크니 커리", "category": "기타", "taste": "기름진", "temp": "뜨거운", "calories": 600, "sugar": 10, "cholesterol": 35, "desc": "부드럽고 풍미 가득한 인도식 버터 치킨 커리와 난", "img_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?q=80&w=600"},
    {"name": "베트남 양지 쌀국수", "category": "기타", "taste": "담백한", "temp": "뜨거운", "calories": 400, "sugar": 5, "cholesterol": 10, "desc": "진한 소고기 육수에 양파와 숙주를 듬뿍 넣은 속 편한 맑은 국수", "img_url": "https://images.unsplash.com/photo-1582878826629-29b7ad1cb431?q=80&w=600"},
    {"name": "분짜", "category": "기타", "taste": "달콤한", "temp": "차가운", "calories": 550, "sugar": 25, "cholesterol": 20, "desc": "새콤달콤한 피시 소스 국물에 숯불고기와 쌀국수를 적셔먹는 요리", "img_url": "https://images.unsplash.com/photo-1564834724105-918b73d1b9e0?q=80&w=600"},
    {"name": "멕시칸 비프 타코", "category": "기타", "taste": "매콤한", "temp": "상온", "calories": 350, "sugar": 4, "cholesterol": 15, "desc": "또띠아에 매콤한 고기와 살사 소스, 야채를 싸먹는 간편 요리", "img_url": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?q=80&w=600"},
    {"name": "하와이안 연어 포케", "category": "기타", "taste": "담백한", "temp": "차가운", "calories": 400, "sugar": 10, "cholesterol": 5, "desc": "연어와 신선한 야채를 깍둑썰어 건강하게 비벼먹는 덮밥", "img_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600"},
    {"name": "나시고랭", "category": "기타", "taste": "달콤한", "temp": "뜨거운", "calories": 600, "sugar": 15, "cholesterol": 40, "desc": "달짝지근한 계란과 소스로 세계인의 입맛을 잡은 볶음밥", "img_url": "https://loremflickr.com/400/300/friedrice?random=2"},
    {"name": "똠얌꿍", "category": "기타", "taste": "매콤한", "temp": "뜨거운", "calories": 400, "sugar": 10, "cholesterol": 50, "desc": "시큼하고 매콤한 오묘하고 중독성 강한 세계 3대 수프", "img_url": "https://loremflickr.com/400/300/soup?random=5"},
    {"name": "치킨 퀘사디아", "category": "기타", "taste": "기름진", "temp": "뜨거운", "calories": 550, "sugar": 5, "cholesterol": 35, "desc": "구운 또띠아 속에 치즈와 재료가 듬뿍 들어간 멕시코 피자", "img_url": "https://loremflickr.com/400/300/mexican?random=1"},
    {"name": "포크 반미 샌드위치", "category": "기타", "taste": "담백한", "temp": "상온", "calories": 480, "sugar": 8, "cholesterol": 15, "desc": "바삭한 바게트 속에 고기와 무절임이 가득한 베트남식 핫도그", "img_url": "https://loremflickr.com/400/300/sandwich?random=1"},
    {"name": "치킨 도시락", "category": "기타", "taste": "기름진", "temp": "뜨거운", "calories": 650, "sugar": 15, "cholesterol": 25, "desc": "바삭한 순살 치킨과 밥이 조화로운 클래식 메뉴", "img_url": "https://loremflickr.com/400/300/rice?random=2"},
    {"name": "마카롱 3구 세트", "category": "기타", "taste": "달콤한", "temp": "차가운", "calories": 450, "sugar": 60, "cholesterol": 10, "desc": "쫀득하고 찌를 듯이 달달한 프랑스의 예쁜 대표 디저트", "img_url": "https://loremflickr.com/400/300/macaron?random=1"},
    {"name": "애플 망고 빙수", "category": "기타", "taste": "달콤한", "temp": "차가운", "calories": 800, "sugar": 80, "cholesterol": 5, "desc": "달콤한 생망고가 듬뿍 올라간 시원하고 달달한 우유 얼음 빙수", "img_url": "https://loremflickr.com/400/300/desert?random=1"},
    {"name": "소떡소떡 꼬치", "category": "기타", "taste": "매콤한", "temp": "뜨거운", "calories": 300, "sugar": 15, "cholesterol": 5, "desc": "소시지와 떡이 번갈아 끼워져 마약 소스를 바른 휴게소 간식", "img_url": "https://loremflickr.com/400/300/snack?random=1"},
]

# ==============================================================================
# CSS 스타일링 (UX/UI 향상을 위한 커스텀 스타일)
# HTML과 CSS를 주입하여 Card UI가 아름답게 보이도록 설정합니다.
# ==============================================================================
st.markdown("""
<style>
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
# 1. 자동 감지 기능 함수 (위치, 날씨 & 시간)
# ==============================================================================
@st.cache_data(ttl=3600)  # 스트림릿에서 같은 요청을 반복하지 않도록, 1시간동안 결과 저장(캐싱)
def get_user_location_and_weather():
    """사용자의 접속 IP를 확인해 국가/도시 및 날씨 정보를 반환합니다."""
    location = "위치 자동 감지 실패 📍"
    weather = "날씨 정보 없음 ☁️"
    try:
        # ip-api.com의 무료 API를 활용해 현재 위치 정보 추출
        response = requests.get('http://ip-api.com/json/', timeout=3)
        data = response.json()
        if data['status'] == 'success':
            location = f"{data['country']}, {data['city']} 📍"
            lat = data['lat']
            lon = data['lon']
            
            # Open-Meteo 무료 API로 해당 위치의 날씨 가져오기
            weather_resp = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true', timeout=3)
            if weather_resp.status_code == 200:
                w_data = weather_resp.json()
                if 'current_weather' in w_data:
                    temp = w_data['current_weather']['temperature']
                    code = w_data['current_weather']['weathercode']
                    
                    # WMO 날씨 코드 변환
                    if code == 0: icon = "☀️"
                    elif 1 <= code <= 3: icon = "⛅"
                    elif 45 <= code <= 48: icon = "🌫️"
                    elif 51 <= code <= 67: icon = "🌧️"
                    elif 71 <= code <= 77: icon = "❄️"
                    elif 80 <= code <= 99: icon = "⛈️"
                    else: icon = "☁️"
                    
                    weather = f"{temp}℃ {icon}"
    except Exception as e:
        pass # 에러 발생 시 무시
    return location, weather

def get_current_time_info():
    """현재 시간을 기반으로 '아침, 점심, 저녁, 야식'을 판별합니다."""
    # datetime.now()를 통해 현재 시간을 가져와서 시간(hour)만 추출합니다.
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 11:
        return "아침 🌅"
    elif 11 <= current_hour < 16:
        return "점심 ☀️"
    elif 16 <= current_hour < 21:
        return "저녁 🌆"
    else:
        return "야식 🌙"

# ==============================================================================
# 2. 메인 UI 화면 그리기
# ==============================================================================

# 타이틀 출력
st.title("🍽️ 오늘의 맞춤 메뉴 추천 앱")
st.markdown("당신의 상황과 취향을 분석하여 완벽한 식사를 추천해 드릴게요!")

# 상단 상태 알림 배너 (위치, 날씨, 시간)
# HTML을 직접 렌더링하기 위해 st.markdown의 unsafe_allow_html=True 속성 사용
location, weather = get_user_location_and_weather()
time_context = get_current_time_info()
st.markdown(f"""
<div class="status-banner">
    현재 감지된 상황 👉 {location} | 날씨: {weather} | 시간대: {time_context}
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 사용자 선택 필터 (3가지 핵심)
# columns 레이아웃을 사용해 나란히 3개의 선택 박스를 배치합니다.
# ==============================================================================
st.subheader("🔍 당신의 취향을 알려주세요")

# 화면을 3개의 세로 열(Column)로 나눕니다.
col1, col2, col3 = st.columns(3)

with col1:
    # 카테고리 선택 드롭다운
    selected_category = st.selectbox(
        "국가/문화권",
        ["전체", "한식", "일식", "중식", "양식", "기타"]
    )

with col2:
    # 맛 프로필 선택 드롭다운
    selected_taste = st.selectbox(
        "맛의 프로필",
        ["전체", "매콤한", "담백한", "달콤한", "기름진"]
    )

with col3:
    # 온도 선택 드롭다운
    selected_temp = st.selectbox(
        "음식의 온도",
        ["전체", "뜨거운", "차가운", "상온"]
    )

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
st.subheader(f"💡 현재 추천된 '{selected_category}' & '{selected_taste}' 메뉴입니다!")

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
<!-- 이미지 -->
<div class="food-placeholder">🍽️ 메뉴 사진 준비중</div>

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
if st.button("🔄 조건은 그대로, 다른 메뉴 추천받기", use_container_width=False):
    pass # Streamlit은 버튼 클릭 시 자동으로 전체 코드를 재실행하므로 추가 코드가 없어도 리로드 역할을 합니다.
