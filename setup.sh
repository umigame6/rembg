#!/bin/bash
# rembgアプリケーション セットアップスクリプト (macOS/Linux)

echo "========================================"
echo "rembg - セットアップスクリプト"
echo "========================================"
echo ""

# Pythonバージョン確認
python3 --version
if [ $? -ne 0 ]; then
    echo "エラー: Python 3がインストールされていません"
    echo "https://www.python.org/ からPythonをインストールしてください"
    exit 1
fi

echo ""
echo "1. 仮想環境を作成します..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "エラー: 仮想環境の作成に失敗しました"
    exit 1
fi

echo ""
echo "2. 仮想環境をアクティベートします..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "エラー: 仮想環境のアクティベーションに失敗しました"
    exit 1
fi

echo ""
echo "3. pipをアップグレードします..."
python -m pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "警告: pipのアップグレードに失敗しました（続行します）"
fi

echo ""
echo "4. 依存パッケージをインストールします..."
echo "（これには数分かかる場合があります）"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "エラー: パッケージのインストールに失敗しました"
    exit 1
fi

echo ""
echo "========================================"
echo "セットアップが完了しました！"
echo "========================================"
echo ""
echo "アプリケーションを起動するには："
echo "  python src/app.py"
echo ""
