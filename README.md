# 📰 My AI Newsroom

GitHub를 데이터베이스처럼 사용하는 Streamlit 기반 IT 뉴스룸입니다.

## 🎯 주요 기능

- **RSS 피드 수집**: 여러 RSS 피드에서 IT 뉴스를 자동으로 수집
- **AI 분석**: Google Gemini API를 활용한 뉴스 요약 및 분석
- **GitHub 기반 저장**: Streamlit Cloud의 임시 파일 시스템 대신 GitHub 리포지토리를 데이터베이스로 사용
- **실시간 대시보드**: RSS 피드 관리 및 분석 실행

## 📋 사전 요구사항

1. **GitHub Personal Access Token**
   - GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - `repo` 권한 필요 (또는 공개 리포지토리인 경우 `public_repo`)

2. **Google Gemini API Key**
   - [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급

3. **Python 3.8 이상**

## 🚀 설치 및 실행

### 1. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 설정 파일 구성

`.streamlit/secrets.toml` 파일을 열고 실제 값으로 수정하세요:

```toml
[general]
github_token = "github_pat_YOUR_TOKEN_HERE"
repo_name = "your-username/your-repo-name"
gemini_api_key = "YOUR_GEMINI_API_KEY"
```

### 3. GitHub 리포지토리 준비

1. 새 GitHub 리포지토리를 생성합니다
2. `data` 폴더를 만들고 다음 파일들을 생성합니다:
   - `data/feeds.json`: `["https://feeds.feedburner.com/geeknews-feed"]`
   - `data/news_data.json`: `{}`
   - `data/stats.json`: `{"visitors": 0}`

### 4. 로컬 실행

```bash
streamlit run app.py
```

## ☁️ Streamlit Cloud 배포

1. GitHub에 코드를 푸시합니다
2. [Streamlit Cloud](https://share.streamlit.io/)에 접속
3. 리포지토리를 연결합니다
4. **Advanced Settings** > **Secrets**에 다음 내용을 붙여넣습니다:

```toml
[general]
github_token = "여기에_깃허브_토큰"
repo_name = "사용자명/리포지토리명"
gemini_api_key = "여기에_제미나이_키"
```

## 📁 프로젝트 구조

```
my-newsroom/
├── .streamlit/
│   └── secrets.toml      # API 키 저장 (로컬 테스트용)
├── data/                 # 데이터 폴더
│   ├── feeds.json        # RSS URL 목록
│   ├── news_data.json    # 날짜별 분석된 뉴스
│   └── stats.json        # 접속자 통계
├── data_manager.py       # GitHub 연동 및 JSON 처리 모듈
├── app.py                # 메인 UI 및 로직
├── requirements.txt      # 라이브러리 목록
└── README.md             # 이 파일
```

## 🔧 주요 개선사항

- ✅ 구체적인 예외 처리
- ✅ 데이터 타입 검증
- ✅ URL 유효성 검사
- ✅ 빈 피드 리스트 처리
- ✅ 안전한 문자열 파싱
- ✅ 명확한 에러 메시지

## 📝 사용 방법

1. **RSS 피드 추가**: 대시보드 탭에서 RSS URL을 추가합니다
2. **뉴스 분석**: "분석 시작" 버튼을 클릭하여 RSS 피드를 수집하고 AI 분석을 실행합니다
3. **결과 확인**: "오늘의 브리핑" 탭에서 분석 결과를 확인합니다

## ⚠️ 주의사항

- GitHub API Rate Limit에 주의하세요 (시간당 5,000회)
- Gemini API 사용량에 따라 비용이 발생할 수 있습니다
- RSS 피드가 많을 경우 분석에 시간이 걸릴 수 있습니다

## 📄 라이선스

이 프로젝트는 자유롭게 사용 가능합니다.


