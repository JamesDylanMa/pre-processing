# 프로젝트 구조 설명

## 전체 구조

```
pre-processing/
├── backend/                    # Backend 레이어
│   ├── __init__.py
│   ├── file_upload.py         # 파일 업로드 처리 모듈
│   └── storage.py             # 결과 저장 관리 모듈
│
├── frontend/                   # Frontend 레이어
│   ├── __init__.py
│   └── streamlit_app.py       # Streamlit 웹 애플리케이션
│
├── processing/                 # Processing 레이어
│   ├── __init__.py
│   ├── parsers/               # 문서 파서 모듈
│   │   ├── __init__.py
│   │   ├── pdf_parser.py      # PDF 파서
│   │   ├── word_parser.py     # Word 파서
│   │   ├── excel_parser.py    # Excel 파서
│   │   └── ppt_parser.py      # PowerPoint 파서
│   │
│   ├── processors/            # 문서 처리 모듈
│   │   ├── __init__.py
│   │   ├── base_processor.py  # 기본 프로세서 (추상 클래스)
│   │   ├── document_ai.py     # Document AI 프로세서
│   │   └── ensemble_processor.py  # 앙상블 프로세서
│   │
│   ├── ollama_integration.py   # Ollama 통합 모듈
│   └── comparison.py          # 결과 비교 모듈
│
├── utils/                      # 유틸리티 함수
│   ├── __init__.py
│   └── file_utils.py          # 파일 관련 유틸리티
│
├── config.py                   # 설정 파일
├── run.py                      # 실행 스크립트
├── requirements.txt            # Python 패키지 의존성
├── Dockerfile                  # Docker 이미지 빌드 파일
├── docker-compose.yml          # Docker Compose 설정
├── .gitignore                  # Git 제외 파일 목록
├── README.md                   # 프로젝트 설명서
├── MANUAL.md                   # 사용 매뉴얼
├── DEPLOYMENT.md               # 배포 가이드
└── PROJECT_STRUCTURE.md        # 이 파일
```

## 레이어별 설명

### Backend 레이어 (`backend/`)

백엔드 로직을 담당하는 모듈들입니다.

- **file_upload.py**: 파일 업로드 처리, 검증, 메타데이터 생성
- **storage.py**: 처리 결과의 저장, 로드, 관리

### Frontend 레이어 (`frontend/`)

사용자 인터페이스를 제공하는 Streamlit 애플리케이션입니다.

- **streamlit_app.py**: 메인 웹 애플리케이션
  - 파일 업로드 인터페이스
  - 처리 결과 표시
  - 비교 분석 표시
  - 다운로드 기능

### Processing 레이어 (`processing/`)

문서 처리의 핵심 로직을 담당합니다.

#### Parsers (`processing/parsers/`)

다양한 파일 형식을 파싱하는 모듈들입니다.

- **pdf_parser.py**: PyPDF2와 pdfplumber를 사용한 PDF 파싱
- **word_parser.py**: python-docx를 사용한 Word 문서 파싱
- **excel_parser.py**: pandas를 사용한 Excel 파일 파싱
- **ppt_parser.py**: python-pptx를 사용한 PowerPoint 파싱

#### Processors (`processing/processors/`)

파싱된 문서를 추가로 처리하는 모듈들입니다.

- **base_processor.py**: 모든 프로세서의 기본 클래스 (추상 클래스)
- **document_ai.py**: AI 기반 문서 처리 및 통계 생성
- **ensemble_processor.py**: 여러 프로세서의 결과를 결합

#### 기타 모듈

- **ollama_integration.py**: Ollama API를 통한 AI 모델 통합
- **comparison.py**: 여러 처리 결과를 비교하고 최적의 방법 추천

### Utils 레이어 (`utils/`)

공통 유틸리티 함수들입니다.

- **file_utils.py**: 파일 타입 감지, 해시 생성, MIME 타입 확인 등

## 데이터 흐름

```
1. 사용자 파일 업로드
   ↓
2. FileUploadHandler: 파일 검증 및 저장
   ↓
3. 적절한 Parser 선택 및 파싱
   ↓
4. Processor를 통한 추가 처리 (선택사항)
   - DocumentAIProcessor
   - EnsembleProcessor
   - OllamaProcessor
   ↓
5. ResultComparator: 결과 비교 (여러 결과가 있는 경우)
   ↓
6. StorageManager: 결과 저장 (JSON/Markdown)
   ↓
7. 사용자에게 결과 표시 및 다운로드 제공
```

## 주요 설정 파일

### config.py

전역 설정을 관리합니다:
- 디렉토리 경로 (uploads, outputs, cache)
- 지원 파일 형식
- Ollama 설정
- 처리 옵션

### requirements.txt

필수 Python 패키지 목록:
- Streamlit: 웹 프레임워크
- 문서 파싱 라이브러리들
- 데이터 처리 라이브러리들

## 확장 가능성

### 새로운 파서 추가

1. `processing/parsers/`에 새 파서 클래스 생성
2. `base_processor.py`의 `parsers` 딕셔너리에 추가
3. `config.py`의 `ALLOWED_EXTENSIONS`에 파일 형식 추가

### 새로운 프로세서 추가

1. `processing/processors/`에 `BaseProcessor`를 상속받는 새 클래스 생성
2. `process()` 메서드 구현
3. `streamlit_app.py`에서 사용

### 새로운 출력 형식 추가

1. `StorageManager.save_result()` 메서드에 새 형식 처리 로직 추가
2. `config.py`의 `OUTPUT_FORMATS`에 추가

## 파일 크기 및 성능 고려사항

- **메모리 사용**: 큰 파일 처리 시 메모리 사용량 증가
- **처리 시간**: 파일 크기와 복잡도에 비례
- **동시 처리**: 현재는 단일 파일 처리만 지원 (향후 확장 가능)

## 보안 고려사항

- 파일 크기 제한 (`MAX_FILE_SIZE`)
- 파일 형식 검증
- 업로드 디렉토리 권한 관리
- 사용자 입력 검증


