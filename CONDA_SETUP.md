# Anaconda 가상환경 설정 및 실행 가이드

## 가상환경 생성 완료

Anaconda 가상환경 `pre-processing`이 성공적으로 생성되었습니다.

- **환경 이름**: pre-processing
- **Python 버전**: 3.9.25
- **위치**: `C:\Users\elect\.conda\envs\pre-processing`

## 필요한 패키지 설치 완료

다음 패키지들이 설치되었습니다:
- streamlit
- pandas, numpy
- PyPDF2, pdfplumber
- python-docx, openpyxl, python-pptx
- requests
- 기타 의존성 패키지들

## 애플리케이션 실행 방법

### 방법 1: 배치 파일 사용 (Windows)

```bash
run_conda.bat
```

### 방법 2: PowerShell 스크립트 사용

```powershell
.\run_conda.ps1
```

### 방법 3: 수동 실행

#### Anaconda Prompt 사용 (권장)

1. **Anaconda Prompt**를 관리자 권한으로 실행
2. 다음 명령어 실행:

```bash
conda activate pre-processing
cd C:\Users\elect\pre-processing
streamlit run frontend/streamlit_app.py
```

#### PowerShell에서 직접 실행

```powershell
# 가상환경 Python 경로 사용
& "$env:USERPROFILE\.conda\envs\pre-processing\Scripts\streamlit.exe" run frontend/streamlit_app.py
```

## 접속 방법

애플리케이션이 실행되면 브라우저에서 자동으로 열립니다. 
수동으로 접속하려면:

```
http://localhost:8501
```

## 가상환경 관리

### 가상환경 활성화

```bash
conda activate pre-processing
```

### 가상환경 비활성화

```bash
conda deactivate
```

### 가상환경 목록 확인

```bash
conda env list
```

### 패키지 목록 확인

```bash
conda list
```

또는

```bash
pip list
```

### 패키지 업데이트

```bash
conda activate pre-processing
pip install --upgrade -r requirements.txt
```

## 문제 해결

### 포트가 이미 사용 중인 경우

다른 포트로 실행:

```bash
streamlit run frontend/streamlit_app.py --server.port=8502
```

### 가상환경을 찾을 수 없는 경우

```bash
conda env list
```

위 명령어로 가상환경 목록을 확인하고, 경로를 확인하세요.

### 패키지 설치 오류

가상환경을 다시 활성화하고 설치:

```bash
conda activate pre-processing
pip install --upgrade pip
pip install -r requirements.txt
```

## 다음 단계

1. 애플리케이션 실행
2. 웹 브라우저에서 `http://localhost:8501` 접속
3. 파일 업로드 및 처리 테스트
4. Ollama 설정 (선택사항)

## Ollama 설정 (선택사항)

Ollama를 사용하려면:

1. Ollama 설치: https://ollama.ai/download
2. 모델 다운로드:
   ```bash
   ollama pull llava
   ollama pull llama3
   ```
3. Ollama 서비스 실행 확인:
   ```bash
   ollama list
   ```

## 참고사항

- 가상환경은 `C:\Users\elect\.conda\envs\pre-processing`에 저장됩니다
- 프로젝트 파일은 `C:\Users\elect\pre-processing`에 있습니다
- 실행 스크립트(`run_conda.bat`, `run_conda.ps1`)를 사용하면 쉽게 실행할 수 있습니다

