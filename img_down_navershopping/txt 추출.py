import os
from PIL import Image
import sys
import cv2

# EasyOCR을 사용한 OCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

def extract_text_with_easyocr(image_path):
    """
    EasyOCR을 사용하여 텍스트를 추출합니다.
    """
    try:
        print("🔄 EasyOCR 모델 로딩 중... (처음 실행 시 시간이 걸릴 수 있습니다)")
        # EasyOCR 리더 초기화 (한국어, 영어)
        reader = easyocr.Reader(['ko', 'en'])
        
        print("📖 이미지에서 텍스트 읽는 중...")
        
        # PIL을 사용하여 이미지 로딩 후 numpy 배열로 변환
        pil_image = Image.open(image_path)
        # RGB로 변환 (RGBA인 경우)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # numpy 배열로 변환
        import numpy as np
        image_array = np.array(pil_image)
        
        # 텍스트 추출
        results = reader.readtext(image_array)
        
        # 결과를 문자열로 합치기
        extracted_text = '\n'.join([result[1] for result in results])
        return extracted_text.strip()
        
    except Exception as e:
        return f"❌ EasyOCR 처리 중 오류 발생: {str(e)}"

def extract_text_from_image(image_path):
    """
    이미지 파일에서 OCR을 사용하여 텍스트를 추출합니다.
    
    Args:
        image_path (str): 이미지 파일 경로
    
    Returns:
        str: 추출된 텍스트
    """
    # 이미지 파일이 존재하는지 확인
    if not os.path.exists(image_path):
        return f"❌ 오류: 파일을 찾을 수 없습니다: {image_path}"
    
    # 파일 크기 확인
    file_size = os.path.getsize(image_path)
    if file_size == 0:
        return "❌ 오류: 파일이 비어있습니다."
    
    print(f"📄 파일 크기: {file_size:,} bytes")
    
    # EasyOCR 사용
    if EASYOCR_AVAILABLE:
        return extract_text_with_easyocr(image_path)
    else:
        return "❌ EasyOCR이 설치되지 않았습니다. 'pip install easyocr'를 실행해주세요."

def main():
    # 지정된 이미지 파일 경로
    image_path = r"C:\Users\신현빈\Desktop\github\img_down_navershopping\미닉스\미닉스_더플렌더프로_250729\image_1.jpg"
    
    print("🔍 이미지에서 텍스트 추출 중...")
    print(f"📁 파일 경로: {image_path}")
    
    # 파일 존재 여부 확인
    if os.path.exists(image_path):
        print("✅ 파일 존재 확인됨")
    else:
        print("❌ 파일을 찾을 수 없습니다")
        # 대안 경로 시도
        alt_path = "미닉스/미닉스_더플렌더프로_250729/image_1.jpg"
        if os.path.exists(alt_path):
            print(f"✅ 대안 경로에서 파일 발견: {alt_path}")
            image_path = alt_path
        else:
            print("❌ 대안 경로에서도 파일을 찾을 수 없습니다")
            return
    
    # EasyOCR 사용 가능 여부 확인
    if EASYOCR_AVAILABLE:
        print("✅ EasyOCR 사용 가능")
    else:
        print("❌ EasyOCR이 설치되지 않음")
    
    print("-" * 50)
    
    # OCR 텍스트 추출
    extracted_text = extract_text_from_image(image_path)
    
    # 결과 출력
    if extracted_text.startswith("❌"):
        print(extracted_text)
        print("\n💡 해결 방법:")
        print("EasyOCR 설치: pip install easyocr")
    else:
        print("📝 추출된 텍스트:")
        print("=" * 50)
        print(extracted_text)
        print("=" * 50)
        
        # 추출된 텍스트가 비어있는지 확인
        if not extracted_text:
            print("ℹ️  추출된 텍스트가 없습니다. 이미지에 텍스트가 없거나 인식되지 않았을 수 있습니다.")

if __name__ == "__main__":
    main()
