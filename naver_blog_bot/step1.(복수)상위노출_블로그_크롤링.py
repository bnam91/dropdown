import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

class NaverBlogScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("Naver Blog Scraper")
        self.root.geometry("500x220")
        self.root.resizable(False, False)
        
        self.filename = None
        self.keywords = None
        self.num_posts = tk.IntVar(value=10)
        self.product_name = tk.StringVar()
        
        self.create_widgets()
    
    def create_widgets(self):
        # File selection frame
        file_frame = ttk.Frame(self.root, padding=10)
        file_frame.pack(fill=tk.X)
        
        ttk.Button(file_frame, text="검색어가 포함된 엑셀 파일 선택", command=self.select_file).pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(file_frame, text="파일을 선택하세요")
        self.file_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Product name input frame
        product_frame = ttk.Frame(self.root, padding=10)
        product_frame.pack(fill=tk.X)
        
        ttk.Label(product_frame, text="진행 상품명:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(product_frame, textvariable=self.product_name, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Post count selection frame
        count_frame = ttk.Frame(self.root, padding=10)
        count_frame.pack(fill=tk.X)
        
        ttk.Label(count_frame, text="가져올 글의 수를 선택하세요:").pack(side=tk.LEFT, padx=5)
        
        for count in [10, 20, 30, 50]:
            ttk.Radiobutton(
                count_frame, 
                text=f"{count}개", 
                variable=self.num_posts, 
                value=count
            ).pack(side=tk.LEFT, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(self.root, padding=10)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Start", command=self.start_scraping).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.root.destroy).pack(side=tk.LEFT, padx=5)
    
    def select_file(self):
        self.filename = filedialog.askopenfilename(
            title="검색어가 포함된 엑셀 파일을 선택하세요",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        
        if self.filename:
            self.file_label.config(text=self.filename)
            # 검색어 목록 불러오기
            try:
                df_keywords = pd.read_excel(self.filename, usecols='B')  # B열만 불러온다고 가정
                self.keywords = df_keywords.iloc[1:].squeeze().tolist()  # 첫 번째 행(헤더)를 제외하고 리스트로 변환
            except Exception as e:
                messagebox.showerror("Error", f"파일을 읽는 중 오류가 발생했습니다: {str(e)}")
                self.keywords = None
    
    def start_scraping(self):
        if not self.filename or not self.keywords:
            messagebox.showerror("Error", "유효한 파일을 선택하세요.")
            return
        
        if not self.product_name.get().strip():
            messagebox.showerror("Error", "진행 상품명을 입력하세요.")
            return
            
        # 선택된 글의 수 파악
        num_posts = self.num_posts.get()
        
        # 직접 스크래핑 실행 (별도의 진행 팝업 없음)
        self.perform_scraping(num_posts)
    
    def perform_scraping(self, num_posts):
        try:
            options = Options()
            options.headless = False
            driver = webdriver.Chrome(options=options)
            
            wb = Workbook()
            ws = wb.active
            
            # 헤더 추가
            ws.append(["검색어", "작성자", "제목", "날짜", "URL", "이메일"])
            
            for search_query in self.keywords:
                # 상태 표시만 창 타이틀에 보여줌
                self.root.title(f"'{search_query}' 데이터 수집 중...")
                
                driver.get("https://www.naver.com")
                time.sleep(1)
                
                driver.find_element(By.ID, "query").send_keys(search_query)
                driver.find_element(By.ID, "search-btn").click()
                time.sleep(1)
                
                driver.find_element(By.LINK_TEXT, "블로그").click()
                time.sleep(2)
                
                html = BeautifulSoup(driver.page_source, 'html.parser')
                title_links = html.find_all('a', class_='title_link', limit=num_posts)
                name_links = html.find_all('a', class_='name', limit=num_posts)
                date_links = html.find_all('span', class_='sub', limit=num_posts)
                
                data = []
                for name_link, title_link, date_link in zip(name_links, title_links, date_links):
                    url = title_link['href']
                    email = ''
                    if "https://blog.naver.com/" in url:
                        username = url.split('/')[3]
                        email = f"{username}@naver.com"
                    elif "https://adcr.naver.com/" in url:
                        email = "파워콘텐츠"
                    elif "https://post.naver.com/" in url:
                        email = "포스트"
                    
                    data.append((search_query, name_link.text.strip(), title_link.text.strip(), date_link.text.strip(), url, email))
                
                for row in data:
                    ws.append(row)
            
            driver.quit()
            
            # 현재 날짜와 상품명으로 파일명 생성
            today_date = datetime.now().strftime('%y%m%d')
            product_name = self.product_name.get().strip()
            folder_name = f"{today_date}_{product_name}_복수키워드"
            file_name = f"{today_date}_{product_name}_복수키워드.xlsx"
            
            # 현재 실행 파일이 있는 디렉토리에 폴더 생성
            current_dir = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(current_dir, folder_name)
            
            # 폴더가 없으면 생성
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            # 파일 저장 경로
            save_path = os.path.join(folder_path, file_name)
            
            wb.save(save_path)
            messagebox.showinfo("저장 완료", f"{save_path} 파일이 저장되었습니다.")
            
            # 창 제목 원래대로 복구
            self.root.title("Naver Blog Scraper")
            
        except Exception as e:
            messagebox.showerror("Error", f"데이터 수집 중 오류가 발생했습니다: {str(e)}")
            # 창 제목 원래대로 복구
            self.root.title("Naver Blog Scraper")

if __name__ == "__main__":
    root = tk.Tk()
    app = NaverBlogScraper(root)
    root.mainloop()