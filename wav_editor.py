import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf
import threading
import io
import sys

class AudioEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("WAV Editor with Waveform and Loop")

        self.audio = None
        self.filepath = None
        self.selection = [0, 0]  # 選択範囲（ms）
        self.is_looping = False
        self.play_thread = None
        self.loading = False  # 読み込み中フラグ
        self.stream = None  # 音声ストリーム
        self.is_playing = False  # 再生中フラグ

        # GUIボタン
        frame = tk.Frame(root)
        frame.pack(pady=10)
        self.buttons = []
        btn_open = tk.Button(frame, text="Open WAV", command=self.open_wav)
        btn_open.grid(row=0, column=0, padx=5)
        self.buttons.append(btn_open)
        btn_play = tk.Button(frame, text="Play Selected", command=self.play_selected)
        btn_play.grid(row=0, column=1, padx=5)
        self.buttons.append(btn_play)
        btn_loop = tk.Button(frame, text="Loop Selected", command=self.loop_selected)
        btn_loop.grid(row=0, column=2, padx=5)
        self.buttons.append(btn_loop)
        btn_stop = tk.Button(frame, text="Stop", command=self.stop_audio)
        btn_stop.grid(row=0, column=3, padx=5)
        self.buttons.append(btn_stop)
        btn_save = tk.Button(frame, text="Save WAV", command=self.save_wav)
        btn_save.grid(row=0, column=4, padx=5)
        self.buttons.append(btn_save)
        btn_convert = tk.Button(frame, text="Convert to OGG", command=self.convert_to_ogg)
        btn_convert.grid(row=0, column=5, padx=5)
        self.buttons.append(btn_convert)

        # ステータスラベル
        self.status_label = tk.Label(root, text="Ready")
        self.status_label.pack(pady=5)

        # プログレスバー
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        self.progress.pack_forget()  # 初期は非表示

        # 音量スライダー
        vol_frame = tk.Frame(root)
        vol_frame.pack(pady=5)
        tk.Label(vol_frame, text="Volume:").pack(side=tk.LEFT)
        self.volume_slider = tk.Scale(vol_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.change_volume)
        self.volume_slider.set(50)  # デフォルト50%
        self.volume_slider.pack(side=tk.LEFT)
        self.volume_db = 0.0  # デフォルト音量（50%相当、従来の100%相当）

        # 選択範囲表示
        range_frame = tk.Frame(root)
        range_frame.pack(pady=5)
        tk.Label(range_frame, text="Start (ms):").grid(row=0, column=0)
        self.start_entry = tk.Entry(range_frame, width=10)
        self.start_entry.grid(row=0, column=1, padx=5)
        tk.Label(range_frame, text="End (ms):").grid(row=0, column=2)
        self.end_entry = tk.Entry(range_frame, width=10)
        self.end_entry.grid(row=0, column=3, padx=5)

        # テキストボックスの変更を検知して選択範囲を更新
        self.start_entry.bind('<KeyRelease>', lambda e: self.update_selection_span())
        self.start_entry.bind('<FocusOut>', lambda e: self.update_selection_span())
        self.end_entry.bind('<KeyRelease>', lambda e: self.update_selection_span())
        self.end_entry.bind('<FocusOut>', lambda e: self.update_selection_span())

        # 波形表示
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.start_x = None
        self.span_patch = None

        # GUI終了時処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def change_volume(self, val):
        val = int(val)
        # Pydub の dBスケールに変換（0-100% → -6dB〜+6dB）
        self.volume_db = -6 + (val / 100) * 12

    def open_wav(self):
        if self.loading:
            return
        path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if not path:
            return
        self.loading = True
        self.status_label.config(text="Loading WAV file...")
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        self.progress.start()
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)

        def load_audio():
            try:
                self.filepath = path
                self.audio = AudioSegment.from_wav(path)
                samples = np.array(self.audio.get_array_of_samples())
                if self.audio.channels == 2:
                    samples = samples.reshape((-1, 2))[:, 0]
                self.root.after(0, lambda: self.update_waveform(samples, path))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(str(e)))

        threading.Thread(target=load_audio, daemon=True).start()

    def update_waveform(self, samples, path):
        self.ax.clear()
        self.ax.plot(samples, color='blue')
        self.ax.set_title(path)
        self.canvas.draw()
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="WAV file loaded successfully")
        for btn in self.buttons:
            btn.config(state=tk.NORMAL)
        self.loading = False
        messagebox.showinfo("Loaded", f"WAV file '{path}' has been loaded successfully.")

    def show_error(self, error_msg):
        self.progress.stop()
        self.progress.pack_forget()
        self.status_label.config(text="Error loading WAV file")
        for btn in self.buttons:
            btn.config(state=tk.NORMAL)
        self.loading = False
        messagebox.showerror("Error", f"Failed to load WAV file: {error_msg}")

    def on_motion(self, event):
        if self.is_playing or not self.audio or self.start_x is None or not event.xdata:
            return
        # ドラッグ中のスパンを更新
        x1, x2 = sorted([self.start_x, event.xdata])
        if self.span_patch:
            self.span_patch.remove()
        self.span_patch = self.ax.axvspan(x1, x2, color='red', alpha=0.3)
        self.canvas.draw()

    def on_click(self, event):
        if self.is_playing or not self.audio or not event.xdata:
            return
        self.start_x = event.xdata
        # 既存のスパンを削除
        if self.span_patch:
            self.span_patch.remove()
            self.span_patch = None

    def on_release(self, event):
        if self.is_playing or not self.audio or self.start_x is None:
            return
        # 波形外でUpしても確定
        if event.xdata is None:
            event.xdata = self.start_x  # 仮にstart_xを使う
        x1, x2 = sorted([self.start_x, event.xdata])
        total_samples = len(self.audio.get_array_of_samples())
        duration_ms = len(self.audio)
        start_ms = int(x1 / total_samples * duration_ms)
        end_ms = int(x2 / total_samples * duration_ms)
        self.selection = [start_ms, end_ms]
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, str(start_ms))
        self.end_entry.delete(0, tk.END)
        self.end_entry.insert(0, str(end_ms))

        # スパンは既にon_motionで描画されているので、更新不要
        self.canvas.draw()
        self.start_x = None  # 選択状態リセット

    def update_selection_span(self):
        if self.is_playing or not self.audio:
            return
        try:
            start_ms = int(self.start_entry.get())
            end_ms = int(self.end_entry.get())
            # 無効な値の補正
            if start_ms < 0:
                start_ms = 0
            if end_ms < start_ms:
                end_ms = start_ms
            duration_ms = len(self.audio)
            if start_ms > duration_ms:
                start_ms = duration_ms
            if end_ms > duration_ms:
                end_ms = duration_ms
            # エントリを更新
            self.start_entry.delete(0, tk.END)
            self.start_entry.insert(0, str(start_ms))
            self.end_entry.delete(0, tk.END)
            self.end_entry.insert(0, str(end_ms))
            self.selection = [start_ms, end_ms]
            # 波形のスパンを更新
            if self.span_patch:
                self.span_patch.remove()
            total_samples = len(self.audio.get_array_of_samples())
            x1 = start_ms / duration_ms * total_samples
            x2 = end_ms / duration_ms * total_samples
            self.span_patch = self.ax.axvspan(x1, x2, color='red', alpha=0.3)
            self.canvas.draw()
        except ValueError:
            # 無効な入力は無視
            pass

    def _play_segment(self, segment, loop=False):
        # データを準備
        raw_data = np.array(segment.get_array_of_samples(), dtype=np.float32)
        if segment.channels == 2:
            data = raw_data.reshape(-1, 2)
        else:
            data = raw_data.reshape(-1, 1)
        data /= 32768.0  # normalize to -1 to 1
        samplerate = segment.frame_rate
        channels = segment.channels

        self.current_data = data
        self.current_index = 0
        self.current_samplerate = samplerate
        self.current_channels = channels
        self.is_playing = True

        self.stream = sd.OutputStream(samplerate=samplerate, channels=channels, callback=self.audio_callback)
        self.stream.start()

        if loop:
            while self.is_looping and self.is_playing:
                if self.current_index >= len(self.current_data):
                    self.current_index = 0
                sd.sleep(10)
        else:
            while self.stream.active and self.is_playing:
                sd.sleep(10)

        self.stream.stop()
        self.stream = None
        self.is_playing = False

    def audio_callback(self, outdata, frames, time, status):
        if not self.is_playing or self.current_index >= len(self.current_data):
            outdata.fill(0)
            return

        end_index = min(self.current_index + frames, len(self.current_data))
        chunk = self.current_data[self.current_index:end_index]
        volume_factor = 10 ** (self.volume_db / 20)
        outdata[:len(chunk)] = chunk * volume_factor
        outdata[len(chunk):] = 0
        self.current_index = end_index

        if self.current_index >= len(self.current_data) and not self.is_looping:
            self.is_playing = False

    def play_selected(self):
        if not self.audio:
            return
        start = int(self.start_entry.get() or 0)
        end = int(self.end_entry.get() or len(self.audio))
        segment = self.audio[start:end]
        if self.play_thread and self.play_thread.is_alive():
            self.stop_audio()
        self.play_thread = threading.Thread(target=self._play_segment, args=(segment, False), daemon=True)
        self.play_thread.start()

    def loop_selected(self):
        if not self.audio:
            return
        start = int(self.start_entry.get() or 0)
        end = int(self.end_entry.get() or len(self.audio))
        segment = self.audio[start:end]
        self.is_looping = True

        def loop_thread():
            self._play_segment(segment, loop=True)

        if self.play_thread and self.play_thread.is_alive():
            self.stop_audio()
        self.play_thread = threading.Thread(target=loop_thread, daemon=True)
        self.play_thread.start()

    def stop_audio(self):
        self.is_looping = False
        self.is_playing = False
        if self.stream:
            self.stream.stop()
            self.stream = None
        sd.stop()

    def save_wav(self):
        if not self.audio:
            return
        path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV Files", "*.wav")])
        if path:
            self.audio.export(path, format='wav')
            messagebox.showinfo("Saved", f"Saved to {path}")

    def convert_to_ogg(self):
        if not self.audio:
            return
        path = filedialog.asksaveasfilename(defaultextension=".ogg", filetypes=[("OGG Files", "*.ogg")])
        if path:
            self.audio.export(path, format='ogg')
            messagebox.showinfo("Converted", f"Converted to {path}")

    def on_close(self):
        self.is_looping = False
        self.is_playing = False
        if self.stream:
            self.stream.stop()
        sd.stop()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEditor(root)
    root.mainloop()

