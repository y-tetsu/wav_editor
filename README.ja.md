[![English](https://img.shields.io/badge/README-English-blue)](README.md)
# WAV Editor

<img src="docs/wav_editor.png" width="128">

Python（Tkinter）で作成した、**シンプルな WAV 音声編集ツール**です。

波形を表示し、指定した範囲の再生・ループ再生・切り出し保存（WAV / OGG / MP3）が行えます。ゲーム制作や効果音編集など、軽作業向けのツールです。

---

## 主な機能

* WAV ファイルの読み込み
* 波形表示（Matplotlib）
* 開始・終了位置の指定（ms 単位）
* 範囲再生 / ループ再生
* 右クリックで再生開始位置を指定
* 再生ヘッド（赤線）のリアルタイム表示
* 選択範囲の保存

  * WAV
  * OGG
  * MP3
* ドラッグ＆ドロップ起動（exe 化時想定）

---

## 動作イメージ

* オレンジ色の範囲：選択範囲（Start ～ End）
* 赤い縦線：再生開始位置 / 再生ヘッド

---

## 操作方法

### ファイル操作

* **Open**

  * WAV ファイルを開きます

* **Save WAV / OGG / MP3**

  * 選択範囲を指定フォーマットで保存します

---

### 再生操作

* **Play**

  * 選択範囲を 1 回再生

* **Loop**

  * 選択範囲をループ再生

* **Stop**

  * 再生停止

---

### 範囲指定

* Start / End エントリ

  * ミリ秒（ms）指定
  * Enter キーで確定

* 波形上の **右クリック**

  * 再生開始位置を指定

---

### キーボード操作

| キー          | 動作                |
| ----------- | ----------------- |
| Enter       | Start / End 入力を確定 |
| Esc         | 再生開始位置のみリセット      |
| Shift + Esc | 範囲・再生位置をすべてリセット   |

---

## 対応フォーマット

* 入力：WAV
* 出力：

  * WAV（soundfile）
  * OGG（pydub / libvorbis）
  * MP3（pydub / lame）

---

## 必要ライブラリ

```bash
pip install numpy sounddevice soundfile pydub matplotlib
```

※ OGG / MP3 保存には ffmpeg または lame が必要です。

---

## 実行方法

```bash
python wav_editor.py
```

### 起動時引数（ドラッグ＆ドロップ対応）

```bash
python wav_editor.py sample.wav
```

---

## exe 化（PyInstaller）

本ツールは **PyInstaller** を使用して Windows 用 exe ファイルとして配布することを想定しています。

同じフォルダに以下の `build.bat` を配置し、実行してください。

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

### オプション説明

* `--onefile`

  * 単一 exe ファイルとして生成します

* `--noconsole`

  * コンソールウィンドウを表示しません（GUI アプリ向け）

* `--add-data "ico;ico"`

  * アイコンファイルを exe 内に同梱します
  * `ico` フォルダをそのまま配置

* `--icon=ico\wav_editor.ico`

  * exe のアプリケーションアイコンを指定します

* `--name wav_editor`

  * 生成される exe ファイル名

* `--exclude-module ...`

  * 使用していないライブラリを除外し、exe サイズを削減します

---

### exe 実行時の注意点

* 初回起動時はウイルスチェック等で起動が遅くなる場合があります
* ffmpeg / lame が PATH に通っていない場合、OGG / MP3 保存が失敗します
* exe への **WAV ファイルのドラッグ＆ドロップ起動**に対応しています

---

## 注意事項

* 大きな WAV ファイルでも表示できるよう、波形表示は間引きしています
* 編集は非破壊（元ファイルは変更されません）
* 精密なサンプル編集用途ではなく、軽量な編集を想定しています

---

## 想定用途

* ゲーム用効果音の切り出し
* BGM ループ位置の確認
* WAV → OGG / MP3 変換
* 音声素材の簡易チェック

---

## ライセンス

このスクリプトは個人・学習用途向けのサンプルコードです。
必要に応じて自由に改変・再利用してください。

---

## 補足

* Tkinter + Matplotlib + sounddevice を組み合わせた
  **最小構成の音声エディタ実装例**としても利用できます。
* PyInstaller で exe 化して配布する用途も想定しています。
