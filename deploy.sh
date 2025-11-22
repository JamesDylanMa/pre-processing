#!/bin/bash

# 배포 스크립트 (Linux/Mac)
# 사용법: ./deploy.sh [옵션]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수 정의
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 옵션 파싱
USE_DOCKER=false
USE_COMPOSE=false
PORT=8501
HOST="0.0.0.0"

while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --compose)
            USE_COMPOSE=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        -h|--help)
            echo "사용법: $0 [옵션]"
            echo ""
            echo "옵션:"
            echo "  --docker      Docker를 사용하여 배포"
            echo "  --compose     Docker Compose를 사용하여 배포"
            echo "  --port PORT   포트 번호 지정 (기본값: 8501)"
            echo "  --host HOST   호스트 주소 지정 (기본값: 0.0.0.0)"
            echo "  -h, --help    도움말 표시"
            exit 0
            ;;
        *)
            print_error "알 수 없는 옵션: $1"
            exit 1
            ;;
    esac
done

# 프로젝트 루트 확인
if [ ! -f "frontend/streamlit_app.py" ]; then
    print_error "프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Docker Compose 배포
if [ "$USE_COMPOSE" = true ]; then
    print_info "Docker Compose를 사용하여 배포합니다..."
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml 파일을 찾을 수 없습니다."
        exit 1
    fi
    
    docker-compose down
    docker-compose up -d --build
    
    print_info "서비스가 시작되었습니다."
    print_info "애플리케이션: http://localhost:$PORT"
    print_info "로그 확인: docker-compose logs -f"
    exit 0
fi

# Docker 배포
if [ "$USE_DOCKER" = true ]; then
    print_info "Docker를 사용하여 배포합니다..."
    
    if [ ! -f "Dockerfile" ]; then
        print_error "Dockerfile을 찾을 수 없습니다."
        exit 1
    fi
    
    IMAGE_NAME="document-preprocessing"
    CONTAINER_NAME="doc-preprocessing"
    
    # 기존 컨테이너 중지 및 제거
    if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
        print_info "기존 컨테이너를 중지하고 제거합니다..."
        docker stop $CONTAINER_NAME || true
        docker rm $CONTAINER_NAME || true
    fi
    
    # 이미지 빌드
    print_info "Docker 이미지를 빌드합니다..."
    docker build -t $IMAGE_NAME .
    
    # 컨테이너 실행
    print_info "컨테이너를 실행합니다..."
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8501 \
        -v "$(pwd)/uploads:/app/uploads" \
        -v "$(pwd)/outputs:/app/outputs" \
        -v "$(pwd)/cache:/app/cache" \
        $IMAGE_NAME
    
    print_info "서비스가 시작되었습니다."
    print_info "애플리케이션: http://localhost:$PORT"
    print_info "로그 확인: docker logs -f $CONTAINER_NAME"
    exit 0
fi

# 일반 배포 (가상 환경 사용)
print_info "일반 모드로 배포합니다..."

# 가상 환경 확인
if [ ! -d "venv" ]; then
    print_warn "가상 환경이 없습니다. 생성합니다..."
    python3 -m venv venv
fi

# 가상 환경 활성화
print_info "가상 환경을 활성화합니다..."
source venv/bin/activate

# 패키지 설치
print_info "패키지를 설치합니다..."
pip install --upgrade pip
pip install -r requirements.txt

# 디렉토리 생성
print_info "필요한 디렉토리를 생성합니다..."
mkdir -p uploads outputs cache

# 애플리케이션 실행
print_info "애플리케이션을 시작합니다..."
print_info "애플리케이션: http://$HOST:$PORT"
print_info "중지하려면 Ctrl+C를 누르세요."

streamlit run frontend/streamlit_app.py --server.port=$PORT --server.address=$HOST

