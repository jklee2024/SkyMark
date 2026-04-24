@echo off
chcp 65001 >nul
title SkyMark v2.0 - 설치

echo ================================================
echo   SkyMark v2.0 설치 프로그램
echo ================================================
echo.

:: Python 확인
py --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo.
    echo Python 64비트를 설치하세요:
    echo https://www.python.org/downloads/
    echo.
    echo 설치 시 "Add Python to PATH" 반드시 체크!
    echo.
    pause
    start https://www.python.org/downloads/
    exit
)

for /f "tokens=*" %%i in ('py --version 2^>^&1') do set PYVER=%%i
echo [OK] %PYVER% 확인됨
echo.

:: SimConnect 설치
echo SimConnect 라이브러리 설치 중...
py -m pip install SimConnect -q
if %errorLevel% neq 0 (
    echo [오류] SimConnect 설치 실패
    echo 네트워크 연결을 확인하고 다시 시도하세요.
    pause
    exit
)
echo [OK] SimConnect 설치 완료
echo.

echo ================================================
echo   설치 완료!
echo.
echo   이제 START.bat 을 더블클릭해서 실행하세요.
echo ================================================
echo.
pause
