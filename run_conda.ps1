# Anaconda 가상환경에서 애플리케이션 실행 스크립트 (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "문서 전처리 서비스 시작" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 가상환경 Python 경로
$pythonPath = "$env:USERPROFILE\.conda\envs\pre-processing\python.exe"
$streamlitPath = "$env:USERPROFILE\.conda\envs\pre-processing\Scripts\streamlit.exe"

# 프로젝트 디렉토리로 이동
Set-Location $PSScriptRoot

# Streamlit 애플리케이션 실행
Write-Host "Streamlit 애플리케이션을 시작합니다..." -ForegroundColor Green
Write-Host "브라우저에서 http://localhost:8501 로 접속하세요." -ForegroundColor Yellow
Write-Host "종료하려면 Ctrl+C를 누르세요." -ForegroundColor Yellow
Write-Host ""

& $streamlitPath run frontend/streamlit_app.py

