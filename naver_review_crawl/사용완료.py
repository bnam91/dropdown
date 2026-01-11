import os
import shutil
from pathlib import Path

def remove_duplicate_photos():
    # 경로 설정
    main_folder = Path("유다모_리뷰분배_250623")
    used_folder = main_folder / "00.사용완료"
    
    # 00.사용완료 폴더의 모든 파일 목록 가져오기
    used_files = set()
    if used_folder.exists():
        for file_path in used_folder.glob("*.jpg"):
            used_files.add(file_path.name)
    
    print(f"00.사용완료 폴더에서 찾은 파일 수: {len(used_files)}")
    
    # 메인 폴더에서 중복 파일 제거
    removed_count = 0
    for file_path in main_folder.glob("*.jpg"):
        if file_path.name in used_files:
            try:
                os.remove(file_path)
                print(f"제거됨: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"제거 실패: {file_path.name} - {e}")
    
    print(f"\n총 {removed_count}개의 중복 파일이 제거되었습니다.")

if __name__ == "__main__":
    remove_duplicate_photos()
