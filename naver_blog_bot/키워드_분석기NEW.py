"""
# 네이버 블로그 키워드 분석기
# 수집 데이터:
# 1. 구글 스프레드시트의 A열에서 분석할 키워드 목록을 읽음
# 2. B열: 검색량 데이터 (수동 입력 필요)
# 3. C열: 최근 1달 이내 작성된 블로그 게시글 수
# 4. D열: 경쟁강도 = (최근 게시글 수 / 검색량) * 1000
# 5. F열: 네이버 블로그 검색 결과 URL
#
# 분석 방법:
# - 각 키워드별로 상위 25개 블로그 게시글 분석
# - 게시글 날짜 정보 수집 (상대적 시간 표현도 실제 날짜로 변환)
# - 최근 1달 이내 게시글 수를 기반으로 경쟁강도 계산
#
# 사용법:
# 1. A열에 분석할 키워드 목록 입력
# 2. B열에 각 키워드의 검색량 데이터 입력
# 3. 프로그램 실행하면 C, D, F열에 자동으로 데이터가 입력됨
"""

import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import re
import gspread
from dotenv import load_dotenv
from auth import get_credentials

# .env 파일 로드
load_dotenv()

class BlogAnalyzer:
    def __init__(self):
        # 구글 시트 설정
        self.spreadsheet_id = "1v2S0qPAP98RsZi_5B1Q33ey-5gUDZdXpPcUK3mWtYQo"
        self.sheet_name = "유다모"
        
    def set_column_format(self, worksheet):
        """F열의 서식을 설정"""
        # F열의 너비를 설정하고 텍스트 오버플로우를 CLIP으로 설정
        worksheet.columns_auto_resize(5, 5)  # F열(인덱스 5)
        worksheet.format("F2:F1000", {
            "wrapStrategy": "CLIP",
            "verticalAlignment": "TOP"
        })

    def is_valid_date_format(self, date_text):
        """날짜 형식인지 확인"""
        # YYYY.MM.DD. 또는 YYYY.MM.DD 형식 확인
        if len(date_text) >= 8 and (date_text.count('.') >= 2 or date_text.count('-') >= 2):
            return True
        
        # 상대적 시간 표현 확인
        relative_pattern = r'(\d+)\s*(시간|일|주|개월|년)\s*전'
        if re.search(relative_pattern, date_text):
            return True
        
        return False

    def convert_relative_time_to_date(self, relative_time):
        """상대적 시간 표현을 실제 날짜로 변환"""
        try:
            now = datetime.now()
            
            # 정규표현식으로 숫자와 단위 추출
            pattern = r'(\d+)\s*(시간|일|주|개월|년)\s*전'
            match = re.search(pattern, relative_time)
            
            if match:
                number = int(match.group(1))
                unit = match.group(2)
                
                if unit == '시간':
                    return (now - timedelta(hours=number)).strftime('%Y.%m.%d.')
                elif unit == '일':
                    return (now - timedelta(days=number)).strftime('%Y.%m.%d.')
                elif unit == '주':
                    return (now - timedelta(weeks=number)).strftime('%Y.%m.%d.')
                elif unit == '개월':
                    # 개월은 대략적으로 30일로 계산
                    return (now - timedelta(days=number*30)).strftime('%Y.%m.%d.')
                elif unit == '년':
                    # 년은 대략적으로 365일로 계산
                    return (now - timedelta(days=number*365)).strftime('%Y.%m.%d.')
            
            return relative_time  # 변환할 수 없는 경우 원본 반환
            
        except Exception as e:
            print(f"날짜 변환 중 오류: {str(e)}")
            return relative_time

    def parse_date_for_comparison(self, date_str):
        """날짜 문자열을 비교 가능한 datetime 객체로 변환"""
        try:
            # YYYY.MM.DD. 형식 파싱
            if date_str.endswith('.'):
                date_str = date_str[:-1]  # 마지막 점 제거
            
            # 점을 하이픈으로 변경하여 파싱
            date_str = date_str.replace('.', '-')
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            # 파싱할 수 없는 경우 현재 날짜 반환
            return datetime.now()

    def analyze_blogs(self):
        try:
            # 구글 시트 클라이언트 생성
            creds = get_credentials()
            client = gspread.authorize(creds)
            
            # 스프레드시트 열기
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet(self.sheet_name)
            
            # F열 서식 설정
            self.set_column_format(worksheet)
            
            # 키워드 읽기 (A열)
            keywords = worksheet.col_values(1)[1:]  # 헤더 제외
            
            # Chrome 옵션 설정
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument("--start-maximized")
            
            # Chrome WebDriver 설정
            driver = webdriver.Chrome(options=options)
            
            # 각 키워드에 대해 분석
            for idx, keyword in enumerate(keywords, start=2):  # start=2는 헤더를 제외하고 시작
                if not keyword.strip():  # 빈 키워드 건너뛰기
                    continue
                    
                print(f"분석 중: {keyword}")
                
                driver.get("https://www.naver.com")
                time.sleep(1)
                
                # 검색어 입력 및 검색
                driver.find_element(By.ID, "query").send_keys(keyword)
                driver.find_element(By.ID, "search-btn").click()
                time.sleep(1)
                
                # 블로그 탭으로 이동
                driver.find_element(By.LINK_TEXT, "블로그").click()
                time.sleep(2)
                
                # 현재 URL 저장 (블로그 탭 URL)
                blog_tab_url = driver.current_url
                
                # 페이지 파싱
                html = BeautifulSoup(driver.page_source, 'html.parser')
                
                # 날짜 추출
                date_links = []
                user_info_divs = html.find_all('div', class_='user_info')
                
                for user_info in user_info_divs[:25]:  # 상위 25개로 변경
                    sub_spans = user_info.find_all('span', class_='sub')
                    for span in sub_spans:
                        date_text = span.text.strip()
                        if self.is_valid_date_format(date_text):
                            date_links.append(date_text)
                            break
                
                # 1달 이내 게시글 수 계산
                one_month_ago = datetime.now() - timedelta(days=30)
                recent_posts = 0
                
                for date_text in date_links:
                    # 상대적 시간을 실제 날짜로 변환
                    actual_date = self.convert_relative_time_to_date(date_text)
                    post_date = self.parse_date_for_comparison(actual_date)
                    
                    if post_date >= one_month_ago:
                        recent_posts += 1
                
                # 결과를 C열에 업데이트
                worksheet.update_cell(idx, 3, str(recent_posts))
                
                # B열에서 검색량 읽기
                search_volume = worksheet.cell(idx, 2).value
                try:
                    # 검색량과 최근 게시글 수로 경쟁강도 계산
                    search_volume = float(search_volume) if search_volume else 0
                    if search_volume > 0:  # 0으로 나누기 방지
                        competition_rate = (recent_posts / search_volume) * 1000
                        # 소수점 2자리까지 반올림
                        competition_rate = round(competition_rate, 2)
                    else:
                        competition_rate = 0
                    
                    # 경쟁강도를 D열에 업데이트
                    worksheet.update_cell(idx, 4, str(competition_rate))
                except (ValueError, TypeError) as e:
                    print(f"경쟁강도 계산 중 오류 발생 (키워드: {keyword}): {str(e)}")
                    worksheet.update_cell(idx, 4, "0")
                
                # 블로그 탭 URL을 F열에 업데이트
                worksheet.update_cell(idx, 6, blog_tab_url)
                time.sleep(1)  # API 제한 방지
                
            driver.quit()
            print("분석 완료!")
            
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            if 'driver' in locals():
                driver.quit()

if __name__ == "__main__":
    analyzer = BlogAnalyzer()
    analyzer.analyze_blogs()
