import pandas as pd
import os
import shutil
from pathlib import Path

def classify_reviews(source_folder_path):
    """
    리뷰 데이터를 분류하는 함수 - 이미지 파일 기반 분류
    
    Args:
        source_folder_path (str): Excel 파일과 이미지 파일들이 있는 폴더 경로
    """
    # 입력된 폴더 경로에서 Excel 파일과 이미지 파일들을 찾기
    source_folder = Path(source_folder_path)
    
    # Excel 파일 찾기 (reviews_chunk_1.xlsx)
    excel_files = list(source_folder.glob("reviews_chunk_1.xlsx"))
    excel_data = {}
    
    if excel_files:
        excel_path = excel_files[0]
        print(f"Excel 파일 발견: {excel_path}")
        
        try:
            # Excel 파일 읽기
            df = pd.read_excel(excel_path)
            
            print("Excel 파일 구조:")
            print(df.columns.tolist())
            print(f"총 {len(df)} 개의 행이 있습니다.")
            
            # Excel 데이터를 딕셔너리로 저장 (A열을 키로, G열을 값으로)
            if len(df.columns) >= 7:
                for idx, row in df.iterrows():
                    page_id = str(row.iloc[0])  # A열 값
                    content = str(row.iloc[6])  # G열 값
                    excel_data[page_id] = content
                    
        except Exception as e:
            print(f"Excel 파일 읽기 오류: {e}")
    else:
        print("Excel 파일이 없습니다. 이미지 파일만으로 분류를 진행합니다.")
    
    # 이미지 파일들이 있는 폴더 경로
    image_folder = source_folder
    
    # 결과를 저장할 폴더 경로 ({선택한 폴더명}_분류)
    folder_name = source_folder.name
    output_folder = source_folder.parent / f"{folder_name}_분류"
    
    try:
        # 모든 이미지 파일의 페이지_리뷰번호 조합 찾기
        print("\n이미지 파일 스캔 중...")
        combinations = get_all_image_combinations(image_folder)
        
        print(f"발견된 페이지_리뷰번호 조합: {len(combinations)}개")
        print(f"조합 예시: {list(combinations)[:10]}")  # 처음 10개만 표시
        
        # 출력 폴더 생성
        os.makedirs(output_folder, exist_ok=True)
        
        # 각 조합에 대해 폴더 생성 및 파일 복사
        for combination in sorted(combinations):
            # 폴더 생성
            folder_path = os.path.join(output_folder, combination)
            os.makedirs(folder_path, exist_ok=True)
            
            # txt 파일 생성 (Excel 데이터가 있으면 사용, 없으면 기본 텍스트)
            txt_file_path = os.path.join(folder_path, f"{combination}.txt")
            content = excel_data.get(combination, f"리뷰 ID: {combination}")
            
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"폴더 생성: {combination}, txt 파일 생성: {combination}.txt")
            
            # 해당하는 이미지 파일들 찾기 및 복사
            copy_matching_images(combination, image_folder, folder_path)
            
    except Exception as e:
        print(f"오류 발생: {e}")

def get_all_image_combinations(image_folder):
    """모든 이미지 파일을 스캔하여 페이지_리뷰번호 조합을 찾기"""
    combinations = set()
    source_path = Path(image_folder)
    
    # review_pageX_Y_photo_Z.jpg 패턴의 모든 파일 찾기
    all_image_files = list(source_path.glob("review_page*_*_photo_*.jpg"))
    
    for img_file in all_image_files:
        # 파일명에서 페이지 번호와 리뷰 번호 추출
        # review_page1_2_photo_1.jpg -> page=1, review=2
        try:
            filename = img_file.stem  # 확장자 제거
            parts = filename.split('_')
            if len(parts) >= 4 and parts[0] == 'review' and parts[1].startswith('page'):
                page_num = parts[1].replace('page', '')
                review_num = parts[2]
                combination = f"{page_num}_{review_num}"
                combinations.add(combination)
        except:
            continue
    
    return combinations

def copy_matching_images(page_id, image_folder, target_folder):
    """해당 page_id와 일치하는 이미지 파일들을 찾아서 복사"""
    try:
        # page_id가 "X_Y" 형태라고 가정 (예: "1_1", "1_2" 등)
        if '_' in str(page_id):
            # 이미 페이지_리뷰 형태인 경우
            page_review_id = str(page_id)
        else:
            # 단순 숫자인 경우, 모든 페이지에서 해당 리뷰 번호를 찾기
            review_num = str(page_id)
            source_path = Path(image_folder)
            all_files = list(source_path.glob(f"review_page*_{review_num}_photo_*.jpg"))
            
            print(f"  {page_id}에 해당하는 이미지 파일 {len(all_files)}개 발견:")
            for img_file in all_files:
                target_path = os.path.join(target_folder, img_file.name)
                shutil.copy2(img_file, target_path)
                print(f"    복사됨: {img_file.name}")
            return
        
        # page_review_id 형태 처리 (예: "1_2" -> page=1, review=2)
        try:
            page_num, review_num = page_review_id.split('_')
            pattern = f"review_page{page_num}_{review_num}_photo_*.jpg"
            
            source_path = Path(image_folder)
            matching_files = list(source_path.glob(pattern))
            
            print(f"  {page_id}에 해당하는 이미지 파일 {len(matching_files)}개 발견 (패턴: {pattern}):")
            for img_file in matching_files:
                target_path = os.path.join(target_folder, img_file.name)
                shutil.copy2(img_file, target_path)
                print(f"    복사됨: {img_file.name}")
            
            # 디버깅 정보
            if len(matching_files) == 0:
                print(f"    디버깅: {source_path}에서 패턴 '{pattern}'으로 검색했지만 파일을 찾지 못했습니다.")
                
        except ValueError:
            print(f"    잘못된 page_id 형식: {page_id}")
                
    except Exception as e:
        print(f"이미지 복사 중 오류 발생 ({page_id}): {e}")

if __name__ == "__main__":
    # 사용자로부터 폴더 경로 입력받기
    print("리뷰 분류 프로그램")
    print("=" * 50)
    
    # 기본 경로 설정 (현재 작업 디렉토리 기준)
    base_path = r"C:\Users\신현빈\Desktop\github\naver_review_crawl"
    
    print(f"기본 경로: {base_path}")
    print("사용 가능한 폴더들:")
    
    # 사용 가능한 폴더들 표시
    available_folders = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            # reviews_chunk_1.xlsx 파일이 있는지 확인
            excel_file = os.path.join(item_path, "reviews_chunk_1.xlsx")
            if os.path.exists(excel_file):
                available_folders.append(item)
                print(f"  - {item} (Excel 파일 있음)")
    
    if not available_folders:
        print("사용 가능한 폴더가 없습니다.")
        print("reviews_chunk_1.xlsx 파일이 있는 폴더를 확인해주세요.")
        exit()
    
    print("\n폴더를 선택하세요:")
    for i, folder in enumerate(available_folders, 1):
        print(f"{i}. {folder}")
    
    try:
        choice = int(input("\n선택 (번호 입력): ")) - 1
        if 0 <= choice < len(available_folders):
            selected_folder = available_folders[choice]
            source_folder_path = os.path.join(base_path, selected_folder)
            
            print(f"\n선택된 폴더: {selected_folder}")
            print(f"분류 시작...")
            
            classify_reviews(source_folder_path)
        else:
            print("잘못된 선택입니다.")
    except ValueError:
        print("숫자를 입력해주세요.")
    except KeyboardInterrupt:
        print("\n프로그램이 중단되었습니다.")
