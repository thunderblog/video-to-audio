# MP4 to MP3 Converter

動画ファイル（MP4など）をMP3音声ファイルに変換するモダンなPython CLIツールです。

## 特徴

- 🎯 **Typer**を使用した直感的なCLI
- 🎨 **Rich**による美しいターミナル出力（カラフルなテーブル表示）
- 📦 **Poetry**による依存関係管理
- ✨ **Ruff**によるコードフォーマットとリンティング
- 🔍 **mypy**による厳格な型チェック
- 対話的モードとコマンドラインモードの両方をサポート
- 複数の動画形式に対応（MP4, AVI, MOV, MKV, WMV, FLVなど）
- バッチ変換機能
- ビットレート選択可能（128k, 192k, 256k, 320k）
- ファイル情報表示機能
- 詳細なエラーハンドリング

## 必要要件

- Python 3.9以上
- Poetry（依存関係管理）
- FFmpeg（システムにインストールされている必要があります）

### FFmpegのインストール

**Windows:**
https://ffmpeg.org/download.html からダウンロードして、環境変数PATHに追加してください。

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

### Poetryのインストール

```bash
# pipxを使用（推奨）
pipx install poetry

# pipを使用
pip install poetry
```

## インストール

1. リポジトリをクローンまたはダウンロード
2. 依存関係をインストール：

```bash
poetry install
```

## 使い方

### Windows環境での実行（推奨）

Windows PowerShell環境で日本語ファイル名を正しく表示するため、`run.bat`を使用してください：

```powershell
# ファイル一覧表示
.\run.bat -l

# 特定のファイルを変換
.\run.bat -f movie/video.mp4

# ビットレート指定
.\run.bat -f movie/video.mp4 -b 320k

# 対話的モード
.\run.bat
```

**注意**: `run.bat`は文字化け対策として自動的にUTF-8エンコーディングを設定します。

### 対話的モード

```bash
poetry run python mp4tomp3.py
# または
poetry run mp4tomp3
```

`movie/`ディレクトリ内の動画ファイル一覧が美しいテーブル形式で表示されます。変換したいファイルの番号を入力してください。

- 番号入力: 個別ファイルを変換
- `all`: 全ファイルを一括変換
- `0`または`exit`: 終了

### コマンドラインモード

```bash
# 特定のファイルを変換
poetry run python mp4tomp3.py -f movie/video.mp4

# ビットレートを指定
poetry run python mp4tomp3.py -f movie/video.mp4 -b 320k

# 出力ディレクトリを指定
poetry run python mp4tomp3.py -f movie/video.mp4 -o output

# ファイル情報を表示しながら変換
poetry run python mp4tomp3.py -f movie/video.mp4 --info

# movieディレクトリ内のファイル一覧のみ表示
poetry run python mp4tomp3.py -l

# ヘルプを表示
poetry run python mp4tomp3.py --help
```

### オプション

```
-f, --file <path>       変換する動画ファイルのパス
-b, --bitrate <rate>    MP3のビットレート (128k, 192k, 256k, 320k) デフォルト: 192k
-o, --output <dir>      出力ディレクトリ デフォルト: mp3
-l, --list              movieディレクトリ内のファイル一覧を表示のみ
--info                  変換前にファイル情報を表示
--help                  ヘルプメッセージを表示
```

## 開発

### セットアップ

```bash
# 開発用依存関係を含めてインストール
poetry install

# 仮想環境をアクティベート
poetry shell
```

### コード品質

```bash
# Ruffでフォーマット
poetry run ruff format .

# Ruffでリント
poetry run ruff check .

# Ruffでリントと自動修正
poetry run ruff check . --fix

# mypyで型チェック
poetry run mypy src/

# テストを実行（pytest設定済み）
poetry run pytest
```

### プロジェクト構造

```
mp4Tomp3/
├── pyproject.toml        # Poetry設定、Ruff設定、mypy設定
├── mp4tomp3.py           # エントリーポイント
├── run.bat               # Windows用起動スクリプト（UTF-8対応）
├── src/                  # ソースコード
│   ├── __init__.py
│   ├── main.py           # Typer CLIメイン
│   ├── converter.py      # 変換ロジック
│   ├── utils.py          # ユーティリティ関数
│   └── exceptions.py     # カスタム例外
├── tests/                # テストファイル
├── movie/                # 入力動画ファイルを配置（対話的モード用）
└── mp3/                  # 変換されたMP3ファイルの出力先（デフォルト）
```

## サポートされている動画形式

.mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v, .3gp, .ts, .mts, .m2ts

## 技術スタック

- **CLI Framework**: [Typer](https://typer.tiangolo.com/) - 型ヒントベースのモダンなCLI
- **Terminal UI**: [Rich](https://rich.readthedocs.io/) - 美しいターミナル出力
- **Dependency Management**: [Poetry](https://python-poetry.org/) - モダンな依存関係管理
- **Linter/Formatter**: [Ruff](https://docs.astral.sh/ruff/) - 高速なPythonリンター
- **Type Checker**: [mypy](https://mypy-lang.org/) - 静的型チェック
- **Video Processing**: [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) - FFmpegのPythonバインディング

## ライセンス

このプロジェクトはオープンソースです。
