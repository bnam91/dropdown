from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import shutil
import sys
import time
from pathlib import Path

def clear_chrome_data(user_data_dir, keep_login=True):
    default_dir = os.path.join(user_data_dir, 'Default')
    if not os.path.exists(default_dir):
        print("Default 디렉토리가 존재하지 않습니다.")
        return

    dirs_to_clear = ['Cache', 'Code Cache', 'GPUCache']
    files_to_clear = ['History', 'Visited Links', 'Web Data']
    
    for dir_name in dirs_to_clear:
        dir_path = os.path.join(default_dir, dir_name)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"{dir_name} 디렉토리를 삭제했습니다.")

    if not keep_login:
        files_to_clear.extend(['Cookies', 'Login Data'])

    for file_name in files_to_clear:
        file_path = os.path.join(default_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_name} 파일을 삭제했습니다.")





def get_available_profiles(user_data_parent):
    """사용 가능한 프로필 목록을 가져옴"""
    profiles = []
    if not os.path.exists(user_data_parent):
        os.makedirs(user_data_parent)
        return profiles
        
    for item in os.listdir(user_data_parent):
        item_path = os.path.join(user_data_parent, item)
        if os.path.isdir(item_path):
            if (os.path.exists(os.path.join(item_path, 'Default')) or 
                any(p.startswith('Profile') for p in os.listdir(item_path) if os.path.isdir(os.path.join(item_path, p)))):
                profiles.append(item)
    return profiles

def select_profile(user_data_parent):
    """사용자에게 프로필을 선택하도록 함"""
    profiles = get_available_profiles(user_data_parent)
    if not profiles:
        print("\n사용 가능한 프로필이 없습니다.")
        create_new = input("새 프로필을 생성하시겠습니까? (y/n): ").lower()
        if create_new == 'y':
            while True:
                name = input("새 프로필 이름을 입력하세요: ")
                if not name:
                    print("프로필 이름을 입력해주세요.")
                    continue
                    
                if any(c in r'\\/:*?"<>|' for c in name):
                    print("프로필 이름에 다음 문자를 사용할 수 없습니다: \\ / : * ? \" < > |")
                    continue
                    
                new_profile_path = os.path.join(user_data_parent, name)
                if os.path.exists(new_profile_path):
                    print(f"'{name}' 프로필이 이미 존재합니다.")
                    continue
                    
                try:
                    os.makedirs(new_profile_path)
                    os.makedirs(os.path.join(new_profile_path, 'Default'))
                    print(f"'{name}' 프로필이 생성되었습니다.")
                    return name
                except Exception as e:
                    print(f'프로필 생성 중 오류가 발생했습니다: {e}')
                    retry = input("다시 시도하시겠습니까? (y/n): ").lower()
                    if retry != 'y':
                        return None
        return None
        
    print("\n사용 가능한 프로필 목록:")
    for idx, profile in enumerate(profiles, 1):
        print(f"{idx}. {profile}")
    print(f"{len(profiles) + 1}. 새 프로필 생성")
        
    while True:
        try:
            choice = int(input("\n사용할 프로필 번호를 선택하세요: "))
            if 1 <= choice <= len(profiles):
                selected_profile = profiles[choice - 1]
                print(f"\n선택된 프로필: {selected_profile}")
                return selected_profile
            elif choice == len(profiles) + 1:
                # 새 프로필 생성
                while True:
                    name = input("새 프로필 이름을 입력하세요: ")
                    if not name:
                        print("프로필 이름을 입력해주세요.")
                        continue
                        
                    if any(c in r'\\/:*?"<>|' for c in name):
                        print("프로필 이름에 다음 문자를 사용할 수 없습니다: \\ / : * ? \" < > |")
                        continue
                        
                    new_profile_path = os.path.join(user_data_parent, name)
                    if os.path.exists(new_profile_path):
                        print(f"'{name}' 프로필이 이미 존재합니다.")
                        continue
                        
                    try:
                        os.makedirs(new_profile_path)
                        os.makedirs(os.path.join(new_profile_path, 'Default'))
                        print(f"'{name}' 프로필이 생성되었습니다.")
                        return name
                    except Exception as e:
                        print(f'프로필 생성 중 오류가 발생했습니다: {e}')
                        retry = input("다시 시도하시겠습니까? (y/n): ").lower()
                        if retry != 'y':
                            break
            else:
                print("유효하지 않은 번호입니다. 다시 선택해주세요.")
        except ValueError:
            print("숫자를 입력해주세요.")

def main():
    # 사용자 프로필 경로 설정
    user_data_parent = r"C:\Users\신현빈\Desktop\github\user_data_coupang"
    
    # 프로필 선택
    selected_profile = select_profile(user_data_parent)
    if not selected_profile:
        print("프로필을 선택할 수 없습니다. 프로그램을 종료합니다.")
        return
        
    user_data_dir = os.path.join(user_data_parent, selected_profile)
    
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
        os.makedirs(os.path.join(user_data_dir, 'Default'))

    # Chrome 옵션 설정
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    options.add_argument("disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument(f"user-data-dir={user_data_dir}")
    options.add_argument("--disable-application-cache")
    options.add_argument("--disable-cache")

    # 캐시와 임시 파일 정리 (로그인 정보 유지)
    clear_chrome_data(user_data_dir)

    # Chrome 드라이버 생성 및 쿠팡 윙 로그인 페이지 열기
    try:
        driver = webdriver.Chrome(options=options)
        print("Chrome 브라우저가 시작되었습니다.")
        
        # 쿠팡 윙 로그인 페이지로 이동
        print("쿠팡 윙 로그인 페이지로 이동합니다...")
        driver.get("https://xauth.coupang.com/auth/realms/seller/protocol/openid-connect/auth?response_type=code&client_id=wing&redirect_uri=https%3A%2F%2Fwing.coupang.com%2Fsso%2Flogin?returnUrl%3D%252F&state=25168410-ce5b-4a14-9b18-26264ee980ae&login=true&scope=openid")
        
        print(f"\n선택된 프로필: {selected_profile}")
        print("로그인 페이지 로딩을 기다리는 중...")
        
        # 로그인 필드가 로드될 때까지 대기
        wait = WebDriverWait(driver, 20)
        
        try:
            # 아이디 입력 필드 대기 및 입력
            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            print("아이디 입력 중...")
            username_field.clear()
            username_field.send_keys("bnam91")
            time.sleep(0.5)
            
            # 비밀번호 입력 필드 대기 및 입력
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            print("비밀번호 입력 중...")
            password_field.clear()
            password_field.send_keys("@rhdi120")
            time.sleep(0.5)
            
            # 로그인 버튼 클릭
            login_button = wait.until(EC.element_to_be_clickable((By.ID, "kc-login")))
            print("로그인 버튼 클릭 중...")
            login_button.click()
            
            print("로그인 시도가 완료되었습니다.")
            print("5초 대기 중...")
            time.sleep(5)  # 로그인 처리 대기
            
            # 지정된 링크로 이동
            target_url = "https://wing.coupang.com/vendor-inventory/list?searchKeywordType=ALL&searchKeywords=&salesMethod=ALL&productStatus=ALL&stockSearchType=ALL&shippingFeeSearchType=ALL&displayCategoryCodes=&listingStartTime=null&listingEndTime=null&saleEndDateSearchType=ALL&bundledShippingSearchType=ALL&upBundling=ALL&displayDeletedProduct=false&shippingMethod=ALL&exposureStatus=ALL&locale=ko_KR&sortMethod=SORT_BY_ITEM_LEVEL_UNIT_SOLD&countPerPage=50&page=1"
            print("재고 관리 페이지로 이동 중...")
            driver.get(target_url)
            print("페이지 이동이 완료되었습니다.")
            
        except Exception as e:
            print(f"로그인 처리 중 오류 발생: {e}")
            print("수동으로 로그인을 진행해주세요.")
        
    except Exception as e:
        print(f"Chrome 드라이버 생성 중 오류 발생: {e}")
        print("프로그램을 종료합니다.")

if __name__ == "__main__":
    main()
