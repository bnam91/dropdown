import tkinter as tk
from tkinter import ttk, scrolledtext, Radiobutton, StringVar, Toplevel, Text
import json
import os
from dotenv import load_dotenv
import openai
import pyperclip  # 클립보드 복사를 위한 라이브러리
import threading  # 백그라운드 처리를 위한 스레딩
import datetime  # 날짜 정보를 위한 모듈 추가

# .env 파일에서 API 키 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI 클라이언트 설정
openai.api_key = OPENAI_API_KEY

def 텍스트_분석(배송정보, 쇼핑몰):
    try:
        # GPT-4o-mini를 사용하여 배송 정보 분석
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"당신은 배송 정보에서 주요 데이터를 추출하는 분석가입니다. 다음 텍스트에서 택배사(없으면 '정보없음'), 송장번호(없으면 '정보없음'), 주문자명, 연락처, 배송지, 상품주문번호(없으면 '정보없음'), 상품명(없으면 '정보없음')을 추출해 JSON 형식으로 반환하세요. 이 정보는 {쇼핑몰}에서 주문한 상품입니다."},
                {"role": "user", "content": 배송정보}
            ],
            response_format={"type": "json_object"}
        )
        
        # 토큰 사용량 계산
        입력_토큰 = response.usage.prompt_tokens
        출력_토큰 = response.usage.completion_tokens
        총_토큰 = response.usage.total_tokens
        
        # 가격 계산 (OpenAI 공식 가격 기준)
        달러당_원화 = 1350  # 달러 당 원화 환율 (변동 가능)
        입력_가격_달러 = 입력_토큰 * (0.15 / 1000000)  # $0.15 / 1M tokens
        출력_가격_달러 = 출력_토큰 * (0.60 / 1000000)  # $0.60 / 1M tokens
        총_가격_달러 = 입력_가격_달러 + 출력_가격_달러
        총_가격_원화 = 총_가격_달러 * 달러당_원화
        
        # JSON 형식으로 파싱
        결과 = response.choices[0].message.content
        파싱된_결과 = json.loads(결과)
        파싱된_결과["쇼핑몰"] = 쇼핑몰  # 선택한 쇼핑몰 정보 추가
        
        # 토큰 사용량 및 비용 정보 추가
        파싱된_결과["API_정보"] = {
            "입력_토큰": 입력_토큰,
            "출력_토큰": 출력_토큰,
            "총_토큰": 총_토큰,
            "비용_원화": round(총_가격_원화, 1)  # 소수점 첫째 자리까지 반올림
        }
        
        return 파싱된_결과
    
    except Exception as e:
        return {"오류": str(e), "택배사": "정보없음", "송장번호": "정보없음", "주문자": "정보없음", "연락처": "정보없음", "배송지": "정보없음", "상품주문번호": "정보없음", "상품명": "정보없음", "쇼핑몰": 쇼핑몰}

def json_to_kakao_format(json_data):
    """JSON 데이터를 카카오톡 형식의 텍스트로 변환 (요청된 순서대로)"""
    return f"""[반품정보]
쇼핑몰: {json_data.get('쇼핑몰', '정보없음')}
상품명: {json_data.get('상품명', '정보없음')}
주문번호: {json_data.get('상품주문번호', '정보없음')}
택배사: {json_data.get('택배사', '정보없음')}
송장번호: {json_data.get('송장번호', '정보없음')}
주문자: {json_data.get('주문자명', json_data.get('주문자', '정보없음'))}
연락처: {json_data.get('연락처', '정보없음')}
배송지: {json_data.get('배송지', '정보없음')}
"""

def json_to_text_format(json_data):
    """JSON 데이터를 읽기 쉬운 텍스트 형식으로 변환"""
    return f"""쇼핑몰: {json_data.get('쇼핑몰', '정보없음')}
상품명: {json_data.get('상품명', '정보없음')}
주문번호: {json_data.get('상품주문번호', '정보없음')}
택배사: {json_data.get('택배사', '정보없음')}
송장번호: {json_data.get('송장번호', '정보없음')}
주문자: {json_data.get('주문자명', json_data.get('주문자', '정보없음'))}
연락처: {json_data.get('연락처', '정보없음')}
배송지: {json_data.get('배송지', '정보없음')}
"""

def 반품처리_프레임_생성(부모_프레임):
    """반품처리 UI를 별도의 창이 아닌 프레임 형태로 생성"""
    # 상단 버튼 프레임
    버튼_프레임 = tk.Frame(부모_프레임)
    버튼_프레임.pack(fill='x', pady=10)
    
    # 반품 추가하기 버튼
    추가_버튼 = tk.Button(버튼_프레임, text="반품 추가하기", 
                      width=16, height=1, font=("맑은 고딕", 10))
    추가_버튼.pack(side=tk.LEFT, padx=15, pady=5)
    
    # 모든 반품정보 복사 버튼
    모든정보_복사_버튼 = tk.Button(버튼_프레임, text="카톡으로 변환하기", 
                            width=20, height=1, font=("맑은 고딕", 10))
    모든정보_복사_버튼.pack(side=tk.LEFT, padx=15, pady=5)
    
    # 탭 컨트롤 생성
    탭_컨트롤 = ttk.Notebook(부모_프레임)
    탭_컨트롤.pack(fill='both', expand=True, padx=10, pady=5)
    
    # 탭 카운터 및 탭 목록 관리
    탭_카운터 = 1
    탭_목록 = []
    
    def 탭_추가():
        nonlocal 탭_카운터
        탭_생성(f"반품 #{탭_카운터}")
        탭_카운터 += 1
    
    def 탭_생성(탭_이름):
        # 새 탭 프레임 생성
        탭_프레임 = ttk.Frame(탭_컨트롤)
        탭_컨트롤.add(탭_프레임, text=탭_이름)
        
        # 쇼핑몰 선택을 위한 라디오 버튼
        쇼핑몰_프레임 = tk.Frame(탭_프레임)
        쇼핑몰_프레임.pack(pady=5, fill='x')
        
        쇼핑몰_라벨 = tk.Label(쇼핑몰_프레임, text="쇼핑몰 선택:")
        쇼핑몰_라벨.pack(side=tk.LEFT, padx=5)
        
        쇼핑몰 = StringVar(value="네이버")  # 기본값은 네이버
        
        네이버_라디오 = Radiobutton(쇼핑몰_프레임, text="네이버", variable=쇼핑몰, value="네이버")
        네이버_라디오.pack(side=tk.LEFT, padx=10)
        
        쿠팡_라디오 = Radiobutton(쇼핑몰_프레임, text="쿠팡", variable=쇼핑몰, value="쿠팡")
        쿠팡_라디오.pack(side=tk.LEFT, padx=10)
        
        # 안내 라벨
        안내_라벨 = tk.Label(탭_프레임, text="배송지 정보를 아래에 입력하세요")
        안내_라벨.pack(pady=5)
        
        # 텍스트 입력 영역
        텍스트_영역 = scrolledtext.ScrolledText(탭_프레임, width=80, height=10)
        텍스트_영역.pack(pady=5, padx=10, fill='both', expand=True)
        
        # 분석 버튼
        분석_버튼 = tk.Button(탭_프레임, text="정보 분석", 
                         command=lambda t=텍스트_영역, s=쇼핑몰: 분석_실행(t, s),
                         width=15, height=1)
        분석_버튼.pack(pady=10)
        
        # 결과 라벨
        결과_라벨 = tk.Label(탭_프레임, text="분석 결과:")
        결과_라벨.pack(pady=(5, 0))
        
        # JSON 결과 영역
        결과_영역 = scrolledtext.ScrolledText(탭_프레임, width=80, height=15, state=tk.DISABLED)
        결과_영역.pack(pady=5, padx=10, fill='both', expand=True)
        
        # 초기 메시지 표시
        결과_영역.config(state=tk.NORMAL)
        결과_영역.insert(tk.END, '''아래의 내용이 나타날 예정입니다.

상품명 :
주문번호 :
택배사 : 
송장번호 :
주문자 :
연락처 : 
배송지 : 

''')
        결과_영역.config(state=tk.DISABLED)
        
        # 복사 상태 라벨
        복사_상태_라벨 = tk.Label(탭_프레임, text="", height=1)
        복사_상태_라벨.pack(pady=5)
        
        # 탭 데이터 저장
        탭_데이터 = {
            "텍스트_영역": 텍스트_영역,
            "결과_영역": 결과_영역,
            "복사_상태_라벨": 복사_상태_라벨,
            "쇼핑몰": 쇼핑몰,
            "최근_분석_결과": None
        }
        
        # 생성된 탭 정보 저장
        탭_목록.append((탭_프레임, 탭_데이터))
        
        # 새 탭으로 포커스 이동
        탭_컨트롤.select(len(탭_목록) - 1)
        
        return 탭_데이터
    
    def 분석_실행(텍스트_영역, 쇼핑몰_변수):
        # 현재 선택된 탭 인덱스
        현재_탭 = 탭_컨트롤.index(탭_컨트롤.select())
        탭_데이터 = 탭_목록[현재_탭][1]
        결과_영역 = 탭_데이터["결과_영역"]
        복사_상태_라벨 = 탭_데이터["복사_상태_라벨"]
        
        # 분석 중임을 표시
        결과_영역.config(state=tk.NORMAL)
        결과_영역.delete("1.0", tk.END)
        결과_영역.insert(tk.END, "GPT로 정보를 분석 중입니다... 잠시만 기다려주세요.")
        결과_영역.config(state=tk.DISABLED)
        
        복사_상태_라벨.config(text="GPT API 호출 중...")
        
        # 화면 즉시 업데이트
        부모_프레임.update_idletasks()
        
        def 백그라운드_분석():
            배송정보 = 텍스트_영역.get("1.0", tk.END)
            선택된_쇼핑몰 = 쇼핑몰_변수.get()
            
            try:
                분석결과 = 텍스트_분석(배송정보, 선택된_쇼핑몰)
                
                # UI 업데이트는 메인 스레드에서 수행
                부모_프레임.after(0, lambda: 분석_결과_표시(분석결과, 탭_데이터))
            except Exception as e:
                # 오류 발생 시 UI 업데이트
                부모_프레임.after(0, lambda: 분석_오류_표시(str(e), 탭_데이터))
        
        # 백그라운드에서 분석 실행
        분석_스레드 = threading.Thread(target=백그라운드_분석)
        분석_스레드.daemon = True  # 메인 프로그램 종료 시 스레드도 종료
        분석_스레드.start()
    
    def 분석_결과_표시(분석결과, 탭_데이터):
        # 분석 결과 저장
        탭_데이터["최근_분석_결과"] = 분석결과
        결과_영역 = 탭_데이터["결과_영역"]
        복사_상태_라벨 = 탭_데이터["복사_상태_라벨"]
        
        # API 정보 추출
        api_정보 = 분석결과.get("API_정보", {})
        입력_토큰 = api_정보.get("입력_토큰", 0)
        출력_토큰 = api_정보.get("출력_토큰", 0)
        총_토큰 = api_정보.get("총_토큰", 0)
        비용_원화 = api_정보.get("비용_원화", 0)
        
        # JSON 대신 텍스트 형식으로 결과 표시
        결과_영역.config(state=tk.NORMAL)
        결과_영역.delete("1.0", tk.END)
        
        # 텍스트 형식으로 변환하여 표시
        텍스트_형식 = json_to_text_format(분석결과)
        결과_영역.insert(tk.END, 텍스트_형식)
        
        # API 정보를 텍스트 아래에 추가 표시
        결과_영역.insert(tk.END, f"\n\n----- API 정보 -----\n")
        결과_영역.insert(tk.END, f"입력 토큰: {입력_토큰}\n")
        결과_영역.insert(tk.END, f"출력 토큰: {출력_토큰}\n")
        결과_영역.insert(tk.END, f"총 토큰: {총_토큰}\n")
        결과_영역.insert(tk.END, f"비용: {비용_원화}원\n")
        
        결과_영역.config(state=tk.DISABLED)
        
        # 분석 완료 메시지 (토큰 정보 포함)
        토큰_정보 = f"분석 완료! [입력: {입력_토큰}토큰 / 출력: {출력_토큰}토큰 / 총: {총_토큰}토큰 / 비용: {비용_원화}원]"
        복사_상태_라벨.config(text=토큰_정보)
    
    def 분석_오류_표시(오류_메시지, 탭_데이터):
        결과_영역 = 탭_데이터["결과_영역"]
        복사_상태_라벨 = 탭_데이터["복사_상태_라벨"]
        
        # 오류 메시지 표시
        결과_영역.config(state=tk.NORMAL)
        결과_영역.delete("1.0", tk.END)
        결과_영역.insert(tk.END, f"분석 중 오류가 발생했습니다:\n{오류_메시지}")
        결과_영역.config(state=tk.DISABLED)
        
        복사_상태_라벨.config(text="GPT API 호출 중 오류가 발생했습니다.")
    
    def 모든_반품정보_복사():
        # 현재 날짜 가져오기
        오늘 = datetime.datetime.now()
        날짜_텍스트 = f"{오늘.month}/{오늘.day}"
        
        # 인사말 생성 - 요청한 줄바꿈 형식으로 수정
        인사말 = f"안녕하세요! 저희 반품 회수요청 드립니다. ({날짜_텍스트})\n확인 부탁드립니다!\n\n\n"
        
        # 모든 탭의 분석 결과를 하나의 텍스트로 합치기
        모든_정보 = 인사말  # 인사말로 시작
        유효한_데이터_존재 = False
        유효한_탭_개수 = 0
        
        for i, (탭_프레임, 탭_데이터) in enumerate(탭_목록):
            최근_분석_결과 = 탭_데이터["최근_분석_결과"]
            if 최근_분석_결과:
                유효한_데이터_존재 = True
                유효한_탭_개수 += 1
                
                # 첫 번째 이후의 반품정보 앞에는 구분선 추가
                if 유효한_탭_개수 > 1:
                    모든_정보 += "\n\n" + "=" * 30 + "\n\n"
                
                카톡_텍스트 = json_to_kakao_format(최근_분석_결과)
                모든_정보 += 카톡_텍스트
        
        if 유효한_데이터_존재:
            # 클립보드에 복사
            pyperclip.copy(모든_정보)
            
            # 별도의 창에 모든 정보 표시
            모든정보_창 = Toplevel(부모_프레임)
            모든정보_창.title(f"모든 반품정보 ({유효한_탭_개수}개)")
            모든정보_창.geometry("500x600")
            
            # 창 상단 라벨
            상단_라벨 = tk.Label(모든정보_창, text="카카오톡 형식으로 변환된 모든 반품정보", font=("맑은 고딕", 12))
            상단_라벨.pack(pady=10)
            
            # 결과 표시 영역
            모든정보_텍스트 = Text(모든정보_창, wrap=tk.WORD, width=60, height=25)
            모든정보_텍스트.pack(padx=10, pady=5, fill='both', expand=True)
            모든정보_텍스트.insert(tk.END, 모든_정보)
            모든정보_텍스트.config(state=tk.DISABLED)
            
            # 복사 확인 라벨
            복사확인_라벨 = tk.Label(모든정보_창, text="클립보드에 복사되었습니다!", fg="blue")
            복사확인_라벨.pack(pady=5)
            
            # 닫기 버튼
            닫기_버튼 = tk.Button(모든정보_창, text="닫기", command=모든정보_창.destroy, width=10)
            닫기_버튼.pack(pady=10)
            
            # 현재 선택된 탭의 상태 라벨 업데이트
            현재_탭 = 탭_컨트롤.index(탭_컨트롤.select())
            탭_데이터 = 탭_목록[현재_탭][1]
            복사_상태_라벨 = 탭_데이터["복사_상태_라벨"]
            복사_상태_라벨.config(text=f"모든 반품정보({유효한_탭_개수}개)가 클립보드에 복사되었습니다!")
        else:
            # 분석된 데이터가 없는 경우
            현재_탭 = 탭_컨트롤.index(탭_컨트롤.select())
            탭_데이터 = 탭_목록[현재_탭][1]
            복사_상태_라벨 = 탭_데이터["복사_상태_라벨"]
            복사_상태_라벨.config(text="분석된 반품정보가 없습니다.")
    
    # 버튼에 명령 할당 (함수 정의 후)
    추가_버튼.config(command=탭_추가)
    모든정보_복사_버튼.config(command=모든_반품정보_복사)
    
    # 첫 번째 탭 생성
    탭_생성(f"반품 #{탭_카운터}")
    탭_카운터 += 1

    # 디버깅용 레이블 추가
    상태_레이블 = tk.Label(부모_프레임, text="GUI가 정상적으로 로드되었습니다", fg="green")
    상태_레이블.pack(side=tk.BOTTOM, pady=5)
