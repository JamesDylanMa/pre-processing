# 배포 가이드

이 문서는 문서 전처리 서비스를 다른 서버로 배포하는 방법을 설명합니다.

## 목차

1. [배포 전 준비사항](#배포-전-준비사항)
2. [로컬 서버 배포](#로컬-서버-배포)
3. [원격 서버 배포](#원격-서버-배포)
4. [Docker를 이용한 배포](#docker를-이용한-배포)
5. [서비스 자동 시작 설정](#서비스-자동-시작-설정)
6. [모니터링 및 로그](#모니터링-및-로그)

## 배포 전 준비사항

### 1. 프로젝트 파일 확인

배포할 프로젝트에 다음 파일들이 포함되어 있는지 확인하세요:

```
pre-processing/
├── backend/
├── frontend/
├── processing/
├── utils/
├── config.py
├── requirements.txt
├── README.md
├── MANUAL.md
└── run.py
```

### 2. 필수 파일 패키징

배포를 위해 프로젝트를 압축할 수 있습니다:

```bash
# Windows (PowerShell)
Compress-Archive -Path pre-processing -DestinationPath pre-processing.zip

# Linux/Mac
tar -czf pre-processing.tar.gz pre-processing/
```

### 3. 배포 스크립트 사용 (권장)

프로젝트에 포함된 배포 스크립트를 사용하면 더 쉽게 배포할 수 있습니다.

#### Linux/Mac

```bash
# 실행 권한 부여 (최초 1회)
chmod +x deploy.sh

# 일반 모드 실행
./deploy.sh

# Docker 모드 실행
./deploy.sh --docker

# Docker Compose 모드 실행 (Ollama 포함)
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

# Docker Compose 모드 실행 (Ollama 포함)
.\deploy.ps1 -Compose

# 포트 변경
.\deploy.ps1 -Port 8502
```

## 로컬 서버 배포

### Windows

1. **프로젝트 디렉토리로 이동**
   ```powershell
   cd C:\path\to\pre-processing
   ```

2. **가상 환경 생성 및 활성화**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **패키지 설치**
   ```powershell
   pip install -r requirements.txt
   ```

4. **애플리케이션 실행**
   ```powershell
   streamlit run frontend/streamlit_app.py
   ```

### Linux/Mac

1. **프로젝트 디렉토리로 이동**
   ```bash
   cd /path/to/pre-processing
   ```

2. **가상 환경 생성 및 활성화**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **애플리케이션 실행**
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

## 원격 서버 배포

### 1. 파일 전송

#### SCP 사용 (Linux/Mac)

```bash
# 디렉토리 전체 전송
scp -r pre-processing/ user@server:/path/to/destination/

# 압축 파일 전송
scp pre-processing.tar.gz user@server:/path/to/destination/
```

#### WinSCP 사용 (Windows)

1. WinSCP를 다운로드하고 설치
2. 서버에 연결
3. 프로젝트 폴더를 드래그 앤 드롭하여 업로드

#### Git 사용 (권장)

```bash
# 서버에서
git clone https://github.com/your-repo/pre-processing.git
cd pre-processing
```

### 2. 서버에서 설정

```bash
# SSH로 서버 접속
ssh user@server

# 프로젝트 디렉토리로 이동
cd /path/to/pre-processing

# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Ollama 설정 (선택사항)

```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# 모델 다운로드
ollama pull llava
ollama pull llama3

# Ollama 서비스 시작
ollama serve
```

### 4. 애플리케이션 실행

#### 직접 실행

```bash
streamlit run frontend/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

#### 백그라운드 실행 (nohup)

```bash
nohup streamlit run frontend/streamlit_app.py > streamlit.log 2>&1 &
```

#### screen 사용

```bash
# screen 세션 생성
screen -S streamlit

# 애플리케이션 실행
streamlit run frontend/streamlit_app.py

# 세션에서 나가기 (Ctrl+A, D)
# 세션 다시 접속: screen -r streamlit
```

## Docker를 이용한 배포

### Dockerfile 생성

`Dockerfile` 파일을 프로젝트 루트에 생성:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 디렉토리 생성
RUN mkdir -p uploads outputs cache

# 포트 노출
EXPOSE 8501

# 애플리케이션 실행
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker 빌드 및 실행

```bash
# 이미지 빌드
docker build -t document-preprocessing .

# 컨테이너 실행
docker run -d \
  -p 8501:8501 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  --name doc-preprocessing \
  document-preprocessing

# 로그 확인
docker logs -f doc-preprocessing
```

### Docker Compose 사용 (권장)

프로젝트에 이미 `docker-compose.yml` 파일이 포함되어 있습니다. 배포 스크립트를 사용하거나 수동으로 실행할 수 있습니다:

#### 배포 스크립트 사용

```bash
# Linux/Mac
./deploy.sh --compose

# Windows PowerShell
.\deploy.ps1 -Compose
```

#### 수동 실행

`docker-compose.yml` 파일 내용:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
      - ./cache:/app/cache
    restart: unless-stopped
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

실행:

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down

# 재빌드 후 시작
docker-compose up -d --build
```

## 서비스 자동 시작 설정

### systemd 서비스 생성 (Linux)

`/etc/systemd/system/doc-preprocessing.service` 파일 생성:

```ini
[Unit]
Description=Document Preprocessing Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/pre-processing
Environment="PATH=/path/to/pre-processing/venv/bin"
ExecStart=/path/to/pre-processing/venv/bin/streamlit run frontend/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 활성화:

```bash
sudo systemctl daemon-reload
sudo systemctl enable doc-preprocessing
sudo systemctl start doc-preprocessing
sudo systemctl status doc-preprocessing
```

### Windows 서비스 (NSSM 사용)

1. NSSM 다운로드: https://nssm.cc/download
2. 서비스 설치:

```powershell
nssm install DocPreprocessing
# GUI에서 설정:
# Path: C:\path\to\venv\Scripts\streamlit.exe
# Arguments: run frontend/streamlit_app.py --server.port=8501
# Startup directory: C:\path\to\pre-processing
```

## 모니터링 및 로그

### 로그 확인

#### Streamlit 로그

```bash
# 직접 실행 시
tail -f streamlit.log

# systemd 서비스
sudo journalctl -u doc-preprocessing -f

# Docker
docker logs -f doc-preprocessing
```

### 성능 모니터링

```bash
# 프로세스 확인
ps aux | grep streamlit

# 포트 확인
netstat -tulpn | grep 8501
# 또는
lsof -i :8501

# 리소스 사용량
top -p $(pgrep -f streamlit)
```

### 헬스 체크

브라우저에서 접속하여 확인:

```
http://your-server-ip:8501
```

또는 curl 사용:

```bash
curl http://localhost:8501/_stcore/health
```

## 방화벽 설정

### Linux (ufw)

```bash
sudo ufw allow 8501/tcp
sudo ufw reload
```

### Linux (firewalld)

```bash
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### Windows

1. Windows Defender 방화벽 설정 열기
2. 인바운드 규칙 추가
3. 포트 8501 허용

## 보안 고려사항

1. **HTTPS 설정**: Nginx나 Apache를 리버스 프록시로 사용하여 HTTPS 적용
2. **인증 추가**: Streamlit의 기본 인증 기능 사용 또는 외부 인증 시스템 연동
3. **파일 크기 제한**: `config.py`에서 `MAX_FILE_SIZE` 설정 확인
4. **디렉토리 권한**: 업로드/출력 디렉토리의 적절한 권한 설정

## 문제 해결

### 포트가 이미 사용 중인 경우

```bash
# 포트 사용 프로세스 확인
lsof -i :8501

# 프로세스 종료
kill -9 <PID>

# 또는 다른 포트 사용
streamlit run frontend/streamlit_app.py --server.port=8502
```

### 권한 오류

```bash
# 디렉토리 권한 설정
chmod -R 755 uploads outputs cache

# 소유권 변경
chown -R user:user uploads outputs cache
```

### 메모리 부족

- 큰 파일 처리 시 메모리 사용량 증가
- 시스템 리소스 모니터링 필요
- 필요시 스왑 메모리 추가

## 업데이트 배포

```bash
# Git 사용 시
git pull origin main

# 또는 새 파일로 교체
# 1. 백업
cp -r pre-processing pre-processing-backup

# 2. 새 파일 복사
# 3. 패키지 업데이트
pip install -r requirements.txt --upgrade

# 4. 서비스 재시작
sudo systemctl restart doc-preprocessing
```

## 추가 리소스

- [Streamlit 배포 가이드](https://docs.streamlit.io/knowledge-base/deploy)
- [Docker 문서](https://docs.docker.com/)
- [systemd 가이드](https://www.freedesktop.org/software/systemd/man/systemd.service.html)


