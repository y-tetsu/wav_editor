import tkinter as tk
from tkinter import filedialog, messagebox
from pydub import AudioSegment
import pygame
import threading
import os

class WavEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("WAV Editor")
        self.root.geometry("400x350")

        pygame.mixer.init()

        self.audio = None
        self.audio_path = None
        self.play_thread = None
        self.loop_flag = False

        # --- GUI 要素 ---
        tk.Button(root, text="ファイルを開く", command=self.load_file).pack(pady=5)
        self.status = tk.Label(root, text="ファイル未読込", fg="gray")
        self.status.pack()

        tk.Button(root, text="再生", command=self.play_audio).pack(pady=3)
        tk.Button(root, text="停止", command=self.stop_audio).pack(pady=3)
        tk.Button(root, text="ループ再生", command=self.loop_audio).pack(pady=3)

        tk.Label(root, text="再生範囲（秒）").pack()
        frm = tk.Frame(root)
        frm.pack()
        tk.Label(frm, text="開始:").pack(side=tk.LEFT)
        self.start_entry = tk.Entry(frm, width=5)
        self.start_entry.insert(0, "0")
        self.start_entry.pack(side=tk.LEFT)
        tk.Label(frm, text="終了:").pack(side=tk.LEFT)
        self.end_entry = tk.Entry(frm, width=5)
        self.end_entry.insert(0, "5")
        self.end_entry.pack(side=tk.LEFT)

        tk.Button(root, text="指定範囲を再生", command=self.play_range).pack(pady=3)
        tk.Button(root, text="指定範囲を保存", command=self.export_range).pack(pady=3)
        tk.Button(root, text="WAV→OGG変換", command=self.convert_to_ogg).pack(pady=3)

    # --- ファイル読み込み ---
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if not path:
            return
        self.audio = AudioSegment.from_wav(path)
        self.audio_path = path
        self.status.config(text=f"読み込み完了: {os.path.basename(path)}", fg="green")

    # --- 再生 ---
    def play_audio(self):
        if not self.audio_path:
            messagebox.showerror("エラー", "ファイルを読み込んでください。")
            return
        self._play_file(self.audio_path)

    # --- 停止 ---
    def stop_audio(self):
        pygame.mixer.music.stop()
        self.loop_flag = False

    # --- ループ再生 ---
    def loop_audio(self):
        if not self.audio_path:
            messagebox.showerror("エラー", "ファイルを読み込んでください。")
            return
        self.loop_flag = True
        self._play_file(self.audio_path, loop=True)

    # --- 指定範囲再生 ---
    def play_range(self):
        if not self.audio:
            messagebox.showerror("エラー", "ファイルを読み込んでください。")
            return

        start = int(float(self.start_entry.get()) * 1000)
        end = int(float(self.end_entry.get()) * 1000)
        segment = self.audio[start:end]

        temp_path = "_temp.wav"
        segment.export(temp_path, format="wav")
        self._play_file(temp_path)

    # --- 指定範囲を保存 ---
    def export_range(self):
        if not self.audio:
            messagebox.showerror("エラー", "ファイルを読み込んでください。")
            return
        start = int(float(self.start_entry.get()) * 1000)
        end = int(float(self.end_entry.get()) * 1000)
        segment = self.audio[start:end]
        out_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if out_path:
            segment.export(out_path, format="wav")
            messagebox.showinfo("完了", f"保存しました: {out_path}")

    # --- WAV→OGG変換 ---
    def convert_to_ogg(self):
        if not self.audio:
            messagebox.showerror("エラー", "ファイルを読み込んでください。")
            return
        out_path = filedialog.asksaveasfilename(defaultextension=".ogg", filetypes=[("OGG", "*.ogg")])
        if out_path:
            self.audio.export(out_path, format="ogg")
            messagebox.showinfo("完了", f"変換しました: {out_path}")

    # --- 内部: 再生スレッド処理 ---
    def _play_file(self, path, loop=False):
        def run():
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
            while pygame.mixer.music.get_busy():
                if not self.loop_flag:
                    break
        self.stop_audio()
        self.play_thread = threading.Thread(target=run)
        self.play_thread.start()

# --- 実行 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = WavEditor(root)
    root.mainloop()

