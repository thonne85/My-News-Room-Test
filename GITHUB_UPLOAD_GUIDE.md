# GitHub 업로드 가이드

## 방법 1: Git 명령어 사용 (권장)

### 1단계: Git 설치
- https://git-scm.com/download/win 에서 Git for Windows 다운로드 및 설치

### 2단계: GitHub 리포지토리 생성
1. https://github.com 에서 로그인
2. 우측 상단 `+` 버튼 > `New repository` 클릭
3. Repository name 입력 (예: `my-newsroom`)
4. Public 또는 Private 선택
5. **"Initialize this repository with a README" 체크 해제** (이미 README.md가 있으므로)
6. `Create repository` 클릭

### 3단계: 로컬에서 Git 초기화 및 푸시

터미널(또는 PowerShell)에서 프로젝트 폴더로 이동 후:

```bash
# Git 초기화
git init

# 모든 파일 추가 (secrets.toml은 .gitignore에 의해 제외됨)
git add .

# 첫 커밋
git commit -m "Initial commit: Streamlit Newsroom with GitHub integration"

# GitHub 리포지토리 연결 (본인의 리포지토리 URL로 변경)
git remote add origin https://github.com/사용자명/리포지토리명.git

# 메인 브랜치 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

---

## 방법 2: GitHub Desktop 사용 (GUI 방식)

### 1단계: GitHub Desktop 설치
- https://desktop.github.com/ 에서 다운로드 및 설치

### 2단계: 리포지토리 생성 및 업로드
1. GitHub Desktop 실행
2. `File` > `Add Local Repository` 클릭
3. 프로젝트 폴더 선택 (`C:\My NEWS Room`)
4. `Publish repository` 버튼 클릭
5. Repository name 입력
6. `Publish repository` 클릭

---

## 방법 3: GitHub 웹사이트에서 직접 업로드

### 1단계: 리포지토리 생성
1. GitHub에서 새 리포지토리 생성
2. `Add file` > `Upload files` 클릭

### 2단계: 파일 업로드
1. 프로젝트 폴더의 모든 파일을 드래그 앤 드롭
2. **주의**: `.streamlit/secrets.toml`은 업로드하지 마세요! (민감한 정보 포함)
3. `Commit changes` 클릭

---

## ⚠️ 중요: 업로드 전 확인사항

### 업로드하면 안 되는 파일
- ✅ `.streamlit/secrets.toml` - 이미 .gitignore에 포함됨
- ✅ `__pycache__/` 폴더
- ✅ `venv/` 또는 `env/` 폴더

### 반드시 업로드해야 하는 파일
- ✅ `app.py`
- ✅ `data_manager.py`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `.gitignore`
- ✅ `data/` 폴더의 JSON 파일들 (초기 데이터)

---

## Streamlit Cloud 배포 시 Secrets 설정

GitHub에 푸시한 후:
1. Streamlit Cloud (https://share.streamlit.io/) 접속
2. 리포지토리 연결
3. **Advanced Settings** > **Secrets**에 다음 내용 입력:

```toml
[general]
github_token = "여기에_실제_깃허브_토큰"
repo_name = "사용자명/리포지토리명"
gemini_api_key = "여기에_실제_제미나이_키"
```

---

## 문제 해결

### Git이 인식되지 않는 경우
- Git 설치 확인: https://git-scm.com/download/win
- PowerShell 재시작
- 또는 GitHub Desktop 사용

### 푸시 권한 오류
- GitHub Personal Access Token 사용 필요
- Settings > Developer settings > Personal access tokens


