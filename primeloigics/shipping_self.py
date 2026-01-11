import shutil
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
from datetime import datetime
import json
import openai
from dotenv import load_dotenv
import webbrowser  # 웹브라우저 모듈 추가
import platform  # 운영체제 확인을 위한 모듈 추가
import subprocess  # 외부 프로세스 실행을 위한 모듈 추가

# .env 파일에서 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

def csv_파일_복사():
    """
    form_sample 폴더의 CSV 파일을 복사하는 함수
    """
    try:
        # 원본 파일 경로
        원본_파일 = os.path.join("form_sample", "20250205_라라스토어_이지어드민 출고요청.csv")
        
        # 대상 파일 경로 (현재 디렉토리에 복사)
        대상_파일 = "20250205_라라스토어_이지어드민 출고요청.csv"
        
        # 파일 복사
        shutil.copy2(원본_파일, 대상_파일)
        
        # 성공 메시지
        messagebox.showinfo("파일 복사 완료", f"'{원본_파일}'이 현재 디렉토리에 복사되었습니다.")
        return f"'{원본_파일}'이 현재 디렉토리에 복사되었습니다."
    
    except FileNotFoundError:
        오류_메시지 = f"파일을 찾을 수 없습니다: {원본_파일}"
        messagebox.showerror("오류", 오류_메시지)
        return 오류_메시지
    
    except Exception as e:
        오류_메시지 = f"파일 복사 중 오류 발생: {str(e)}"
        messagebox.showerror("오류", 오류_메시지)
        return 오류_메시지

def 수기출고_프레임_생성(부모_프레임, 상태_콜백=None):
    """
    수기출고 데이터를 입력할 수 있는 테이블 GUI를 프레임 형태로 생성하는 함수
    """
    # 상품 리스트
    상품_리스트 = ["럭슨 오페라글라스 미드그레이", "럭슨 오페라글라스 블랙", "로도프 보풀제거기", "유다모 탈모샴푸", "직접입력"]
    
    # 헤더 (삭제 버튼 열 추가)
    표시_헤더 = ['삭제', '[주문번호]', '[상품명]', '[수량]', '[받는사람]', '[받는사람 휴대폰번호]', '[받는사람 주소]', '[배송기재사항]']
    # CSV 저장용 헤더 (원래 헤더 유지)
    헤더 = ['[주문번호]', '[상품명]', '[수량]', '[받는사람]', '[받는사람 휴대폰번호]', '[받는사람 주소]', '[배송기재사항]']
    
    # 메인 프레임 생성
    메인_프레임 = ttk.Frame(부모_프레임, padding=10)
    메인_프레임.pack(fill="both", expand=True)
    
    # 상단 설명 라벨
    ttk.Label(메인_프레임, text="※ 행 삭제: 행 앞의 [-] 버튼 클릭 또는 행 선택 후 Delete 키 누르기").pack(pady=(0, 10))
    
    # 테이블 프레임 생성
    테이블_프레임 = ttk.Frame(메인_프레임)
    테이블_프레임.pack(fill="both", expand=True, pady=5)
    
    # 테이블 생성 - 높이를 16에서 10으로 줄임
    tree = ttk.Treeview(테이블_프레임, columns=표시_헤더, show="headings", height=10)
    
    # 스크롤바 추가
    y스크롤 = ttk.Scrollbar(테이블_프레임, orient="vertical", command=tree.yview)
    y스크롤.pack(side="right", fill="y")
    
    x스크롤 = ttk.Scrollbar(테이블_프레임, orient="horizontal", command=tree.xview)
    x스크롤.pack(side="bottom", fill="x")
    
    tree.configure(yscrollcommand=y스크롤.set, xscrollcommand=x스크롤.set)
    
    # 헤더 설정
    for i, col in enumerate(표시_헤더):
        tree.heading(col, text=col)
        if col == '삭제':
            tree.column(col, width=40, anchor="center", minwidth=40)
        elif col == '[주문번호]':
            tree.column(col, width=150, anchor="center", minwidth=120)
        elif col == '[상품명]':
            tree.column(col, width=200, anchor="w", minwidth=150)
        elif col == '[수량]':
            tree.column(col, width=60, anchor="center", minwidth=50)
        elif col == '[받는사람]':
            tree.column(col, width=100, anchor="w", minwidth=80)
        elif col == '[받는사람 휴대폰번호]':
            tree.column(col, width=150, anchor="w", minwidth=120)
        elif col == '[받는사람 주소]':
            tree.column(col, width=300, anchor="w", minwidth=200)
        else:
            tree.column(col, width=200, anchor="w", minwidth=150)
    
    tree.pack(fill="both", expand=True)
    
    # 트리뷰 셀 편집 기능 추가
    def 셀_더블클릭(event):
        # 클릭된 위치 확인
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        # 클릭된 행과 열 식별
        column = tree.identify_column(event.x)
        row_id = tree.identify_row(event.y)
        
        if not row_id:
            return
        
        # 열 인덱스 계산 (#1, #2, ... 형식에서 숫자만 추출)
        column_index = int(column.replace('#', '')) - 1
        
        # 삭제 버튼 열(첫 번째 열)이나 주문번호 열(두 번째 열)은 편집 불가
        if column_index <= 1:
            return
        
        # 현재 셀 값 가져오기
        current_values = tree.item(row_id, 'values')
        current_text = current_values[column_index] if len(current_values) > column_index else ""
        
        # 편집할 열의 헤더 이름 가져오기
        column_name = 표시_헤더[column_index]
        
        # 셀의 좌표 계산
        x, y, width, height = tree.bbox(row_id, column)
        
        # 상품명 열인 경우 콤보박스로 편집
        if column_name == '[상품명]':
            # 임시 콤보박스 생성
            temp_combo = ttk.Combobox(tree, values=상품_리스트, width=width//10)
            temp_combo.set(current_text)
            temp_combo.place(x=x, y=y, width=width, height=height)
            temp_combo.focus_set()
            
            # 콤보박스 값 변경 후 처리
            def 콤보박스_선택(event=None):
                new_value = temp_combo.get()
                # 직접입력 처리
                if new_value == "직접입력":
                    직접입력_창 = tk.Toplevel(부모_프레임)
                    직접입력_창.title("상품명 직접 입력")
                    직접입력_창.geometry("300x100")
                    직접입력_창.resizable(False, False)
                    직접입력_창.transient(부모_프레임)
                    직접입력_창.grab_set()
                    
                    ttk.Label(직접입력_창, text="상품명 입력:").pack(padx=10, pady=10)
                    입력_필드 = ttk.Entry(직접입력_창, width=30)
                    입력_필드.pack(padx=10, pady=5)
                    입력_필드.focus_set()
                    
                    def 직접입력_확인():
                        입력값 = 입력_필드.get()
                        if 입력값:
                            new_values = list(current_values)
                            new_values[column_index] = 입력값
                            tree.item(row_id, values=new_values)
                        직접입력_창.destroy()
                    
                    # 엔터키 이벤트 추가
                    입력_필드.bind("<Return>", lambda event: 직접입력_확인())
                    ttk.Button(직접입력_창, text="확인", command=직접입력_확인).pack(pady=10)
                    
                    부모_프레임.wait_window(직접입력_창)
                else:
                    # 값 업데이트
                    new_values = list(current_values)
                    new_values[column_index] = new_value
                    tree.item(row_id, values=new_values)
                
                # 임시 콤보박스 제거
                temp_combo.destroy()
            
            # 콤보박스 이벤트 바인딩
            temp_combo.bind("<<ComboboxSelected>>", 콤보박스_선택)
            temp_combo.bind("<Return>", 콤보박스_선택)
            temp_combo.bind("<FocusOut>", lambda e: temp_combo.destroy())
        
        else:
            # 일반 텍스트 필드로 편집
            temp_entry = ttk.Entry(tree)
            temp_entry.insert(0, current_text)
            temp_entry.place(x=x, y=y, width=width, height=height)
            temp_entry.focus_set()
            
            # 엔터키 입력 시 값 저장
            def 엔터키_처리(event=None):
                new_text = temp_entry.get()
                
                # 값 검증 (수량 필드는 숫자만 허용)
                if column_name == '[수량]' and not new_text.isdigit():
                    messagebox.showerror("입력 오류", "수량은 숫자만 입력 가능합니다.")
                    temp_entry.focus_set()
                    return
                
                # 변경된 값 적용
                new_values = list(current_values)
                new_values[column_index] = new_text
                tree.item(row_id, values=new_values)
                
                # 임시 입력 필드 제거
                temp_entry.destroy()
            
            # 이벤트 바인딩
            temp_entry.bind("<Return>", 엔터키_처리)
            temp_entry.bind("<FocusOut>", lambda e: 엔터키_처리())

    # 더블클릭 이벤트 바인딩
    tree.bind("<Double-1>", 셀_더블클릭)
    
    # 트리뷰 클릭 이벤트 - 삭제 버튼 클릭 처리
    def 트리뷰_클릭(event):
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            column = tree.identify_column(event.x)
            column_index = int(column.replace('#', '')) - 1
            
            # 첫 번째 열(삭제 버튼 열)인 경우
            if column_index == 0:
                row_id = tree.identify_row(event.y)
                if row_id:
                    확인 = messagebox.askyesno("행 삭제", "선택한 행을 삭제하시겠습니까?")
                    if 확인:
                        tree.delete(row_id)
    
    tree.bind("<ButtonRelease-1>", 트리뷰_클릭)
    
    # 키보드 이벤트 - Delete 키로 행 삭제
    def 행_삭제_키(event):
        선택된_항목 = tree.selection()
        if 선택된_항목:
            확인 = messagebox.askyesno("행 삭제", "선택한 행을 삭제하시겠습니까?")
            if 확인:
                for item in 선택된_항목:
                    tree.delete(item)
    
    tree.bind("<Delete>", 행_삭제_키)
    
    # 현재 행 수 저장 변수
    행_카운트 = [0]
    
    # 오늘 날짜
    오늘날짜 = datetime.now().strftime("%Y%m%d")
    
    def 새_주문번호_생성():
        """다음 주문번호 생성"""
        행_카운트[0] += 1
        주문번호 = f"{오늘날짜}_{행_카운트[0]:05d}"
        return 주문번호
    
    # 휴대폰 번호 형식 정규화 함수
    def 휴대폰번호_정규화(번호):
        """휴대폰 번호를 010-XXXX-XXXX 형식으로 변환"""
        # 숫자만 추출
        숫자만 = ''.join(filter(str.isdigit, 번호))
        
        # 숫자가 10-11자리인 경우에만 처리
        if len(숫자만) == 11:  # 11자리(010XXXXXXXX)
            return f"{숫자만[:3]}-{숫자만[3:7]}-{숫자만[7:]}"
        elif len(숫자만) == 10:  # 10자리(01XXXXXXXX)
            return f"{숫자만[:3]}-{숫자만[3:6]}-{숫자만[6:]}"
        else:
            return 번호  # 원래 형식 유지
    
    # 휴대폰 번호 필드 형식 업데이트 함수
    def 휴대폰번호_형식_업데이트(event=None, 필드=None):
        """포커스가 떠날 때 휴대폰 번호 형식 업데이트"""
        if 필드 is None:
            필드 = event.widget
        
        현재값 = 필드.get()
        정규화된_값 = 휴대폰번호_정규화(현재값)
        
        # 값이 변경된 경우에만 업데이트
        if 현재값 != 정규화된_값:
            필드.delete(0, tk.END)
            필드.insert(0, 정규화된_값)
    
    def AI로_데이터_추가():
        """AI를 이용하여 텍스트 데이터 분석 후 테이블에 추가"""
        텍스트 = ai_텍스트_입력.get("1.0", tk.END).strip()
        
        if not 텍스트:
            messagebox.showinfo("알림", "텍스트를 입력해주세요.")
            return
        
        try:
            # 로딩 표시
            if 상태_콜백:
                상태_콜백("AI가 데이터를 분석 중입니다...")
            
            # OpenAI API 요청 (명확한 형식 지정)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "배송 주문 정보를 JSON 형식으로 추출해주세요. 정확히 지정된 키 이름을 사용하세요."},
                    {"role": "user", "content": f"""
                    다음 텍스트에서 주문 정보를 추출하여 정확한 JSON 형식으로만 반환해주세요:
                    
                    {텍스트}
                    
                    다음 필드명을 정확히 사용하여 반환해주세요:
                    {{
                        "[상품명]": "상품 이름",
                        "[수량]": "수량(숫자만)",
                        "[받는사람]": "수령인 이름",
                        "[받는사람 휴대폰번호]": "전화번호",
                        "[받는사람 주소]": "주소",
                        "[배송기재사항]": "배송 요청사항"
                    }}
                    
                    * 주의: 필드명을 정확히 "[상품명]", "[수량]" 등의 형식으로 사용하세요.
                    * 수량이 명시되지 않은 경우 기본값은 1로 설정하세요.
                    * 배송기재사항이 없으면 빈 문자열로 설정하세요.
                    * 설명 없이 JSON 객체만 응답해주세요.
                    * 모든 값을 문자열로 반환해주세요.
                    """}
                ],
                response_format={"type": "json_object"}
            )
            
            # 응답에서 JSON 추출
            response_text = response.choices[0].message.content.strip()
            
            # 디버깅 메시지 (실제 응답 내용 확인)
            print("API 응답:", response_text)
            
            # JSON 파싱
            데이터 = json.loads(response_text)
            
            # 디버깅 메시지 (파싱된 데이터 확인)
            print("파싱된 데이터:", 데이터)
            
            # 키 이름 정규화 - 대괄호 없는 키를 대괄호 있는 형식으로 변환
            정규화된_데이터 = {}
            for 키, 값 in 데이터.items():
                정규화된_키 = 키
                if not 키.startswith('['):
                    정규화된_키 = f"[{키}]"
                정규화된_데이터[정규화된_키] = 값
            
            # 데이터 준비 (누락된 필드는 빈 값으로 설정)
            모든_필드 = ['[상품명]', '[수량]', '[받는사람]', '[받는사람 휴대폰번호]', '[받는사람 주소]', '[배송기재사항]']
            최종_데이터 = {}
            
            for 필드 in 모든_필드:
                기본값 = "1" if 필드 == "[수량]" else ""
                # 대괄호 있는 형식 확인
                if 필드 in 정규화된_데이터 and 정규화된_데이터[필드]:
                    최종_데이터[필드] = 정규화된_데이터[필드]
                # 대괄호 없는 형식 확인 (호환성)
                elif 필드.strip('[]') in 데이터 and 데이터[필드.strip('[]')]:
                    최종_데이터[필드] = 데이터[필드.strip('[]')]
                # 기본값 설정
                else:
                    최종_데이터[필드] = 기본값
            
            # 디버깅 메시지 (최종 데이터 확인)
            print("최종 데이터:", 최종_데이터)
            
            # 데이터 확인 팝업창 생성
            확인_창 = tk.Toplevel(부모_프레임)
            확인_창.title("AI 분석 결과 확인")
            확인_창.geometry("600x400")  # 600x400으로 조정
            확인_창.resizable(False, False)  # 창 크기 고정
            확인_창.transient(부모_프레임)
            확인_창.grab_set()
            
            # 메인 프레임 - 여백 조정
            메인_프레임 = ttk.Frame(확인_창, padding=15)
            메인_프레임.pack(fill="both", expand=True)
            
            # 간소화된 제목 (하나만 유지)
            제목_라벨 = ttk.Label(
                메인_프레임, 
                text="AI 분석 결과 확인", 
                font=("맑은 고딕", 12, "bold")
            )
            제목_라벨.pack(anchor="center", pady=(0, 15))
            
            # 데이터 수정 프레임 - 패딩 유지
            편집_프레임 = ttk.Frame(메인_프레임, padding=10)
            편집_프레임.pack(fill="both", expand=True)
            
            # 수정 가능한 필드들 생성 - 스타일 유지
            편집_필드 = {}
            라벨_스타일 = {"font": ("맑은 고딕", 10), "width": 12, "anchor": "e"}
            엔트리_스타일 = {"font": ("맑은 고딕", 10)}
            
            # 상품명 그룹 - 너비 조정
            상품_프레임 = ttk.LabelFrame(편집_프레임, text="상품 정보", padding=(10, 5))
            상품_프레임.pack(fill="x", pady=(0, 10))
            
            ttk.Label(상품_프레임, text="상품명:", **라벨_스타일).grid(row=0, column=0, sticky="e", padx=5, pady=8)
            편집_필드['[상품명]'] = ttk.Combobox(상품_프레임, values=상품_리스트, width=20, **엔트리_스타일)
            편집_필드['[상품명]'].set(최종_데이터['[상품명]'])
            편집_필드['[상품명]'].grid(row=0, column=1, sticky="w", padx=5, pady=8)
            
            ttk.Label(상품_프레임, text="수량:", **라벨_스타일).grid(row=0, column=2, sticky="e", padx=5, pady=8)
            편집_필드['[수량]'] = ttk.Entry(상품_프레임, width=8, **엔트리_스타일)
            편집_필드['[수량]'].insert(0, 최종_데이터['[수량]'])
            편집_필드['[수량]'].grid(row=0, column=3, sticky="w", padx=5, pady=8)
            
            # 수령인 그룹 - 너비 조정
            수령인_프레임 = ttk.LabelFrame(편집_프레임, text="수령인 정보", padding=(10, 5))
            수령인_프레임.pack(fill="x", pady=(0, 10))
            
            ttk.Label(수령인_프레임, text="수령인:", **라벨_스타일).grid(row=0, column=0, sticky="e", padx=5, pady=8)
            편집_필드['[받는사람]'] = ttk.Entry(수령인_프레임, width=20, **엔트리_스타일)
            편집_필드['[받는사람]'].insert(0, 최종_데이터['[받는사람]'])
            편집_필드['[받는사람]'].grid(row=0, column=1, sticky="w", padx=5, pady=8)
            
            ttk.Label(수령인_프레임, text="연락처:", **라벨_스타일).grid(row=0, column=2, sticky="e", padx=5, pady=8)
            편집_필드['[받는사람 휴대폰번호]'] = ttk.Entry(수령인_프레임, width=15, **엔트리_스타일)
            편집_필드['[받는사람 휴대폰번호]'].insert(0, 최종_데이터['[받는사람 휴대폰번호]'])
            편집_필드['[받는사람 휴대폰번호]'].grid(row=0, column=3, sticky="w", padx=5, pady=8)
            
            # 휴대폰 번호 필드에 형식 변환 함수 바인딩
            편집_필드['[받는사람 휴대폰번호]'].bind("<FocusOut>", 휴대폰번호_형식_업데이트)
            
            ttk.Label(수령인_프레임, text="배송주소:", **라벨_스타일).grid(row=1, column=0, sticky="e", padx=5, pady=8)
            편집_필드['[받는사람 주소]'] = ttk.Entry(수령인_프레임, width=55, **엔트리_스타일)
            편집_필드['[받는사람 주소]'].insert(0, 최종_데이터['[받는사람 주소]'])
            편집_필드['[받는사람 주소]'].grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=8)
            
            # 추가 정보 그룹 - 너비 조정
            추가정보_프레임 = ttk.LabelFrame(편집_프레임, text="배송 메모", padding=(10, 5))
            추가정보_프레임.pack(fill="x", pady=(0, 10))
            
            ttk.Label(추가정보_프레임, text="배송기재사항:", **라벨_스타일).grid(row=0, column=0, sticky="e", padx=5, pady=8)
            편집_필드['[배송기재사항]'] = ttk.Entry(추가정보_프레임, width=55, **엔트리_스타일)
            편집_필드['[배송기재사항]'].insert(0, 최종_데이터['[배송기재사항]'])
            편집_필드['[배송기재사항]'].grid(row=0, column=1, sticky="ew", padx=5, pady=8)
            
            # 상품명 직접입력 함수는 그대로 유지
            def 상품명_직접입력(event=None):
                if 편집_필드['[상품명]'].get() == "직접입력":
                    직접입력_창 = tk.Toplevel(확인_창)
                    직접입력_창.title("상품명 직접 입력")
                    직접입력_창.geometry("350x120")
                    직접입력_창.resizable(False, False)
                    직접입력_창.transient(확인_창)
                    직접입력_창.grab_set()
                    
                    내부_프레임 = ttk.Frame(직접입력_창, padding=15)
                    내부_프레임.pack(fill="both", expand=True)
                    
                    ttk.Label(내부_프레임, text="상품명 입력:", font=("맑은 고딕", 10)).pack(anchor="w", pady=(0, 5))
                    입력_필드 = ttk.Entry(내부_프레임, width=40, font=("맑은 고딕", 10))
                    입력_필드.pack(fill="x", pady=5)
                    입력_필드.focus_set()
                    
                    def 확인():
                        편집_필드['[상품명]'].set(입력_필드.get())
                        직접입력_창.destroy()
                    
                    # 엔터키 이벤트 추가
                    입력_필드.bind("<Return>", lambda event: 확인())
                    
                    버튼_프레임 = ttk.Frame(내부_프레임)
                    버튼_프레임.pack(anchor="e", pady=(10, 0))
                    
                    ttk.Button(버튼_프레임, text="확인", command=확인, width=10).pack(side="right")
                    
                    확인_창.wait_window(직접입력_창)
            
            편집_필드['[상품명]'].bind("<<ComboboxSelected>>", 상품명_직접입력)
            
            # 버튼 프레임 - 간소화
            버튼_프레임 = ttk.Frame(메인_프레임)
            버튼_프레임.pack(pady=(15, 0), anchor="center")
            
            # 확인/취소 버튼 - 유지
            버튼_스타일 = {"width": 12, "padding": 5}
            
            def 확인():
                # 필수 필드 검증
                필수_필드 = ['[상품명]', '[수량]', '[받는사람]', '[받는사람 휴대폰번호]', '[받는사람 주소]']
                
                # 필드 값 가져오기
                최종_데이터 = {}
                for 필드 in 모든_필드:
                    최종_데이터[필드] = 편집_필드[필드].get()
                
                # 필수 필드 체크
                누락_필드 = [필드 for 필드 in 필수_필드 if not 최종_데이터.get(필드)]
                if 누락_필드:
                    messagebox.showerror("입력 오류", f"다음 필드는 필수입니다: {', '.join(누락_필드)}")
                    return
                    
                # 수량 숫자 검증
                if not 최종_데이터['[수량]'].isdigit():
                    messagebox.showerror("입력 오류", "수량은 숫자만 입력 가능합니다.")
                    return
                    
                # 창 닫기
                확인_창.destroy()
                
                # 추출된 데이터로 테이블에 행 추가
                주문번호 = 새_주문번호_생성()
                
                # 트리뷰에 행 추가
                values = ["[-]", 주문번호] + [최종_데이터[col] for col in 헤더[1:]]
                tree.insert('', 'end', values=values)
                
                # 입력 필드 비우기
                ai_텍스트_입력.delete("1.0", tk.END)
                
                # 성공 메시지 - 팝업창 제거하고 상태바만 업데이트
                if 상태_콜백:
                    상태_콜백("AI가 데이터를 성공적으로 추가했습니다.")
            
            def 취소():
                확인_창.destroy()
                if 상태_콜백:
                    상태_콜백("AI 데이터 추가가 취소되었습니다.")
            
            확인_버튼 = ttk.Button(버튼_프레임, text="확인", command=확인, **버튼_스타일)
            확인_버튼.pack(side="left", padx=10)
            
            취소_버튼 = ttk.Button(버튼_프레임, text="취소", command=취소, **버튼_스타일)
            취소_버튼.pack(side="left", padx=10)
            
        except json.JSONDecodeError:
            messagebox.showerror("오류", "JSON 파싱 오류: AI 응답을 JSON으로 변환할 수 없습니다.")
            if 상태_콜백:
                상태_콜백("오류: AI 응답을 파싱할 수 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"AI 데이터 추가 중 오류 발생: {str(e)}")
            if 상태_콜백:
                상태_콜백(f"오류: {str(e)}")

    # AI 데이터 입력 프레임 추가 - 함수 정의 이후로 이동
    ai_입력_프레임 = ttk.LabelFrame(메인_프레임, text="AI 데이터 변환", padding=10)
    ai_입력_프레임.pack(fill="x", pady=10)
    
    # AI 텍스트 입력창
    ttk.Label(ai_입력_프레임, text="텍스트를 입력하면 AI가 자동으로 데이터를 분류합니다").pack(pady=(0, 5))
    ai_텍스트_입력 = scrolledtext.ScrolledText(ai_입력_프레임, width=60, height=5, wrap=tk.WORD)
    ai_텍스트_입력.pack(fill="x", pady=5)
    
    # AI 데이터 추가 버튼
    ai_버튼 = ttk.Button(ai_입력_프레임, text="AI로 데이터 추가하기", command=AI로_데이터_추가, width=20)
    ai_버튼.pack(pady=5)
    ai_버튼.configure(style='Custom.TButton')
    
    # 데이터 입력 프레임
    입력_프레임 = ttk.LabelFrame(메인_프레임, text="데이터 입력", padding=10)
    입력_프레임.pack(fill="x", pady=10)
    
    # 입력 필드 생성
    입력_필드 = {}
    
    # 입력 필드 영역 생성 (좌측 상품정보, 우측 배송정보)
    입력_상품정보 = ttk.LabelFrame(입력_프레임, text="상품 정보", padding=5)
    입력_상품정보.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    입력_배송정보 = ttk.LabelFrame(입력_프레임, text="배송 정보", padding=5)
    입력_배송정보.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    # 상품 정보 입력 필드
    # 상품명 콤보박스
    ttk.Label(입력_상품정보, text='[상품명]').grid(row=0, column=0, padx=5, pady=5, sticky="e")
    상품명_콤보 = ttk.Combobox(입력_상품정보, values=상품_리스트, width=25)
    상품명_콤보.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    상품명_콤보.bind("<<ComboboxSelected>>", lambda e: 상품명_선택_이벤트(e, 상품명_콤보))
    입력_필드['[상품명]'] = 상품명_콤보
    
    # 수량 입력
    ttk.Label(입력_상품정보, text='[수량]').grid(row=1, column=0, padx=5, pady=5, sticky="e")
    수량_입력 = ttk.Entry(입력_상품정보, width=5)
    수량_입력.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    수량_입력.insert(0, "1")  # 기본값 1
    입력_필드['[수량]'] = 수량_입력
    
    # 배송 정보 입력 필드
    # 받는사람 입력
    ttk.Label(입력_배송정보, text='[받는사람]').grid(row=0, column=0, padx=5, pady=5, sticky="e")
    받는사람_입력 = ttk.Entry(입력_배송정보, width=15)
    받는사람_입력.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    입력_필드['[받는사람]'] = 받는사람_입력
    
    # 받는사람 휴대폰번호 입력
    ttk.Label(입력_배송정보, text='[받는사람 휴대폰번호]').grid(row=1, column=0, padx=5, pady=5, sticky="e")
    휴대폰번호_입력 = ttk.Entry(입력_배송정보, width=15)
    휴대폰번호_입력.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    입력_필드['[받는사람 휴대폰번호]'] = 휴대폰번호_입력
    
    # 받는사람 주소 입력
    ttk.Label(입력_배송정보, text='[받는사람 주소]').grid(row=0, column=2, padx=5, pady=5, sticky="e")
    주소_입력 = ttk.Entry(입력_배송정보, width=40)
    주소_입력.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    입력_필드['[받는사람 주소]'] = 주소_입력
    
    # 배송기재사항 입력
    ttk.Label(입력_배송정보, text='[배송기재사항]').grid(row=1, column=2, padx=5, pady=5, sticky="e")
    배송기재사항_입력 = ttk.Entry(입력_배송정보, width=40)
    배송기재사항_입력.grid(row=1, column=3, padx=5, pady=5, sticky="w")
    입력_필드['[배송기재사항]'] = 배송기재사항_입력
    
    def 상품명_선택_이벤트(event, 콤보박스):
        """상품명 콤보박스에서 '직접입력' 선택 시 처리"""
        if 콤보박스.get() == "직접입력":
            # 직접 입력 창 표시
            직접입력_창 = tk.Toplevel(부모_프레임)
            직접입력_창.title("상품명 직접 입력")
            직접입력_창.geometry("300x100")
            직접입력_창.resizable(False, False)
            
            ttk.Label(직접입력_창, text="상품명 입력:").pack(padx=10, pady=10)
            입력_필드 = ttk.Entry(직접입력_창, width=30)
            입력_필드.pack(padx=10, pady=5)
            입력_필드.focus_set()
            
            def 확인():
                콤보박스.set(입력_필드.get())
                직접입력_창.destroy()
            
            # 엔터키 이벤트 추가
            입력_필드.bind("<Return>", lambda event: 확인())
                
            ttk.Button(직접입력_창, text="확인", command=확인).pack(pady=10)
            
            # 창이 닫힐 때까지 기다림
            직접입력_창.transient(부모_프레임)
            직접입력_창.grab_set()
            부모_프레임.wait_window(직접입력_창)
    
    def 행_추가():
        """
        입력 필드의 값을 가져와 테이블에 추가하는 함수
        """
        # 주문번호 생성
        주문번호 = 새_주문번호_생성()
        
        # 입력 필드 값 가져오기
        행_데이터 = {'[주문번호]': 주문번호}
        
        # 모든 필드에 대해 값 가져오기 (빈 값 허용)
        for 필드명, 필드 in 입력_필드.items():
            if isinstance(필드, ttk.Combobox):
                값 = 필드.get()
            else:
                값 = 필드.get()
            행_데이터[필드명] = 값
        
        # 수량 필드 검증 (값이 있는 경우에만)
        if 행_데이터['[수량]'] and not 행_데이터['[수량]'].isdigit():
            messagebox.showerror("입력 오류", "수량은 숫자만 입력 가능합니다.")
            입력_필드['[수량]'].focus_set()
            return
        
        # 수량이 비어있으면 기본값 '1'로 설정
        if not 행_데이터['[수량]']:
            행_데이터['[수량]'] = '1'
        
        # 트리뷰에 행 추가
        values = ["[-]"]
        for 헤더명 in 헤더:
            values.append(행_데이터.get(헤더명, ""))
        
        tree.insert('', 'end', values=values)
        
        # 입력 필드 초기화
        for 필드 in 입력_필드.values():
            if isinstance(필드, ttk.Combobox):
                필드.set('')
            else:
                필드.delete(0, tk.END)
        
        # 첫 번째 입력 필드에 포커스 설정
        list(입력_필드.values())[0].focus_set()
        
        return 주문번호
    
    def 행_복사():
        """선택한 행 복사"""
        선택된_항목 = tree.selection()
        
        if not 선택된_항목:
            messagebox.showinfo("알림", "복사할 행을 선택해주세요.")
            return
            
        # 선택된 항목의 값 가져오기
        선택된_값 = tree.item(선택된_항목[0], 'values')
        
        # 새 주문번호 생성 및 값 업데이트
        주문번호 = 새_주문번호_생성()
        새_값 = ["[-]", 주문번호] + list(선택된_값[2:])  # 두 번째 값부터 복사 (삭제 버튼과 주문번호 제외)
        
        # 트리뷰에 행 추가
        tree.insert('', 'end', values=새_값)
    
    def CSV_생성():
        """테이블의 데이터로 CSV 파일 생성"""
        # 테이블의 모든 항목 가져오기
        모든_항목 = tree.get_children()
        
        if not 모든_항목:
            messagebox.showinfo("알림", "데이터가 없습니다. 행을 추가해주세요.")
            return
            
        # 현재 작업 디렉토리 경로 가져오기
        현재_폴더 = os.getcwd()
        
        # files 폴더 경로 설정 및 생성
        files_폴더 = os.path.join(현재_폴더, "files")
        if not os.path.exists(files_폴더):
            os.makedirs(files_폴더)
        
        # 오늘 날짜 폴더 생성 (files 폴더 내에)
        날짜_폴더 = os.path.join(files_폴더, 오늘날짜)
        if not os.path.exists(날짜_폴더):
            os.makedirs(날짜_폴더)
        
        # 기본 CSV 파일명 생성 (오늘 날짜 기준)
        기본_파일명 = f"{오늘날짜}_라라스토어_이지어드민 출고요청(수기).csv"
        
        # 파일명 중복 방지 처리
        파일명 = 기본_파일명
        파일_경로 = os.path.join(날짜_폴더, 파일명)
        파일_번호 = 1
        
        # 파일이 이미 존재하는 경우 번호 붙여서 새 파일명 생성
        while os.path.exists(파일_경로):
            파일명 = f"{오늘날짜}_라라스토어_이지어드민 출고요청(수기)_{파일_번호}.csv"
            파일_경로 = os.path.join(날짜_폴더, 파일명)
            파일_번호 += 1
        
        try:
            # 디버그용 출력 추가
            print(f"저장할 헤더: {헤더}")
            
            with open(파일_경로, 'w', newline='', encoding='euc-kr') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                
                # 헤더 쓰기 (원래 헤더 사용)
                writer.writerow(헤더)
                
                # 데이터 쓰기 (삭제 버튼 열 제외)
                for item in 모든_항목:
                    원본_데이터 = tree.item(item, 'values')
                    print(f"원본 데이터: {원본_데이터}")
                    
                    # 첫번째 열(삭제 버튼) 제외하고 헤더 길이에 맞게 조정
                    행_데이터 = list(원본_데이터[1:])
                    
                    # 행 데이터 길이가 헤더 길이와 일치하는지 확인 후 조정
                    if len(행_데이터) > len(헤더):
                        행_데이터 = 행_데이터[:len(헤더)]
                    elif len(행_데이터) < len(헤더):
                        행_데이터.extend([""] * (len(헤더) - len(행_데이터)))
                    
                    print(f"저장할 데이터: {행_데이터}")
                    writer.writerow(행_데이터)
                
            messagebox.showinfo("CSV 생성 완료", f"'{파일명}' 파일이 files/{오늘날짜} 폴더에 생성되었습니다.")
            
            # 상태 업데이트
            if 상태_콜백:
                상태_콜백(f"CSV 파일 '{파일명}'이 files/{오늘날짜} 폴더에 생성되었습니다.")
            
            # 저장 폴더 열기 (날짜 폴더)
            현재_OS = platform.system()
            if 현재_OS == "Windows":
                os.startfile(날짜_폴더)
            elif 현재_OS == "Darwin":  # macOS
                subprocess.Popen(["open", 날짜_폴더])
            else:  # Linux 등
                subprocess.Popen(["xdg-open", 날짜_폴더])
            
            return 파일_경로  # 생성된 파일 경로 반환
            
        except Exception as e:
            오류_메시지 = f"CSV 파일 생성 중 오류 발생: {str(e)}"
            messagebox.showerror("오류", 오류_메시지)
            print(f"CSV 생성 오류: {str(e)}")
            return None
    
    # 버튼 프레임
    버튼_프레임 = ttk.Frame(메인_프레임)
    버튼_프레임.pack(side="top", fill="x", pady=5)
    
    # 공통 버튼 스타일 정의
    버튼_스타일 = {"width": 12, "padding": 5}
    
    # 이지어드민 사이트 열기 함수
    def 이지어드민_열기():
        webbrowser.open("https://www.ezadmin.co.kr/index.html")
    
    # CSV 생성 버튼 - 왼쪽으로 이동 (스타일 적용)
    CSV생성_버튼 = ttk.Button(버튼_프레임, text="CSV 생성하기", command=CSV_생성, **버튼_스타일)
    CSV생성_버튼.pack(side="left", padx=5)
    
    # 이지어드민 버튼 - CSV 생성 버튼 옆에 배치
    이지어드민_버튼 = ttk.Button(버튼_프레임, text="이지어드민", command=이지어드민_열기, **버튼_스타일)
    이지어드민_버튼.pack(side="left", padx=5)
    
    # 데이터 추가 및 복사 버튼 - 오른쪽으로 이동 (스타일 적용)
    데이터추가_버튼 = ttk.Button(버튼_프레임, text="데이터 추가", command=lambda: 행_추가(), **버튼_스타일)
    데이터추가_버튼.pack(side="right", padx=5)
    
    복사_버튼 = ttk.Button(버튼_프레임, text="복사하기", command=행_복사, **버튼_스타일)
    복사_버튼.pack(side="right", padx=5)
    복사_버튼.configure(style='Custom.TButton')
    
    # 버튼 스타일 설정
    스타일 = ttk.Style()
    스타일.configure('Custom.TButton', font=('Helvetica', 10), padding=5)
    
    if 상태_콜백:
        상태_콜백("수기출고 테이블이 생성되었습니다.")
    
    return "수기출고 테이블이 생성되었습니다."
