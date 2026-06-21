import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from rembg import remove
import os
from pathlib import Path


class RemBGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("rembg - 対象物自動切り抜きツール")
        self.root.geometry("1200x800")
        
        # 状態管理
        self.original_image = None
        self.original_image_cv = None
        self.display_image = None
        self.drawing = False
        self.start_point = None
        self.current_point = None
        self.mask = None
        self.selected_rect = None
        self.image_item = None
        self.rect_item = None
        self.display_width = 0
        self.display_height = 0
        self.image_offset_x = 0
        self.image_offset_y = 0
        
        # UI作成
        self.create_ui()
        
    def create_ui(self):
        """UIコンポーネントの作成"""
        # フレーム分割
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        
        display_frame = tk.Frame(self.root)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # コントロールパネル
        title_label = tk.Label(control_frame, text="操作パネル", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # ボタン
        self.load_btn = tk.Button(control_frame, text="画像を開く", command=self.load_image, 
                                   bg="#4CAF50", fg="white", font=("Arial", 10), width=20)
        self.load_btn.pack(pady=5)
        
        self.clear_mask_btn = tk.Button(control_frame, text="選択をクリア", command=self.clear_mask,
                                         bg="#FF9800", fg="white", font=("Arial", 10), width=20, state=tk.DISABLED)
        self.clear_mask_btn.pack(pady=5)
        
        self.process_btn = tk.Button(control_frame, text="背景を除去", command=self.process_image,
                                      bg="#2196F3", fg="white", font=("Arial", 10), width=20, state=tk.DISABLED)
        self.process_btn.pack(pady=5)
        
        self.save_btn = tk.Button(control_frame, text="結果を保存", command=self.save_result,
                                   bg="#9C27B0", fg="white", font=("Arial", 10), width=20, state=tk.DISABLED)
        self.save_btn.pack(pady=5)
        
        self.reset_btn = tk.Button(control_frame, text="リセット", command=self.reset,
                                    bg="#F44336", fg="white", font=("Arial", 10), width=20)
        self.reset_btn.pack(pady=5)
        
        # 情報パネル
        info_frame = tk.LabelFrame(control_frame, text="情報", font=("Arial", 10, "bold"), padx=10, pady=10)
        info_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        self.info_label = tk.Label(info_frame, text="1. 「画像を開く」をクリック\n2. マウスでドラッグして対象領域を選択（または選択せず全体処理）\n3. 「背景を除去」をクリック\n4. 「結果を保存」で保存",
                                    justify=tk.LEFT, font=("Arial", 9))
        self.info_label.pack()
        
        # ディスプレイフレーム
        display_label = tk.Label(display_frame, text="画像表示エリア", font=("Arial", 12, "bold"))
        display_label.pack()
        
        # Canvas
        self.canvas = tk.Canvas(display_frame, bg="gray20", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        
    def load_image(self):
        """画像ファイルを開く"""
        file_path = filedialog.askopenfilename(
            title="画像を選択してください",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"), ("All files", "*.*")]
        )
        
        if file_path:
            self.original_image_cv = cv2.imread(file_path)
            if self.original_image_cv is None:
                messagebox.showerror("エラー", "画像を読み込めません")
                return
            
            # OpenCVはBGRなのでRGBに変換
            self.original_image = cv2.cvtColor(self.original_image_cv, cv2.COLOR_BGR2RGB)
            self.display_image = self.original_image.copy()
            self.mask = None
            self.selected_rect = None
            self.clear_rectangle()
            
            self.clear_mask_btn.config(state=tk.DISABLED)
            self.process_btn.config(state=tk.NORMAL)
            self.save_btn.config(state=tk.DISABLED)
            
            self.show_image()
    
    def load_image_from_path(self, file_path):
        """指定パスから画像を読み込み"""
        self.original_image_cv = cv2.imread(file_path)
        if self.original_image_cv is None:
            messagebox.showerror("エラー", "画像を読み込めません")
            return False
        
        self.original_image = cv2.cvtColor(self.original_image_cv, cv2.COLOR_BGR2RGB)
        self.display_image = self.original_image.copy()
        self.mask = None
        self.selected_rect = None
        self.clear_rectangle()
        
        self.clear_mask_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.DISABLED)
        
        self.show_image()
        return True
    
    def on_mouse_press(self, event):
        """マウスボタン押下時"""
        if self.original_image is None:
            return
        
        if not self.point_in_image(event.x, event.y):
            return
        
        self.drawing = True
        self.start_point = (event.x, event.y)
        self.current_point = self.start_point
        self.clear_rectangle()
        self.update_rectangle()
    
    def on_mouse_drag(self, event):
        """マウスドラッグ時"""
        if not self.drawing or self.original_image is None:
            return
        
        self.current_point = self.clamp_point(event.x, event.y)
        self.update_rectangle()
    
    def on_mouse_release(self, event):
        """マウスボタン解放時"""
        if not self.drawing or self.original_image is None:
            return
        
        self.drawing = False
        self.current_point = self.clamp_point(event.x, event.y)
        self.update_rectangle()
        
        if self.start_point and self.current_point:
            self.create_selection_mask()
            self.clear_mask_btn.config(state=tk.NORMAL)
    
    def point_in_image(self, x, y):
        return (self.image_offset_x <= x <= self.image_offset_x + self.display_width and
                self.image_offset_y <= y <= self.image_offset_y + self.display_height)
    
    def clamp_point(self, x, y):
        x = min(max(x, self.image_offset_x), self.image_offset_x + self.display_width)
        y = min(max(y, self.image_offset_y), self.image_offset_y + self.display_height)
        return (x, y)
    
    def update_rectangle(self):
        if self.start_point is None or self.current_point is None:
            return
        
        x1 = min(self.start_point[0], self.current_point[0])
        y1 = min(self.start_point[1], self.current_point[1])
        x2 = max(self.start_point[0], self.current_point[0])
        y2 = max(self.start_point[1], self.current_point[1])
        
        if self.rect_item is None:
            self.rect_item = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00FF00", width=2)
        else:
            self.canvas.coords(self.rect_item, x1, y1, x2, y2)
    
    def draw_existing_selection(self):
        if self.selected_rect is None:
            return
        x1, y1, x2, y2 = self.image_to_canvas_coords(*self.selected_rect)
        if self.rect_item is None:
            self.rect_item = self.canvas.create_rectangle(x1, y1, x2, y2, outline="#00FF00", width=2)
        else:
            self.canvas.coords(self.rect_item, x1, y1, x2, y2)
    
    def clear_rectangle(self):
        if self.rect_item is not None:
            self.canvas.delete(self.rect_item)
            self.rect_item = None
    
    def canvas_to_image_coords(self, x, y):
        x_rel = x - self.image_offset_x
        y_rel = y - self.image_offset_y
        if x_rel < 0 or y_rel < 0:
            return None
        x_img = int(x_rel * self.original_image.shape[1] / self.display_width)
        y_img = int(y_rel * self.original_image.shape[0] / self.display_height)
        x_img = min(max(x_img, 0), self.original_image.shape[1] - 1)
        y_img = min(max(y_img, 0), self.original_image.shape[0] - 1)
        return x_img, y_img
    
    def image_to_canvas_coords(self, x1, y1, x2, y2):
        x1c = int(x1 * self.display_width / self.original_image.shape[1]) + self.image_offset_x
        y1c = int(y1 * self.display_height / self.original_image.shape[0]) + self.image_offset_y
        x2c = int(x2 * self.display_width / self.original_image.shape[1]) + self.image_offset_x
        y2c = int(y2 * self.display_height / self.original_image.shape[0]) + self.image_offset_y
        return x1c, y1c, x2c, y2c
    
    def create_selection_mask(self):
        """選択領域のマスクを作成"""
        if self.start_point is None or self.current_point is None:
            return
        
        start_img = self.canvas_to_image_coords(*self.start_point)
        end_img = self.canvas_to_image_coords(*self.current_point)
        if start_img is None or end_img is None:
            return
        
        x1 = min(start_img[0], end_img[0])
        y1 = min(start_img[1], end_img[1])
        x2 = max(start_img[0], end_img[0])
        y2 = max(start_img[1], end_img[1])
        
        if x1 == x2 or y1 == y2:
            return
        
        h, w = self.original_image.shape[:2]
        self.mask = np.zeros((h, w), dtype=np.uint8)
        cv2.rectangle(self.mask, (x1, y1), (x2, y2), 255, -1)
        self.selected_rect = (x1, y1, x2, y2)
    
    def process_image(self):
        """背景を除去"""
        if self.original_image_cv is None:
            messagebox.showwarning("警告", "画像を選択してください")
            return
        
        try:
            messagebox.showinfo("処理中", "背景を除去中です。しばらくお待ちください...")
            
            if self.selected_rect is not None:
                x1, y1, x2, y2 = self.selected_rect
                selected_region = self.original_image_cv[y1:y2, x1:x2]
                result = remove(selected_region)
            else:
                result = remove(self.original_image_cv)
            
            self.result_image = cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)
            self.display_image = self.result_image[:, :, :3]
            
            self.save_btn.config(state=tk.NORMAL)
            self.process_btn.config(state=tk.DISABLED)
            
            self.show_image()
            messagebox.showinfo("完了", "背景の除去が完了しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {str(e)}")
    
    def save_result(self):
        """結果を保存"""
        if not hasattr(self, 'result_image') or self.result_image is None:
            messagebox.showwarning("警告", "処理済み画像がありません")
            return
        
        file_path = filedialog.asksaveasfilename(
            initialdir=str(Path(__file__).parent.parent / "output"),
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.result_image.ndim == 3 and self.result_image.shape[2] == 4:
                save_image = cv2.cvtColor(self.result_image, cv2.COLOR_RGBA2BGRA)
            else:
                save_image = cv2.cvtColor(self.result_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(file_path, save_image)
            messagebox.showinfo("成功", f"画像を保存しました\n{file_path}")
    
    def clear_mask(self):
        """マスク選択をクリア"""
        self.mask = None
        self.selected_rect = None
        self.clear_rectangle()
        self.display_image = self.original_image.copy()
        self.show_image()
        self.clear_mask_btn.config(state=tk.DISABLED)
    
    def reset(self):
        """すべてをリセット"""
        self.original_image = None
        self.original_image_cv = None
        self.display_image = None
        self.mask = None
        self.result_image = None
        self.selected_rect = None
        
        self.canvas.delete("all")
        self.canvas.config(bg="gray20")
        
        self.load_btn.config(state=tk.NORMAL)
        self.clear_mask_btn.config(state=tk.DISABLED)
        self.process_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
    
    def show_image(self):
        """画像をキャンバスに表示"""
        if self.display_image is None:
            return
        
        self.show_image_with_array(self.display_image)
    
    def show_image_with_array(self, image_array):
        """Numpyアレイをキャンバスに表示"""
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        if canvas_w <= 1 or canvas_h <= 1:
            self.root.after(100, lambda: self.show_image_with_array(image_array))
            return
        
        h, w = image_array.shape[:2]
        aspect_ratio = w / h
        
        if canvas_w / canvas_h > aspect_ratio:
            new_h = canvas_h
            new_w = int(new_h * aspect_ratio)
        else:
            new_w = canvas_w
            new_h = int(new_w / aspect_ratio)
        
        self.display_width = new_w
        self.display_height = new_h
        self.image_offset_x = (canvas_w - new_w) // 2
        self.image_offset_y = (canvas_h - new_h) // 2
        
        resized = cv2.resize(image_array, (new_w, new_h))
        
        pil_image = Image.fromarray(resized)
        photo = ImageTk.PhotoImage(pil_image)
        
        self.canvas.delete("all")
        self.image_item = self.canvas.create_image(self.image_offset_x, self.image_offset_y, image=photo, anchor="nw")
        self.canvas.image = photo
        
        if self.selected_rect is not None:
            self.draw_existing_selection()

    def on_canvas_resize(self, event):
        if self.display_image is not None:
            self.show_image()

def main():
    root = tk.Tk()
    app = RemBGApp(root)
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if not app.load_image_from_path(input_path):
            messagebox.showerror("エラー", f"指定された画像を開けませんでした: {input_path}")
    root.mainloop()


if __name__ == "__main__":
    main()
