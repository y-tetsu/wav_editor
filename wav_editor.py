import tkinter as tk
from tkinter import filedialog, messagebox
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
        self.selection = [0, 0]
        self.is_playing = False
        self.is_looping = False

        frame = tk.Frame(root)
        frame.pack(pady=10)
        tk.Button(frame, text="Open WAV", command=self.open_wav).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Play Selected", command=self.play_selected).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Loop Selected", command=self.loop_selected).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Stop", command=self.stop_audio).grid(row=0, column=3, padx=5)
        tk.Button(frame, text="Save WAV", command=self.save_wav).grid(row=0, column=4, padx=5)
        tk.Button(frame, text="Convert to OGG", command=self.convert_to_ogg).grid(row=0, column=5, padx=5)

        range_frame = tk.Frame(root)
        range_frame.pack(pady=5)
        tk.Label(range_frame, text="Start (ms):").grid(row=0, column=0)
        self.start_entry = tk.Entry(range_frame, width=10)
        self.start_entry.grid(row=0, column=1, padx=5)
        tk.Label(range_frame, text="End (ms):").grid(row=0, column=2)
        self.end_entry = tk.Entry(range_frame, width=10)
        self.end_entry.grid(row=0, column=3, padx=5)

        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        self.start_x = None

        # GUI終了イベントのハンドラ登録
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def open_wav(self):
        path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if not path:
            return
        self.filepath = path
        self.audio = AudioSegment.from_wav(path)
        samples = np.array(self.audio.get_array_of_samples())
        if self.audio.channels == 2:
            samples = samples.reshape((-1, 2))[:, 0]
        self.ax.clear()
        self.ax.plot(samples, color='blue')
        self.ax.set_title(path)
        self.canvas.draw()

    def on_click(self, event):
        if not self.audio or not event.xdata:
            return
        self.start_x = event.xdata

    def on_release(self, event):
        if not self.audio or self.start_x is None or not event.xdata:
            return
        x1, x2 = sorted([self.start_x, event.xdata])
        duration_ms = len(self.audio)
        total_samples = len(self.audio.get_array_of_samples())
        start_ms = x1 / total_samples * duration_ms
        end_ms = x2 / total_samples * duration_ms
        self.selection = [int(start_ms), int(end_ms)]
        self.start_entry.delete(0, tk.END)
        self.start_entry.insert(0, str(int(start_ms)))
        self.end_entry.delete(0, tk.END)
        self.end_entry.insert(0, str(int(end_ms)))
        self.ax.axvspan(x1, x2, color='red', alpha=0.3)
        self.canvas.draw()

    def play_selected(self):
        if not self.audio:
            return
        start = int(self.start_entry.get() or 0)
        end = int(self.end_entry.get() or len(self.audio))
        segment = self.audio[start:end]
        threading.Thread(target=self._play_segment, args=(segment,), daemon=True).start()

    def loop_selected(self):
        if not self.audio:
            return
        start = int(self.start_entry.get() or 0)
        end = int(self.end_entry.get() or len(self.audio))
        segment = self.audio[start:end]
        self.is_looping = True
        threading.Thread(target=self._loop_segment, args=(segment,), daemon=True).start()

    def _play_segment(self, segment):
        self.is_playing = True
        with io.BytesIO() as buf:
            segment.export(buf, format='wav')
            buf.seek(0)
            data, samplerate = sf.read(buf, dtype='float32')
            sd.play(data, samplerate)
            sd.wait()
        self.is_playing = False

    def _loop_segment(self, segment):
        while self.is_looping:
            self._play_segment(segment)

    def stop_audio(self):
        self.is_looping = False
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
        sd.stop()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEditor(root)
    root.mainloop()
