# 피그마 이미지 자동 요소 분리 도구 - 완전 가이드

## 🎯 개요

이 프로젝트는 피그마에 업로드된 이미지를 GPT-4o API로 분석하여 UI 요소들을 자동으로 분리하고 편집 가능한 피그마 컴포넌트로 변환하는 도구입니다.

## 📁 프로젝트 구조

```
figma_mcp/
├── cursor-talk-to-figma-mcp/          # MCP 서버
│   ├── src/talk_to_figma_mcp/
│   │   └── server.ts                  # 확장된 MCP 서버 (AI 분석 기능 포함)
│   ├── env.template                   # 환경 변수 템플릿
│   └── package.json
├── goya_figam_test/                   # PowerShell 스크립트들
│   ├── auto_image_analyzer.ps1        # 메인 분석 도구
│   ├── batch_image_analyzer.ps1       # 배치 분석 도구
│   ├── setup_environment.ps1          # 환경 설정 스크립트
│   ├── test_ai_analyzer.ps1           # 테스트 스크립트
│   ├── get_layers.ps1                 # 기존 레이어 조회 스크립트
│   └── README_auto_analyzer.md        # 상세 사용법
└── FIGMA_AI_ANALYZER_GUIDE.md         # 이 파일
```

## 🚀 빠른 시작

### 1. 사전 요구사항

- **OpenAI API 키**: GPT-4o 모델 사용을 위한 API 키
- **Node.js**: MCP 서버 실행용
- **PowerShell**: Windows PowerShell 5.1 이상
- **피그마**: 피그마 데스크톱 앱 또는 웹 버전

### 2. 설치 및 설정

```bash
# 1. 환경 변수 설정
cd cursor-talk-to-figma-mcp
cp env.template .env
# .env 파일을 편집하여 OpenAI API 키 설정

# 2. MCP 서버 의존성 설치
npm install

# 3. MCP 서버 실행
npm start
```

### 3. 환경 설정 확인

```powershell
# PowerShell에서 환경 설정 확인
cd goya_figam_test
.\setup_environment.ps1
```

### 4. 기본 사용법

```powershell
# 1. 피그마에서 이미지를 선택
# 2. 스크립트 실행
.\auto_image_analyzer.ps1
```

## 🛠️ 주요 기능

### 1. 자동 이미지 분석
- GPT-4o API를 사용한 고급 이미지 분석
- 텍스트, 버튼, 입력 필드, 카드 등 UI 요소 자동 감지
- 정확한 위치, 크기, 색상 정보 추출

### 2. 요소 자동 생성
- 분석 결과를 바탕으로 피그마 요소 자동 생성
- 원본 이미지와 동일한 위치에 배치
- 색상, 폰트, 코너 반지름 등 스타일 자동 적용

### 3. 편집 가능한 컴포넌트
- 생성된 모든 요소는 피그마에서 편집 가능
- 텍스트 내용 수정 가능
- 색상, 크기, 위치 조정 가능

## 📋 사용 가능한 스크립트

### 1. `auto_image_analyzer.ps1` (메인 도구)
```powershell
# 기본 사용법
.\auto_image_analyzer.ps1

# 고급 옵션
.\auto_image_analyzer.ps1 -Channel "custom_channel" -OpenAIAPIKey "sk-..." -SkipConfirmation
```

**주요 기능:**
- 단일 이미지 분석 및 요소 생성
- GPT-4o API를 사용한 고급 분석
- 자동 요소 생성 및 스타일 적용

### 2. `batch_image_analyzer.ps1` (배치 처리)
```powershell
# 배치 분석
.\batch_image_analyzer.ps1 -DelaySeconds 5
```

**주요 기능:**
- 여러 이미지를 연속으로 분석
- 사용자 상호작용으로 진행
- 지연 시간 설정 가능

### 3. `setup_environment.ps1` (환경 설정)
```powershell
# 환경 설정 확인
.\setup_environment.ps1 -Force
```

**주요 기능:**
- 환경 변수 설정 확인
- MCP 서버 연결 테스트
- 필요한 모듈 확인
- 실행 권한 확인

### 4. `test_ai_analyzer.ps1` (테스트)
```powershell
# 전체 시스템 테스트
.\test_ai_analyzer.ps1 -TestOnly

# 실제 분석 포함 테스트
.\test_ai_analyzer.ps1
```

**주요 기능:**
- WebSocket 연결 테스트
- OpenAI API 연결 테스트
- 전체 워크플로우 테스트

## 🔧 MCP 서버 확장 기능

### 새로운 도구: `analyze_image_with_ai`

MCP 서버에 추가된 새로운 도구로, Cursor IDE에서 직접 사용할 수 있습니다:

```typescript
// Cursor IDE에서 사용 예시
const result = await analyze_image_with_ai({
  nodeId: "selected_node_id", // 선택사항
  openaiApiKey: "sk-...",
  createElements: true,
  analysisPrompt: "특별한 분석 요청" // 선택사항
});
```

**주요 기능:**
- 이미지 노드 자동 분석
- GPT-4o를 사용한 UI 요소 추출
- 피그마 요소 자동 생성
- 커스텀 분석 프롬프트 지원

## 📊 분석 결과 예시

### 입력 이미지
- 로그인 화면 스크린샷
- 모바일 앱 인터페이스
- 웹사이트 목업

### 분석 결과
```json
{
  "elements": [
    {
      "type": "text",
      "content": "Welcome Back",
      "position": {"x": 50, "y": 30},
      "size": {"width": 200, "height": 24},
      "color": {"r": 0.2, "g": 0.2, "b": 0.2, "a": 1},
      "fontSize": 24,
      "fontWeight": 600
    },
    {
      "type": "button",
      "content": "Sign In",
      "position": {"x": 50, "y": 200},
      "size": {"width": 120, "height": 40},
      "color": {"r": 0.1, "g": 0.5, "b": 1, "a": 1},
      "cornerRadius": 8,
      "interactive": true
    }
  ],
  "layout": {
    "width": 375,
    "height": 667,
    "background": {"r": 1, "g": 1, "b": 1, "a": 1}
  },
  "metadata": {
    "totalElements": 5,
    "primaryColors": ["#1a73e8", "#ffffff"],
    "designSystem": "material"
  }
}
```

### 생성되는 피그마 요소
- **텍스트 요소**: "Welcome Back" (폰트 크기 24, 굵게)
- **버튼**: "Sign In" (파란색 배경, 8px 모서리 둥글게)
- **입력 필드**: 이메일/비밀번호 입력창
- **배경 프레임**: 전체 레이아웃 컨테이너

## 🚨 문제 해결

### 1. API 키 오류
```
오류: OpenAI API 키가 설정되지 않았습니다.
```
**해결방법:**
- `.env` 파일에 올바른 API 키 설정
- API 키가 유효한지 확인
- 사용량 한도 확인

### 2. MCP 서버 연결 오류
```
오류: MCP 서버에 연결할 수 없습니다.
```
**해결방법:**
- MCP 서버가 실행 중인지 확인: `npm start`
- 포트 3055가 사용 가능한지 확인
- 방화벽 설정 확인

### 3. 피그마 연결 오류
```
오류: 피그마에서 이미지를 선택해주세요.
```
**해결방법:**
- 피그마에서 이미지 요소 선택
- 피그마 플러그인이 설치되었는지 확인
- 채널명이 올바른지 확인

### 4. 이미지 분석 실패
```
오류: 이미지 분석에 실패했습니다.
```
**해결방법:**
- 이미지 크기가 적절한지 확인
- 이미지가 명확한 UI 요소를 포함하는지 확인
- 네트워크 연결 상태 확인

## 📈 성능 최적화

### 1. 이미지 크기 최적화
- 너무 큰 이미지는 분석 시간이 오래 걸림
- 권장 크기: 1000x1000 픽셀 이하

### 2. 배치 처리
- 여러 이미지를 연속으로 처리할 때는 `batch_image_analyzer.ps1` 사용
- API 사용량을 고려하여 적절한 지연 시간 설정

### 3. API 사용량 관리
- GPT-4o API는 사용량에 따라 비용 발생
- 필요에 따라 `createElements: false`로 분석만 수행

## 🔄 업데이트 및 확장

### 버전 1.0.0 기능
- ✅ 기본 이미지 분석
- ✅ 텍스트, 버튼, 사각형 요소 생성
- ✅ 색상 및 스타일 자동 적용
- ✅ MCP 서버 통합

### 향후 계획
- 🔄 더 많은 UI 요소 유형 지원
- 🔄 레이어 그룹핑 자동화
- 🔄 컴포넌트 라이브러리 연동
- 🔄 실시간 협업 기능

## 📞 지원 및 기여

### 문제 신고
- GitHub Issues를 통해 버그 신고
- 개선 제안 환영

### 기여 방법
1. 프로젝트 포크
2. 기능 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**주의사항**: 
- GPT-4o API 사용량에 따라 비용이 발생할 수 있습니다
- API 키를 안전하게 보관하세요
- 네트워크 연결이 안정적인 환경에서 사용하세요

**최종 업데이트**: 2024년 12월
