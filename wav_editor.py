import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import sounddevice as sd
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AudioEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("WAV Editor")

        # ===== audio state =====
        self.audio = None
        self.sample_rate = 44100
        self.channels = 1

        self.start_sample = 0
        self.end_sample = 0

        self.is_playing = False
        self.is_looping = False
        self.stream = None
        self.play_pos = 0

        # ===== UI =====
        frame = tk.Frame(root)
        frame.pack()

        self.btn_open = tk.Button(frame, text="Open", command=self.open_file)
        self.btn_play = tk.Button(frame, text="Play", command=self.play_selected)
        self.btn_loop = tk.Button(frame, text="Loop", command=self.loop_selected)
        self.btn_stop = tk.Button(frame, text="Stop", command=self.stop_audio)
        self.btn_save = tk.Button(frame, text="Save Selection", command=self.save_selection)

        self.btn_open.pack(side=tk.LEFT)
        self.btn_play.pack(side=tk.LEFT)
        self.btn_loop.pack(side=tk.LEFT)
        self.btn_stop.pack(side=tk.LEFT)
        self.btn_save.pack(side=tk.LEFT)

        tk.Label(frame, text="Start (ms)").pack(side=tk.LEFT)
        self.start_entry = tk.Entry(frame, width=8)
        self.start_entry.pack(side=tk.LEFT)

        tk.Label(frame, text="End (ms)").pack(side=tk.LEFT)
        self.end_entry = tk.Entry(frame, width=8)
        self.end_entry.pack(side=tk.LEFT)

        self.start_entry.bind("<Return>", self.entry_confirm)
        self.end_entry.bind("<Return>", self.entry_confirm)
        self.root.bind("<Escape>", self.reset_view)

        # ===== plot =====
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()

        # ===== close hook =====
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # =====================================================
    # UI control
    # =====================================================

    def set_ui_playing(self, playing: bool):
        state = tk.DISABLED if playing else tk.NORMAL

        self.btn_open.config(state=state)
        self.btn_play.config(state=state)
        self.btn_loop.config(state=state)
        self.btn_save.config(state=state)

        self.start_entry.config(state=state)
        self.end_entry.config(state=state)

        self.btn_stop.config(state=tk.NORMAL)

    # =====================================================
    # File
    # =====================================================

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
        if not path:
            return

        self.audio, self.sample_rate = sf.read(path, always_2d=True)
        self.channels = self.audio.shape[1]

        self.start_sample = 0
        self.end_sample = len(self.audio)

        self.update_entries()
        self.draw_waveform()

    # =====================================================
    # Save
    # =====================================================

    def save_selection(self):
        if self.audio is None:
            return

        if self.start_sample >= self.end_sample:
            messagebox.showwarning("Invalid range", "Start must be smaller than End.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV", "*.wav")]
        )
        if not path:
            return

        segment = self.audio[self.start_sample:self.end_sample]

        sf.write(path, segment, self.sample_rate)
        messagebox.showinfo("Saved", f"Saved selection to:\n{path}")

    # =====================================================
    # UI helpers
    # =====================================================

    def update_entries(self):
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

        self.start_entry.insert(
            0, f"{self.start_sample * 1000 / self.sample_rate:.3f}"
        )
        self.end_entry.insert(
            0, f"{self.end_sample * 1000 / self.sample_rate:.3f}"
        )

    def entry_confirm(self, event=None):
        if self.audio is None or self.is_playing:
            return

        try:
            s = float(self.start_entry.get())
            e = float(self.end_entry.get())
        except ValueError:
            return

        self.start_sample = int(s * self.sample_rate / 1000)
        self.end_sample = int(e * self.sample_rate / 1000)

        self.start_sample = max(0, min(self.start_sample, len(self.audio)))
        self.end_sample = max(self.start_sample, min(self.end_sample, len(self.audio)))

        self.draw_waveform()

    def reset_view(self, event=None):
        if self.audio is None:
            return

        self.stop_audio()
        self.start_sample = 0
        self.end_sample = len(self.audio)
        self.update_entries()
        self.draw_waveform()

    # =====================================================
    # Drawing
    # =====================================================

    def draw_waveform(self):
        self.ax.clear()

        if self.audio is not None:
            y = self.audio[:, 0]
            x = np.arange(len(y)) * 1000 / self.sample_rate
            self.ax.plot(x, y, linewidth=0.5)

            s = self.start_sample * 1000 / self.sample_rate
            e = self.end_sample * 1000 / self.sample_rate
            self.ax.axvspan(s, e, color="orange", alpha=0.3)

        self.ax.set_xlabel("Time (ms)")
        self.fig.tight_layout()
        self.canvas.draw()

    # =====================================================
    # Audio control
    # =====================================================

    def stop_audio(self):
        self.is_looping = False
        self.is_playing = False

        if self.stream:
            try:
                self.stream.abort()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        sd.stop()
        self.set_ui_playing(False)

    def play_selected(self):
        self._play(loop=False)

    def loop_selected(self):
        self._play(loop=True)

    def _play(self, loop=False):
        if self.audio is None:
            return

        self.stop_audio()

        segment = self.audio[self.start_sample:self.end_sample]
        if len(segment) == 0:
            return

        self.is_playing = True
        self.is_looping = loop
        self.play_pos = 0
        self.set_ui_playing(True)

        def callback(outdata, frames, time, status):
            if not self.is_playing:
                raise sd.CallbackStop()

            remain = len(segment) - self.play_pos
            n = min(frames, remain)

            outdata[:n] = segment[self.play_pos:self.play_pos + n]
            outdata[n:] = 0
            self.play_pos += n

            if self.play_pos >= len(segment):
                if self.is_looping:
                    self.play_pos = 0
                else:
                    self.is_playing = False
                    self.root.after(0, self.set_ui_playing, False)
                    raise sd.CallbackStop()

        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback
        )
        self.stream.start()

    # =====================================================
    # Proper shutdown
    # =====================================================

    def on_close(self):
        self.stop_audio()
        self.root.quit()
        self.root.destroy()


# =====================================================
# main
# =====================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEditor(root)
    root.mainloop()

