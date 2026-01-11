"""
GitHub 릴리즈 기반 자동 업데이트 템플릿
==================================

사용 가이드:
1. 환경 설정:
   - GITHUB_OWNER, GITHUB_REPO 환경변수 설정 또는 아래 변수 직접 수정
   - 필요한 의존성 패키지: requests

2. 새 프로젝트 적용 방법:
   - 이 파일과 release_updater.py 파일을 프로젝트에 복사
   - owner, repo 변수를 프로젝트에 맞게 수정
   - run_program() 함수만 실제 프로젝트 코드로 교체
   
3. 확장 방법:
   - 추가 설정이 필요하면 환경변수나 설정 파일로 분리
   - 로깅 기능 추가 고려
   - CLI 인자 처리 추가 가능 (--skip-update 등)

이 템플릿은 기본 구조를 유지하면서 run_program() 함수만 수정하여
다양한 프로젝트에 일관된 자동 업데이트 기능을 제공합니다.
"""

import os
from release_updater import ReleaseUpdater

# 환경 변수나 설정 파일에서 값 읽기
owner = os.environ.get("GITHUB_OWNER", "bnam91")
repo = os.environ.get("GITHUB_REPO", "PrimelogicBot")

def main():
    try:
        updater = ReleaseUpdater(owner=owner, repo=repo)
        update_success = updater.update_to_latest()
        
        if update_success:
            print("프로그램을 실행합니다...")
        else:
            print("업데이트 실패, 이전 버전으로 계속 진행합니다...")
        
        # 업데이트 결과와 상관없이 실행되는 코드
        run_program()
        
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        # 중요한 예외는 로깅하거나 오류 보고 시스템에 전송할 수 있음

def run_program():
    # 실제 프로그램 코드를 별도 함수로 분리
    print("Hello, GitHub!")

if __name__ == "__main__":
    main() 