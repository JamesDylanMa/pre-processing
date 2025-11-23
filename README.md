# 문서 전처리 서비스 (Document Preprocessing Service)

다양한 형식의 문서 파일을 업로드하고 여러 전처리 모듈을 통해 처리한 후, 결과를 비교 분석하여 최적의 전처리 방법을 추천하는 서비스입니다.

## 주요 기능

- 📄 **다양한 파일 형식 지원**: PDF, Word, Excel, PowerPoint, 텍스트, 이미지
- 🔄 **다중 전처리 모듈**: 여러 파서와 Document AI를 통한 전처리
- 🤖 **Ollama 통합**: Multi-modal AI 모델을 활용한 고급 문서 처리
- 📊 **결과 비교 분석**: 여러 전처리 결과를 비교하여 최적의 방법 추천
- 🎯 **앙상블 처리**: 여러 처리기를 조합한 복합 처리 지원
- 💾 **다양한 출력 형식**: JSON, Markdown 형식으로 결과 저장 및 다운로드
- 🔍 **고급 OCR**: EasyOCR 지원 (80+ 언어, 외부 의존성 없음)
- 📋 **구조화된 데이터 추출**: Unstructured 라이브러리로 문서 구조 분석
- ✨ **텍스트 큐레이션**: NeMo Curator 기반 품질 필터링, 중복 제거, 텍스트 정리, 언어 감지

## 프로젝트 구조

```
pre-processing/
├── backend/              # Backend 레이어
│   ├── file_upload.py   # 파일 업로드 처리
│   ├── storage.py       # 결과 저장 관리
│   └── api.py           # API 엔드포인트 (향후 확장)
├── frontend/            # Frontend 레이어
│   └── streamlit_app.py # Streamlit 웹 애플리케이션
├── processing/           # Processing 레이어
│   ├── parsers/         # 문서 파서 모듈
│   │   ├── pdf_parser.py
│   │   ├── pdf_pymupdf_parser.py
│   │   ├── pdf_pdfminer_parser.py
│   │   ├── pdf_pypdf_parser.py
│   │   ├── pdf_easyocr_parser.py  # EasyOCR (새로 추가)
│   │   ├── pdf_unstructured_parser.py  # Unstructured (새로 추가)
│   │   ├── pdf_pdfquery_parser.py  # PDFQuery (새로 추가)
│   │   ├── pdf_ocr_parser.py
│   │   ├── pdf_camelot_parser.py
│   │   ├── pdf_tabula_parser.py
│   │   ├── word_parser.py
│   │   ├── excel_parser.py
│   │   └── ppt_parser.py
│   ├── processors/      # 문서 처리 모듈
│   │   ├── base_processor.py
│   │   ├── document_ai.py
│   │   └── ensemble_processor.py
│   ├── ollama_integration.py  # Ollama 통합
│   └── comparison.py    # 결과 비교 모듈
├── utils/               # 유틸리티 함수
│   └── file_utils.py
├── config.py            # 설정 파일
├── requirements.txt     # Python 패키지 의존성
├── README.md           # 프로젝트 설명서
└── MANUAL.md           # 사용 매뉴얼
```

## 설치 방법

### 1. 필수 요구사항

- Python 3.8 이상
- pip 패키지 관리자

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 선택적 의존성 설치

#### OCR 지원 (선택사항)

**EasyOCR (권장)**: 외부 의존성 없이 바로 사용 가능
```bash
# requirements.txt에 이미 포함되어 있음
pip install easyocr pdf2image
```

**Tesseract OCR (대안)**: 더 많은 언어 지원, 하지만 별도 설치 필요
- Windows: [Tesseract 설치 가이드](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux: `sudo apt-get install tesseract-ocr`
- Mac: `brew install tesseract`

#### 테이블 추출 (선택사항)

**Camelot** (Java 필요):
```bash
pip install camelot-py[cv]
# Java 설치 필요
```

**Tabula** (Java 필요):
```bash
pip install tabula-py
# Java 설치 필요
```

### 4. Ollama 설치 (선택사항)

Ollama를 사용하려면 별도로 설치해야 합니다:

```bash
# Windows (PowerShell)
winget install Ollama.Ollama

# 또는 공식 웹사이트에서 다운로드
# https://ollama.ai/download
```

Ollama 설치 후 모델 다운로드:

```bash
# 권장 모델 (Multi-modal)
ollama pull llava

# 또는 다른 모델
ollama pull llama3
ollama pull mistral
```

## 실행 방법

### 기본 실행

```bash
streamlit run frontend/streamlit_app.py
```

브라우저에서 자동으로 열리며, 기본 주소는 `http://localhost:8501`입니다.

### 포트 변경

```bash
streamlit run frontend/streamlit_app.py --server.port 8502
```

## 사용 방법

1. **파일 업로드**: 웹 인터페이스에서 지원되는 형식의 파일을 업로드합니다.
2. **처리 옵션 선택**: 사이드바에서 처리 옵션을 선택합니다.
   - 앙상블 처리 사용 여부
   - 결과 비교 활성화
   - Ollama AI 처리 사용
3. **처리 시작**: "파일 업로드 및 처리 시작" 버튼을 클릭합니다.
4. **결과 확인**: 
   - "처리 결과" 탭에서 각 처리기의 결과를 확인합니다.
   - "비교 분석" 탭에서 최적의 처리기를 확인합니다.
   - "다운로드" 탭에서 결과 파일을 다운로드합니다.

## 지원 파일 형식

- **PDF**: `.pdf`
- **Word**: `.doc`, `.docx`
- **Excel**: `.xls`, `.xlsx`, `.xlsm`
- **PowerPoint**: `.ppt`, `.pptx`
- **텍스트**: `.txt`, `.md`
- **이미지**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`

## 지원하는 PDF 파서

### 기본 파서 (항상 사용 가능)
- **pdfplumber**: 텍스트 및 테이블 추출에 우수
- **PyMuPDF (fitz)**: 빠르고 정확한 텍스트 추출
- **pdfminer.six**: 레이아웃 정보를 포함한 텍스트 추출
- **pypdf**: PyPDF2의 현대적 후속작

### OCR 파서 (스캔된 PDF용)
- **EasyOCR** (권장): 80+ 언어 지원, 외부 의존성 없음, 더 나은 정확도
- **Tesseract OCR**: 전통적인 OCR 엔진, 더 많은 언어 지원 (별도 설치 필요)

### 고급 파서
- **Unstructured**: 구조화되지 않은 문서에서 구조화된 데이터 추출
- **PDFQuery**: CSS-like selector를 사용한 구조화된 PDF 데이터 추출

### 테이블 추출 파서 (선택사항, Java 필요)
- **Camelot**: 테이블 추출에 특화
- **Tabula**: 다양한 테이블 형식 지원

## Ollama 모델 추천

### Multi-modal 모델 (이미지 처리 포함)
- **llava**: 가장 권장되는 모델 (균형잡힌 성능)
- **bakllava**: 더 큰 컨텍스트 윈도우
- **llava-phi3**: 경량화된 버전

### 텍스트 전용 모델
- **llama3**: 최신 Llama 모델
- **mistral**: 빠른 응답 속도
- **phi3**: 경량화된 모델

## 환경 변수 설정

환경 변수를 설정하여 애플리케이션 동작을 커스터마이징할 수 있습니다.

### 방법 1: 환경 변수 직접 설정

```bash
# Linux/Mac
export OLLAMA_BASE_URL=http://localhost:11434

# Windows PowerShell
$env:OLLAMA_BASE_URL="http://localhost:11434"

# Windows CMD
set OLLAMA_BASE_URL=http://localhost:11434
```

### 방법 2: .env 파일 사용

`.env` 파일을 프로젝트 루트에 생성하여 설정할 수 있습니다:

```env
OLLAMA_BASE_URL=http://localhost:11434
```

**참고**: `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다.

### 방법 3: config.py에서 직접 수정

`config.py` 파일에서 직접 설정 값을 수정할 수 있습니다.

### 주요 환경 변수

- `OLLAMA_BASE_URL`: Ollama 서버 URL (기본값: `http://localhost:11434`)

## Docker를 사용한 배포

### Docker Compose 사용 (권장)

가장 간단한 방법으로, Ollama를 포함한 전체 스택을 실행합니다:

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### Docker 단독 사용

```bash
# 이미지 빌드
docker build -t document-preprocessing .

# 컨테이너 실행
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/cache:/app/cache \
  --name doc-preprocessing \
  document-preprocessing

# 로그 확인
docker logs -f doc-preprocessing

# 컨테이너 중지
docker stop doc-preprocessing
docker rm doc-preprocessing
```

### 배포 스크립트 사용

#### Linux/Mac

```bash
# 실행 권한 부여
chmod +x deploy.sh

# 일반 모드 실행
./deploy.sh

# Docker 모드 실행
./deploy.sh --docker

# Docker Compose 모드 실행
./deploy.sh --compose

# 포트 변경
./deploy.sh --port 8502
```

#### Windows PowerShell

```powershell
# 일반 모드 실행
.\deploy.ps1

# Docker 모드 실행
.\deploy.ps1 -Docker

# Docker Compose 모드 실행
.\deploy.ps1 -Compose

# 포트 변경
.\deploy.ps1 -Port 8502
```

## 다른 서버로 배포

### 1. 파일 전송

프로젝트 전체 디렉토리를 대상 서버로 전송합니다:

```bash
# SCP 사용 예시 (Linux/Mac)
scp -r pre-processing/ user@server:/path/to/destination/

# 또는 압축 후 전송
tar -czf pre-processing.tar.gz pre-processing/
scp pre-processing.tar.gz user@server:/path/to/destination/
```

### 2. 서버에서 설정

```bash
# 디렉토리 이동
cd /path/to/destination/pre-processing

# 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 3. 실행

```bash
streamlit run frontend/streamlit_app.py
```

### 4. 백그라운드 실행 (Linux)

```bash
# nohup 사용
nohup streamlit run frontend/streamlit_app.py > streamlit.log 2>&1 &

# 또는 systemd 서비스로 등록 (선택사항)
```

자세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참조하세요.

## 문제 해결

### Ollama 연결 오류

- Ollama 서비스가 실행 중인지 확인: `ollama list`
- `config.py`의 `OLLAMA_BASE_URL`이 올바른지 확인
- 방화벽 설정 확인

### 파일 업로드 오류

- 파일 크기 제한 확인 (기본 100MB)
- 지원되는 파일 형식인지 확인
- 디스크 공간 확인

### 패키지 설치 오류

- Python 버전 확인 (3.8 이상 필요)
- pip 업그레이드: `pip install --upgrade pip`
- 개별 패키지 설치 시도

### 파서 오류

- **Camelot/Tabula 오류**: Java가 설치되어 있는지 확인
- **OCR 오류**: Tesseract 또는 EasyOCR이 제대로 설치되었는지 확인
- **Unstructured 오류**: 필요한 의존성이 모두 설치되었는지 확인

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.

## 연락처

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.
