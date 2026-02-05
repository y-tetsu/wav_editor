[![日本語](https://img.shields.io/badge/README-日本語-red)](README.ja.md)
# WAV Editor

<img src="docs/wav_editor.png" width="128">

A **simple WAV audio editing tool** built with Python (Tkinter).

It allows you to display waveforms, play selected ranges, loop playback, and cut/export audio segments (WAV / OGG / MP3).  
This tool is designed for lightweight tasks such as game development and sound effect editing.

---

## Features

* Load WAV files
* Waveform display (Matplotlib)
* Specify start/end positions (in milliseconds)
* Range playback / loop playback
* Right-click to set playback start position
* Real-time playback head display (red line)
* Save selected range:
  * WAV
  * OGG
  * MP3
* Drag & drop launch support (for exe builds)

---

## Visual Guide

* Orange area: Selected range (Start–End)
* Red vertical line: Playback start position / playback head

---

## How to Use

### File Operations

* **Open**
  * Open a WAV file

* **Save WAV / OGG / MP3**
  * Save the selected range in the chosen format

---

### Playback Controls

* **Play**
  * Play the selected range once

* **Loop**
  * Loop playback of the selected range

* **Stop**
  * Stop playback

---

### Range Selection

* Start / End entries
  * Specify in milliseconds (ms)
  * Press Enter to apply

* **Right-click** on waveform
  * Set playback start position

---

### Keyboard Shortcuts

| Key           | Action                                   |
|--------------|-------------------------------------------|
| Enter        | Confirm Start / End input                 |
| Esc          | Reset playback start position only        |
| Shift + Esc  | Reset range and playback position entirely|

---

## Supported Formats

* Input: WAV
* Output:
  * WAV (soundfile)
  * OGG (pydub / libvorbis)
  * MP3 (pydub / lame)

---

## Requirements

```bash
pip install numpy sounddevice soundfile pydub matplotlib
```

Saving OGG / MP3 requires **ffmpeg** or **lame** to be installed and available in PATH.

---

## Running the Script

```bash
python wav_editor.py
```

### Command-line Argument (Drag & Drop Support)

```bash
python wav_editor.py sample.wav
```

---

## Building an Executable (PyInstaller)

This tool is intended to be distributed as a Windows executable using **PyInstaller**.

Place the following `build.bat` in the same directory and run it.

### build.bat

```bat
pyinstaller ^
--onefile ^
--noconsole ^
--add-data "ico;ico" ^
--icon=ico\wav_editor.ico ^
--name wav_editor ^
--exclude-module unittest ^
--exclude-module pip ^
wav_editor.py
```

---

### Option Details

* `--onefile`
  * Build a single executable file

* `--noconsole`
  * Hide the console window (recommended for GUI apps)

* `--add-data "ico;ico"`
  * Bundle icon files into the executable
  * Keeps the `ico` folder structure

* `--icon=ico\wav_editor.ico`
  * Specify the application icon

* `--name wav_editor`
  * Name of the generated executable

* `--exclude-module ...`
  * Exclude unused libraries to reduce executable size

---

### Notes for Executable Usage

* First launch may be slow due to antivirus scanning
* Saving OGG / MP3 will fail if ffmpeg / lame are not in PATH
* Drag & drop WAV files onto the exe is supported

---

## Notes

* Waveform display is downsampled for large WAV files
* Editing is non-destructive (original files are not modified)
* Intended for lightweight editing, not sample-accurate mastering

---

## Intended Use Cases

* Extracting sound effects for games
* Checking BGM loop points
* WAV to OGG / MP3 conversion
* Quick inspection of audio assets

---

## License

This script is provided as sample code for personal and educational use.  
You are free to modify and reuse it as needed.

---

## Additional Information

* Can be used as a **minimal audio editor implementation**
  combining Tkinter, Matplotlib, and sounddevice
* Designed with PyInstaller-based distribution in mind
