import streamlit as st
import feedparser
import google.generativeai as genai
from datetime import datetime
import re
from data_manager import DataManager

# 1. 페이지 설정
st.set_page_config(page_title="My AI Newsroom", layout="wide")
st.title("📰 나만의 IT 뉴스룸")

# URL 검증 함수
def is_valid_url(url):
    """URL 유효성 검사"""
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and pattern.search(url)

# 2. 데이터 매니저 및 API 설정
try:
    dm = DataManager()
    genai.configure(api_key=st.secrets["general"]["gemini_api_key"])
except Exception as e:
    st.error(f"초기화 오류: {e}")
    st.stop()

# 3. 데이터 로드 (타입 보장)
feeds = dm.load_json("data/feeds.json", default_value=[])
if not isinstance(feeds, list):
    feeds = []

news_data = dm.load_json("data/news_data.json", default_value={})
if not isinstance(news_data, dict):
    news_data = {}

stats = dm.load_json("data/stats.json", default_value={"visitors": 0})
if not isinstance(stats, dict):
    stats = {"visitors": 0}

# 접속자 통계 업데이트 (새 세션일 경우만 카운트)
if 'visited' not in st.session_state:
    stats['visitors'] = stats.get('visitors', 0) + 1
    dm.save_json("data/stats.json", stats, "Update visitor count")
    st.session_state['visited'] = True

# ------------------------------------------------------------------
# UI: 탭 구성
tab1, tab2 = st.tabs(["📢 오늘의 브리핑", "⚙️ 대시보드 (관리)"])

# ------------------------------------------------------------------
# 탭 1: 메인 뉴스룸
with tab1:
    today = datetime.now().strftime("%Y-%m-%d")
    
    st.subheader(f"📅 {today} IT 트렌드 브리핑")
    
    # 해당 날짜의 데이터가 있는지 확인
    if today in news_data:
        daily_summary = news_data[today]
        if isinstance(daily_summary, dict) and 'summary' in daily_summary:
            st.markdown(daily_summary['summary'])
            
            with st.expander("🔗 참고한 원본 기사 목록"):
                sources = daily_summary.get('sources', [])
                if isinstance(sources, list):
                    for item in sources:
                        if isinstance(item, dict):
                            title = item.get('title', '제목 없음')
                            link = item.get('link', '')
                            st.write(f"- [{title}]({link})")
                        else:
                            st.write(f"- {item}")
        else:
            st.warning("데이터 형식이 올바르지 않습니다.")
    else:
        st.info("아직 오늘의 분석 데이터가 없습니다. 대시보드에서 분석을 실행해주세요.")
        
    st.divider()
    st.caption(f"👀 총 누적 방문자 수: {stats.get('visitors', 0)}명")

# ------------------------------------------------------------------
# 탭 2: 대시보드
with tab2:
    st.header("관리자 대시보드")
    
    col1, col2 = st.columns(2)
    
    # [기능 1] RSS 피드 관리
    with col1:
        st.subheader("📡 RSS 피드 관리")
        new_feed = st.text_input("새 RSS URL 추가", placeholder="https://...")
        if st.button("피드 추가"):
            if not new_feed:
                st.warning("URL을 입력해주세요.")
            elif not is_valid_url(new_feed):
                st.warning("유효한 URL 형식이 아닙니다.")
            elif new_feed in feeds:
                st.warning("이미 존재하는 피드입니다.")
            else:
                feeds.append(new_feed)
                if dm.save_json("data/feeds.json", feeds, "Add new RSS feed"):
                    st.success("피드가 추가되었습니다!")
                    st.rerun()

        st.write("📋 현재 등록된 피드:")
        if not feeds:
            st.info("등록된 피드가 없습니다.")
        else:
            for idx, url in enumerate(feeds):
                c1, c2 = st.columns([0.8, 0.2])
                c1.text(url)
                if c2.button("삭제", key=f"del_{idx}"):
                    feeds.pop(idx)
                    if dm.save_json("data/feeds.json", feeds, "Delete RSS feed"):
                        st.success("피드가 삭제되었습니다!")
                        st.rerun()

    # [기능 2] 수집 및 AI 분석 트리거
    with col2:
        st.subheader("🧠 수집 및 AI 분석")
        st.write("등록된 모든 RSS를 긁어와 오늘 날짜로 분석합니다.")
        
        if st.button("🚀 분석 시작 (시간이 걸립니다)"):
            if not feeds:
                st.warning("먼저 RSS 피드를 추가해주세요.")
            else:
                all_articles = []
                
                # 1. RSS 파싱
                progress_text = "RSS 피드 수집 중..."
                my_bar = st.progress(0, text=progress_text)
                
                for i, url in enumerate(feeds):
                    try:
                        feed = feedparser.parse(url)
                        # 오늘/최근 기사만 필터링 (여기선 단순 상위 3개씩 수집 예시)
                        for entry in feed.entries[:3]:
                            all_articles.append({
                                "title": entry.get('title', '제목 없음'),
                                "link": entry.get('link', '')
                            })
                    except Exception as e:
                        st.error(f"RSS 파싱 오류 ({url}): {e}")
                    
                    # 진행률 업데이트 (feeds가 비어있지 않으므로 안전)
                    if len(feeds) > 0:
                        my_bar.progress((i + 1) / len(feeds), text=progress_text)
                
                # 2. Gemini 분석
                if all_articles:
                    my_bar.progress(0.8, text="Gemini가 뉴스룸 리포트를 작성 중입니다...")
                    
                    try:
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        context = "\n".join([f"- {a['title']} ({a['link']})" for a in all_articles])
                        prompt = f"""
                        다음은 오늘 수집된 국내외 IT 뉴스 헤드라인 목록입니다.
                        
                        [뉴스 데이터]
                        {context}
                        
                        이 뉴스들을 바탕으로 '오늘의 IT 뉴스룸' 리포트를 마크다운 형식으로 작성해주세요.
                        조건:
                        1. 가장 핫한 키워드 3개를 뽑아주세요.
                        2. 주요 이슈를 3가지 카테고리(예: AI, 모바일, 비즈니스 등)로 분류하여 요약하세요.
                        3. 전체적인 시장 분위기를 한 문장으로 평가하세요.
                        4. 이모지를 적절히 사용하여 가독성을 높이세요.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        # 3. 결과 저장 (GitHub)
                        data_to_save = {
                            "summary": response.text,
                            "sources": all_articles,  # 이미 딕셔너리 형태
                            "created_at": str(datetime.now())
                        }
                        
                        # 기존 데이터에 오늘 날짜 키로 업데이트
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        news_data[today_str] = data_to_save
                        
                        if dm.save_json("data/news_data.json", news_data, f"Update news analysis for {today_str}"):
                            my_bar.progress(1.0, text="완료!")
                            st.success("분석이 완료되었습니다! '오늘의 브리핑' 탭을 확인하세요.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Gemini API 오류: {e}")
                        my_bar.empty()
                else:
                    st.warning("수집된 뉴스가 없습니다.")
                    my_bar.empty()


