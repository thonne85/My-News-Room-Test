Cursor AI를 활용해 **"GitHub를 데이터베이스처럼 사용하는 Streamlit 뉴스룸"**을 구축하는 완벽한 설계를 도와드리겠습니다.

이 구조의 핵심은 **Streamlit Cloud는 재부팅 시 로컬 파일이 초기화**된다는 점입니다. 따라서 데이터(JSON)가 변경될 때마다 **GitHub API를 통해 리포지토리에 커밋(저장)**하는 로직이 필수적입니다.

아래 가이드를 따라 Cursor에게 코드를 작성해달라고 하거나, 직접 파일을 생성하세요.

---

### 🧱 프로젝트 구조
먼저 폴더 구조를 이렇게 잡아야 합니다.

```text
my-newsroom/
├── .streamlit/
│   └── secrets.toml      # API 키 저장 (로컬 테스트용)
├── data/                 # 데이터 폴더 (초기 파일 생성 필요)
│   ├── feeds.json        # RSS URL 목록
│   ├── news_data.json    # 날짜별 분석된 뉴스
│   └── stats.json        # 접속자 통계
├── data_manager.py       # GitHub 연동 및 JSON 처리 모듈
├── app.py                # 메인 UI 및 로직
└── requirements.txt      # 라이브러리 목록
```

---

### 1단계: 필수 설정 (Secrets 및 라이브러리)

**`requirements.txt`**
```text
streamlit
feedparser
google-generativeai
PyGithub
pandas
```

**`.streamlit/secrets.toml`** (로컬 실행용, 배포 시엔 Streamlit Cloud 설정에 입력)
```toml
[general]
github_token = "github_pat_..."  # GitHub Personal Access Token (Repo 권한 필요)
repo_name = "username/repo-name" # 본인 깃헙 아이디/리포지토리명
gemini_api_key = "AIzaSy..."     # 구글 Gemini API 키
```

---

### 2단계: GitHub 연동 모듈 (`data_manager.py`)
이 파일은 JSON 데이터를 읽고, 수정 사항이 생기면 GitHub에 자동으로 커밋해주는 역할을 합니다. Cursor에게 이 코드를 작성해달라고 하세요.

```python
import streamlit as st
import json
import os
from github import Github

class DataManager:
    def __init__(self):
        self.github_token = st.secrets["general"]["github_token"]
        self.repo_name = st.secrets["general"]["repo_name"]
        self.g = Github(self.github_token)
        self.repo = self.g.get_repo(self.repo_name)

    def load_json(self, file_path):
        """GitHub에서 JSON 파일을 읽어옵니다. 없으면 빈 값을 반환."""
        try:
            contents = self.repo.get_contents(file_path)
            return json.loads(contents.decoded_content.decode())
        except:
            # 파일이 없으면 기본 구조 반환
            if "feeds" in file_path: return []
            if "stats" in file_path: return {"visitors": 0}
            return {}

    def save_json(self, file_path, data, commit_message):
        """데이터를 JSON으로 변환하여 GitHub에 커밋합니다."""
        try:
            content = json.dumps(data, indent=4, ensure_ascii=False)
            try:
                # 파일이 존재하면 업데이트
                file = self.repo.get_contents(file_path)
                self.repo.update_file(file.path, commit_message, content, file.sha)
            except:
                # 파일이 없으면 생성
                self.repo.create_file(file_path, commit_message, content)
            return True
        except Exception as e:
            st.error(f"저장 실패: {e}")
            return False
```

---

### 3단계: 메인 앱 코드 (`app.py`)
Cursor에게 아래 명세를 주고 코드를 작성하게 하거나, 복사해서 붙여넣으세요.

```python
import streamlit as st
import feedparser
import google.generativeai as genai
from datetime import datetime
import pandas as pd
from data_manager import DataManager

# 1. 페이지 설정
st.set_page_config(page_title="My AI Newsroom", layout="wide")
st.title("📰 나만의 IT 뉴스룸")

# 2. 데이터 매니저 및 API 설정
dm = DataManager()
genai.configure(api_key=st.secrets["general"]["gemini_api_key"])

# 3. 데이터 로드 (캐싱하여 속도 향상 가능하지만 실시간성을 위해 직접 호출)
feeds = dm.load_json("data/feeds.json")
news_data = dm.load_json("data/news_data.json")
stats = dm.load_json("data/stats.json")

# 접속자 통계 업데이트 (새 세션일 경우만 카운트하는 로직은 생략하고 단순 새로고침 카운트)
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
        st.markdown(daily_summary['summary'])
        
        with st.expander("🔗 참고한 원본 기사 목록"):
            for item in daily_summary['sources']:
                st.write(f"- [{item['title']}]({item['link']})")
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
            if new_feed and new_feed not in feeds:
                feeds.append(new_feed)
                if dm.save_json("data/feeds.json", feeds, "Add new RSS feed"):
                    st.success("피드가 추가되었습니다!")
                    st.rerun()
            elif new_feed in feeds:
                st.warning("이미 존재하는 피드입니다.")

        st.write("📋 현재 등록된 피드:")
        for idx, url in enumerate(feeds):
            c1, c2 = st.columns([0.8, 0.2])
            c1.text(url)
            if c2.button("삭제", key=f"del_{idx}"):
                feeds.pop(idx)
                dm.save_json("data/feeds.json", feeds, "Delete RSS feed")
                st.rerun()

    # [기능 2] 수집 및 AI 분석 트리거
    with col2:
        st.subheader("🧠 수집 및 AI 분석")
        st.write("등록된 모든 RSS를 긁어와 오늘 날짜로 분석합니다.")
        
        if st.button("🚀 분석 시작 (시간이 걸립니다)"):
            all_articles = []
            
            # 1. RSS 파싱
            progress_text = "RSS 피드 수집 중..."
            my_bar = st.progress(0, text=progress_text)
            
            for i, url in enumerate(feeds):
                try:
                    feed = feedparser.parse(url)
                    # 오늘/최근 기사만 필터링 (여기선 단순 상위 3개씩 수집 예시)
                    for entry in feed.entries[:3]:
                        all_articles.append(f"- {entry.title} ({entry.link})")
                except Exception as e:
                    st.error(f"Error parsing {url}: {e}")
                my_bar.progress((i + 1) / len(feeds), text=progress_text)
            
            # 2. Gemini 분석
            if all_articles:
                my_bar.progress(0.8, text="Gemini가 뉴스룸 리포트를 작성 중입니다...")
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                context = "\n".join(all_articles)
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
                    "sources": [{"title": a.split('(')[0], "link": a.split('(')[-1].replace(')', '')} for a in all_articles],
                    "created_at": str(datetime.now())
                }
                
                # 기존 데이터에 오늘 날짜 키로 업데이트
                today_str = datetime.now().strftime("%Y-%m-%d")
                news_data[today_str] = data_to_save
                
                if dm.save_json("data/news_data.json", news_data, f"Update news analysis for {today_str}"):
                    my_bar.progress(1.0, text="완료!")
                    st.success("분석이 완료되었습니다! '오늘의 브리핑' 탭을 확인하세요.")
            else:
                st.warning("수집된 뉴스가 없습니다.")

```

---

### 4단계: Cursor AI 사용 팁 및 배포 방법

#### 1. 초기 데이터 파일 생성 (GitHub Repo)
GitHub 리포지토리에 `data` 폴더를 만들고 빈 파일들을 미리 올려두는 것이 좋습니다. (혹은 코드가 처음 실행될 때 생성되게 할 수도 있지만, 미리 구조를 잡는 게 안전합니다.)
*   `data/feeds.json`: `["https://feeds.feedburner.com/geeknews-feed"]` (예시 데이터 하나 넣어두기)
*   `data/news_data.json`: `{}`
*   `data/stats.json`: `{"visitors": 0}`

#### 2. Streamlit Cloud 배포
1.  GitHub에 위 코드들을 모두 푸시(Push)합니다.
2.  [Streamlit Cloud](https://share.streamlit.io/)에 접속하여 해당 리포지토리를 연결합니다.
3.  **Advanced Settings** (고급 설정)을 열고 **Secrets** 섹션에 다음 내용을 붙여넣습니다.

```toml
[general]
github_token = "여기에_깃허브_토큰"
repo_name = "사용자명/리포지토리명"
gemini_api_key = "여기에_제미나이_키"
```

#### 3. Cursor에게 요청하기 (복붙용 프롬프트)
만약 직접 코딩하기 귀찮다면 Cursor 채팅창(`Cmd+L` or `Ctrl+L`)에 아래 내용을 붙여넣으세요.

> "나는 Streamlit과 Gemini API를 이용해서 IT 뉴스 대시보드를 만들 거야.
> 중요한 건 DB 대신 GitHub 리포지토리의 JSON 파일을 데이터베이스처럼 써야 해.
>
> 1. `data_manager.py`: PyGithub 라이브러리를 써서 내 리포지토리의 json 파일을 읽고(load), 내용을 수정해서 커밋(save)하는 클래스를 만들어줘.
> 2. `app.py`: 메인 화면에는 날짜별 뉴스 요약을 보여주고, 대시보드 탭에서는 RSS URL을 추가/삭제하고, '분석 시작' 버튼을 누르면 RSS를 크롤링해서 Gemini에게 요약을 시킨 뒤 결과를 GitHub에 저장하는 기능을 구현해줘.
>
> 필요한 라이브러리와 secrets.toml 설정 예시도 알려줘."

이렇게 하면 위에서 설계한 코드를 Cursor가 문맥에 맞게 생성해 줄 것입니다.