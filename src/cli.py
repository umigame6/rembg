#!/usr/bin/env python3
"""
rembg コマンドラインツール

背景除去処理をコマンドラインから実行
"""

import argparse
import sys
from pathlib import Path
import cv2
from rembg import remove
import numpy as np


def process_single_image(input_path, output_path, mask_path=None):
    """単一画像を処理"""
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"エラー: {input_path} が見つかりません")
        return False
    
    try:
        print(f"読み込み中: {input_path}")
        img = cv2.imread(str(input_file))
        
        if img is None:
            print(f"エラー: {input_path} を読み込めません")
            return False
        
        print("背景を除去中...")
        
        # マスクがある場合は適用
        if mask_path:
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is not None:
                img = cv2.bitwise_and(img, img, mask=mask)
        
        result = remove(img)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        cv2.imwrite(str(output_file), result)
        print(f"[OK] 保存完了: {output_path}")
        return True
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False


def process_batch(input_dir, output_dir):
    """バッチ処理"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        print(f"エラー: {input_dir} が見つかりません")
        return False
    
    if not input_path.is_dir():
        print(f"エラー: {input_dir} はディレクトリではありません")
        return False
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = [f for f in input_path.iterdir() 
                   if f.suffix.lower() in supported_formats]
    
    if not image_files:
        print(f"サポートされた画像ファイルが見つかりません")
        return False
    
    print(f"{len(image_files)} 個のファイルを処理します")
    
    success_count = 0
    for i, img_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] {img_file.name}")
        
        output_file = output_path / f"{img_file.stem}_no_bg.png"
        
        if process_single_image(str(img_file), str(output_file)):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"処理完了: {success_count}/{len(image_files)} 成功")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="rembg コマンドラインツール - 画像から背景を除去",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  # 単一画像の処理
  python src/cli.py -i input.jpg -o output.png
  
  # ディレクトリ内のすべての画像を処理
  python src/cli.py -i input_dir/ -o output_dir/ --batch
  
  # マスク付きで処理
  python src/cli.py -i input.jpg -o output.png -m mask.png
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                        help='入力画像ファイルまたはディレクトリ')
    parser.add_argument('-o', '--output', required=True,
                        help='出力ファイルまたはディレクトリ')
    parser.add_argument('-m', '--mask',
                        help='マスク画像ファイル（オプション）')
    parser.add_argument('-b', '--batch', action='store_true',
                        help='バッチ処理モード（ディレクトリ内のすべての画像を処理）')
    
    args = parser.parse_args()
    
    if args.batch:
        success = process_batch(args.input, args.output)
    else:
        success = process_single_image(args.input, args.output, args.mask)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
