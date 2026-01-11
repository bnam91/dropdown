import os
import hashlib
from collections import defaultdict
import shutil

def get_file_hash(filepath):
    """파일의 MD5 해시값을 계산합니다."""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def remove_duplicate_images(directory_path):
    """중복 이미지를 제거합니다."""
    print(f"'{directory_path}' 디렉토리에서 중복 이미지를 찾는 중...")
    
    # 지원하는 이미지 확장자
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    # 파일 크기별로 그룹화
    size_groups = defaultdict(list)
    
    # 디렉토리 내 모든 파일 검사
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        
        # 파일인지 확인
        if not os.path.isfile(filepath):
            continue
            
        # 이미지 파일인지 확인
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in image_extensions:
            continue
            
        # 파일 크기 가져오기
        file_size = os.path.getsize(filepath)
        size_groups[file_size].append(filepath)
    
    print(f"총 {len([f for files in size_groups.values() for f in files])}개의 이미지 파일을 찾았습니다.")
    
    # 중복 제거
    removed_count = 0
    kept_count = 0
    
    for size, files in size_groups.items():
        if len(files) > 1:
            print(f"\n크기 {size} bytes인 파일 {len(files)}개 발견:")
            
            # 해시값별로 그룹화
            hash_groups = defaultdict(list)
            for filepath in files:
                file_hash = get_file_hash(filepath)
                hash_groups[file_hash].append(filepath)
            
            # 각 해시 그룹에서 중복 제거
            for file_hash, hash_files in hash_groups.items():
                if len(hash_files) > 1:
                    print(f"  중복 파일 {len(hash_files)}개 발견 (해시: {file_hash[:8]}...)")
                    
                    # 첫 번째 파일은 유지, 나머지는 삭제
                    keep_file = hash_files[0]
                    delete_files = hash_files[1:]
                    
                    print(f"    유지: {os.path.basename(keep_file)}")
                    kept_count += 1
                    
                    for delete_file in delete_files:
                        try:
                            os.remove(delete_file)
                            print(f"    삭제: {os.path.basename(delete_file)}")
                            removed_count += 1
                        except Exception as e:
                            print(f"    삭제 실패: {os.path.basename(delete_file)} - {e}")
                else:
                    # 중복이 없는 파일
                    kept_count += 1
        else:
            # 크기가 고유한 파일
            kept_count += 1
    
    print(f"\n=== 결과 ===")
    print(f"유지된 파일: {kept_count}개")
    print(f"삭제된 파일: {removed_count}개")
    print(f"총 절약된 공간: {removed_count * 20:.2f} KB (평균 20KB/파일 기준)")

if __name__ == "__main__":
    # 대상 디렉토리 경로
    target_directory = r"C:\Users\신현빈\Desktop\github\naver_review_crawl\유다모_리뷰"
    
    # 디렉토리가 존재하는지 확인
    if not os.path.exists(target_directory):
        print(f"오류: 디렉토리 '{target_directory}'를 찾을 수 없습니다.")
    else:
        # 중복 제거 실행
        remove_duplicate_images(target_directory)
