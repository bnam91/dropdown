import sys
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import requests
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO

class NaverShoppingDownloader:
    def __init__(self, url):
        self.url = url
        
    def start_browser(self):
        # Selenium 설정
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument("disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        driver = webdriver.Chrome(options=options)
        
        # 먼저 네이버로 이동
        driver.get("https://www.naver.com")
        time.sleep(random.uniform(2, 3))
        
        # 상품 페이지로 이동
        driver.get(self.url)
        time.sleep(random.uniform(2, 3))
        
        return driver
    
    def resize_image(self, image, target_width):
        # 이미지의 가로 세로 비율을 유지하면서 가로 너비 조정
        width, height = image.size
        aspect_ratio = height / width
        new_height = int(target_width * aspect_ratio)
        return image.resize((target_width, new_height), Image.Resampling.LANCZOS)
    
    def download_images(self, driver, save_path, gif_as_original=False):
        # 이미지 요소들 찾기
        images = driver.find_elements(By.CSS_SELECTOR, 'img.se-image-resource')
        
        # 저장 폴더 생성
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        downloaded_count = 0
        target_width = 860  # 목표 가로 너비
        
        for index, img in enumerate(images):
            try:
                # 이미지 URL 가져오기 (data-src 또는 src 속성에서)
                img_url = img.get_attribute('data-src')
                if not img_url:
                    img_url = img.get_attribute('src')
                
                # base64 이미지는 건너뛰기
                if img_url.startswith('data:image'):
                    continue
                    
                # 이미지 다운로드
                response = requests.get(img_url)
                if response.status_code == 200:
                    # Content-Type 확인
                    content_type = response.headers.get('Content-Type', '').lower()
                    is_gif = 'gif' in content_type or img_url.lower().endswith('.gif')
                    
                    # GIF 처리 방식 선택
                    if is_gif and gif_as_original:
                        # GIF를 원본 그대로 다운로드
                        file_name = f'image_{index + 1}.gif'
                        file_path = os.path.join(save_path, file_name)
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        downloaded_count += 1
                        print(f'GIF 다운로드 완료: {file_name} (원본)')
                    else:
                        # 기존 방식: 이미지를 PIL로 열어서 처리 (GIF는 첫 프레임만 캡쳐됨)
                        image = Image.open(BytesIO(response.content))
                        
                        # 이미지가 RGB가 아닌 경우 RGB로 변환
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        
                        # 이미지 리사이징
                        resized_image = self.resize_image(image, target_width)
                        
                        # 파일 확장자 설정
                        file_name = f'image_{index + 1}.jpg'  # JPG 형식으로 통일
                        file_path = os.path.join(save_path, file_name)
                        
                        # 리사이즈된 이미지 저장
                        resized_image.save(file_path, 'JPEG', quality=95)
                        downloaded_count += 1
                        if is_gif:
                            print(f'이미지 다운로드 완료: {file_name} (GIF 첫 프레임 캡쳐, 크기: {target_width}x{resized_image.size[1]})')
                        else:
                            print(f'이미지 다운로드 완료: {file_name} (크기: {target_width}x{resized_image.size[1]})')
                    
            except Exception as e:
                print(f'이미지 다운로드 실패 ({index + 1}): {str(e)}')
                
        return downloaded_count

class NaverShoppingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('네이버 쇼핑 다운로더')
        self.root.geometry('500x400')
        
        self.initUI()
    
    def initUI(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 상품 링크 입력
        ttk.Label(main_frame, text="상품 링크:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_input = ttk.Entry(main_frame, width=50)
        self.url_input.grid(row=0, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 저장 경로
        ttk.Label(main_frame, text="저장 경로:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.path_input = ttk.Entry(main_frame, width=40)
        self.path_input.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="선택", command=self.select_path).grid(row=1, column=3, pady=5)
        
        # GIF 처리 방식 선택
        gif_frame = ttk.LabelFrame(main_frame, text="GIF 처리 방식", padding="5")
        gif_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        self.gif_mode = tk.StringVar(value="capture")  # 기본값: 캡쳐 모드
        ttk.Radiobutton(gif_frame, text="GIF 첫 프레임 캡쳐 (JPG로 저장)", 
                       variable=self.gif_mode, value="capture").grid(row=0, column=0, sticky=tk.W, padx=5)
        ttk.Radiobutton(gif_frame, text="GIF 원본 다운로드 (GIF로 저장)", 
                       variable=self.gif_mode, value="original").grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # 실행 버튼과 폴더 열기 버튼
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        self.run_button = ttk.Button(button_frame, text="실행", command=self.run_downloader)
        self.run_button.grid(row=0, column=0, padx=(0, 10))
        
        self.open_folder_button = ttk.Button(button_frame, text="폴더 열기", command=self.open_folder)
        self.open_folder_button.grid(row=0, column=1)
        
        # 로그 출력
        ttk.Label(main_frame, text="로그:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=60)
        self.log_text.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def select_path(self):
        folder_path = filedialog.askdirectory(title="저장 경로 선택")
        if folder_path:
            self.path_input.delete(0, tk.END)
            self.path_input.insert(0, folder_path)
    
    def open_folder(self):
        folder_path = self.path_input.get()
        if not folder_path:
            messagebox.showerror("오류", "먼저 저장 경로를 선택해주세요.")
            return
            
        if not os.path.exists(folder_path):
            messagebox.showerror("오류", "선택된 경로가 존재하지 않습니다.")
            return
            
        try:
            # Windows에서 폴더 열기
            os.startfile(folder_path)
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 열 수 없습니다: {str(e)}")
    
    def update_log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_downloader(self):
        # 입력값 가져오기
        input_url = self.url_input.get()
        save_path = self.path_input.get()
        
        if not input_url:
            messagebox.showerror("오류", "상품 링크를 입력해주세요.")
            return
            
        if not save_path:
            messagebox.showerror("오류", "저장 경로를 선택해주세요.")
            return
        
        try:
            # 다운로더 실행
            downloader = NaverShoppingDownloader(input_url)
            driver = downloader.start_browser()
            self.update_log("브라우저가 실행되었습니다.")
            self.update_log(f"URL로 이동했습니다: {input_url}")
            
            # GIF 처리 방식 가져오기
            gif_as_original = (self.gif_mode.get() == "original")
            if gif_as_original:
                self.update_log("GIF 처리 방식: 원본 다운로드")
            else:
                self.update_log("GIF 처리 방식: 첫 프레임 캡쳐")
            
            # 이미지 다운로드 (재시도 로직 포함)
            max_retries = 3
            retry_count = 0
            downloaded_count = 0
            
            while retry_count < max_retries:
                downloaded_count = downloader.download_images(driver, save_path, gif_as_original)
                self.update_log(f"총 {downloaded_count}개의 이미지를 다운로드했습니다.")
                
                if downloaded_count > 0:
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        self.update_log(f"이미지가 0개입니다. 10초 후 재시도합니다... (시도 {retry_count}/{max_retries})")
                        time.sleep(10)
                        # 페이지 새로고침
                        driver.refresh()
                        time.sleep(random.uniform(2, 3))
                    else:
                        self.update_log("최대 재시도 횟수에 도달했습니다. 이미지 다운로드를 중단합니다.")
            
            # 완료 메시지
            if downloaded_count > 0:
                messagebox.showinfo("완료", f"이미지 다운로드가 완료되었습니다.\n총 {downloaded_count}개의 이미지가 저장되었습니다.")
            else:
                messagebox.showwarning("경고", "이미지를 다운로드할 수 없습니다. 페이지를 확인해주세요.")
            
        except Exception as e:
            self.update_log(f"오류 발생: {str(e)}")
            messagebox.showerror("오류", f"실행 중 오류가 발생했습니다: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    app = NaverShoppingGUI(root)
    root.mainloop()
