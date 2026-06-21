@echo off
REM rembgアプリケーション セットアップスクリプト (Windows)

echo ========================================
echo rembg - セットアップスクリプト
echo ========================================
echo.

REM Pythonバージョン確認
python --version
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません
    echo https://www.python.org/ からPythonをインストールしてください
    pause
    exit /b 1
)

echo.
echo 1. 仮想環境を作成します...
python -m venv venv
if errorlevel 1 (
    echo エラー: 仮想環境の作成に失敗しました
    pause
    exit /b 1
)

echo.
echo 2. 仮想環境をアクティベートします...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo エラー: 仮想環境のアクティベーションに失敗しました
    pause
    exit /b 1
)

echo.
echo 3. pipをアップグレードします...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo 警告: pipのアップグレードに失敗しました（続行します）
)

echo.
echo 4. 依存パッケージをインストールします...
echo （これには数分かかる場合があります）
pip install -r requirements.txt
if errorlevel 1 (
    echo エラー: パッケージのインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo ========================================
echo セットアップが完了しました！
echo ========================================
echo.
echo アプリケーションを起動するには：
echo   python src\app.py
echo.
pause
