import streamlit as st
import json
from github import Github
from github.GithubException import GithubException, UnknownObjectException

class DataManager:
    def __init__(self):
        try:
            self.github_token = st.secrets["general"]["github_token"]
            self.repo_name = st.secrets["general"]["repo_name"]
        except KeyError as e:
            st.error(f"필수 설정이 누락되었습니다: {e}")
            st.stop()
        
        try:
            self.g = Github(self.github_token)
            self.repo = self.g.get_repo(self.repo_name)
        except GithubException as e:
            st.error(f"GitHub 연결 실패: {e}")
            st.stop()

    def load_json(self, file_path, default_value=None):
        """GitHub에서 JSON 파일을 읽어옵니다. 없으면 기본값을 반환."""
        try:
            contents = self.repo.get_contents(file_path)
            return json.loads(contents.decoded_content.decode())
        except UnknownObjectException:
            # 파일이 없으면 기본값 반환
            return default_value if default_value is not None else {}
        except json.JSONDecodeError as e:
            st.warning(f"JSON 파싱 오류 ({file_path}): {e}")
            return default_value if default_value is not None else {}
        except GithubException as e:
            st.error(f"GitHub API 오류: {e}")
            return default_value if default_value is not None else {}

    def save_json(self, file_path, data, commit_message):
        """데이터를 JSON으로 변환하여 GitHub에 커밋합니다."""
        try:
            content = json.dumps(data, indent=4, ensure_ascii=False)
            content_bytes = content.encode('utf-8')
            
            try:
                # 파일이 존재하면 업데이트
                file = self.repo.get_contents(file_path)
                self.repo.update_file(file.path, commit_message, content_bytes, file.sha)
            except UnknownObjectException:
                # 파일이 없으면 생성
                self.repo.create_file(file_path, commit_message, content_bytes)
            
            return True
        except GithubException as e:
            st.error(f"저장 실패: {e}")
            return False
        except Exception as e:
            st.error(f"예상치 못한 오류: {e}")
            return False


