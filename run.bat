@echo off
REM rembgアプリケーション 実行スクリプト (Windows)

REM 仮想環境をアクティベート
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo エラー: 仮想環境が見つかりません
    echo 最初に setup.bat を実行してください
    pause
    exit /b 1
)

REM アプリケーション起動
python src\app.py
