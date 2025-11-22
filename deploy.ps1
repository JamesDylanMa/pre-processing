# 배포 스크립트 (Windows PowerShell)
# 사용법: .\deploy.ps1 [옵션]

param(
    [switch]$Docker,
    [switch]$Compose,
    [int]$Port = 8501,
    [string]$Host = "0.0.0.0",
    [switch]$Help
)

# 도움말 표시
if ($Help) {
    Write-Host "사용법: .\deploy.ps1 [옵션]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "옵션:"
    Write-Host "  -Docker      Docker를 사용하여 배포"
    Write-Host "  -Compose      Docker Compose를 사용하여 배포"
    Write-Host "  -Port PORT    포트 번호 지정 (기본값: 8501)"
    Write-Host "  -Host HOST    호스트 주소 지정 (기본값: 0.0.0.0)"
    Write-Host "  -Help         도움말 표시"
    exit 0
}

# 함수 정의
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 프로젝트 루트 확인
if (-not (Test-Path "frontend\streamlit_app.py")) {
    Write-Error "프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
}

# Docker Compose 배포
if ($Compose) {
    Write-Info "Docker Compose를 사용하여 배포합니다..."
    
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "docker-compose.yml 파일을 찾을 수 없습니다."
        exit 1
    }
    
    docker-compose down
    docker-compose up -d --build
    
    Write-Info "서비스가 시작되었습니다."
    Write-Info "애플리케이션: http://localhost:$Port"
    Write-Info "로그 확인: docker-compose logs -f"
    exit 0
}

# Docker 배포
if ($Docker) {
    Write-Info "Docker를 사용하여 배포합니다..."
    
    if (-not (Test-Path "Dockerfile")) {
        Write-Error "Dockerfile을 찾을 수 없습니다."
        exit 1
    }
    
    $ImageName = "document-preprocessing"
    $ContainerName = "doc-preprocessing"
    
    # 기존 컨테이너 중지 및 제거
    $existingContainer = docker ps -aq -f name=$ContainerName
    if ($existingContainer) {
        Write-Info "기존 컨테이너를 중지하고 제거합니다..."
        docker stop $ContainerName 2>$null
        docker rm $ContainerName 2>$null
    }
    
    # 이미지 빌드
    Write-Info "Docker 이미지를 빌드합니다..."
    docker build -t $ImageName .
    
    # 컨테이너 실행
    Write-Info "컨테이너를 실행합니다..."
    $currentDir = (Get-Location).Path
    docker run -d `
        --name $ContainerName `
        -p "${Port}:8501" `
        -v "${currentDir}\uploads:/app/uploads" `
        -v "${currentDir}\outputs:/app/outputs" `
        -v "${currentDir}\cache:/app/cache" `
        $ImageName
    
    Write-Info "서비스가 시작되었습니다."
    Write-Info "애플리케이션: http://localhost:$Port"
    Write-Info "로그 확인: docker logs -f $ContainerName"
    exit 0
}

# 일반 배포 (가상 환경 사용)
Write-Info "일반 모드로 배포합니다..."

# 가상 환경 확인
if (-not (Test-Path "venv")) {
    Write-Warn "가상 환경이 없습니다. 생성합니다..."
    python -m venv venv
}

# 가상 환경 활성화
Write-Info "가상 환경을 활성화합니다..."
& "venv\Scripts\Activate.ps1"

# 패키지 설치
Write-Info "패키지를 설치합니다..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# 디렉토리 생성
Write-Info "필요한 디렉토리를 생성합니다..."
New-Item -ItemType Directory -Force -Path "uploads", "outputs", "cache" | Out-Null

# 애플리케이션 실행
Write-Info "애플리케이션을 시작합니다..."
Write-Info "애플리케이션: http://$Host:$Port"
Write-Info "중지하려면 Ctrl+C를 누르세요."

streamlit run frontend/streamlit_app.py --server.port=$Port --server.address=$Host

