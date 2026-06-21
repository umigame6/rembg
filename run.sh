#!/bin/bash
# rembgアプリケーション 実行スクリプト (macOS/Linux)

# 仮想環境をアクティベート
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo "エラー: 仮想環境が見つかりません"
    echo "最初に setup.sh を実行してください"
    exit 1
fi

# アプリケーション起動
python src/app.py
