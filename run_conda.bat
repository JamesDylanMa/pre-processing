@echo off
REM Anaconda 가상환경에서 애플리케이션 실행 스크립트

echo ========================================
echo 문서 전처리 서비스 시작
echo ========================================
echo.

REM 가상환경 활성화
call C:\ProgramData\Anaconda3\Scripts\activate.bat pre-processing

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM Streamlit 애플리케이션 실행
echo Streamlit 애플리케이션을 시작합니다...
echo 브라우저에서 http://localhost:8501 로 접속하세요.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

streamlit run frontend/streamlit_app.py

pause

