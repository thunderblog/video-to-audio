# CLAUDE.md

このファイルは、このリポジトリでClaude Code (claude.ai/code)が作業する際のガイダンスを提供します。

## 言語設定
- **重要**: Claude Codeからの回答は必ず日本語で返してください

## プロジェクト概要
MP4動画ファイルをMP3音声ファイルに変換するモダンなPython CLIツールです。Typer、Rich、Poetry、Ruffなどの最新ツールを使用しています。

## システム要件
- Python 3.9以上
- Poetry（依存関係管理）
- FFmpeg: このツールはFFmpegに依存しています。https://ffmpeg.org/download.html からインストールしてください

## 開発コマンド

### セットアップ
```bash
# 依存関係インストール
poetry install

# 仮想環境をアクティベート
poetry shell
```

### 実行
```bash
# 対話的モードで実行
poetry run python mp4tomp3.py
poetry run mp4tomp3  # scriptとして登録済み

# 特定のファイルを変換
poetry run python mp4tomp3.py -f movie/video.mp4

# ビットレート指定
poetry run python mp4tomp3.py -b 320k

# ファイル一覧表示のみ
poetry run python mp4tomp3.py -l

# ファイル情報を表示しながら変換
poetry run python mp4tomp3.py -f movie/video.mp4 --info
```

**注意**: Windows環境(特にGit Bash)で日本語ファイル名が文字化けする場合は、環境変数を設定してください:
```bash
# Windowsで日本語ファイル名を正しく表示
PYTHONIOENCODING=utf-8 poetry run python mp4tomp3.py

# または環境変数を永続的に設定
export PYTHONIOENCODING=utf-8
poetry run python mp4tomp3.py
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

# テストを実行
poetry run pytest
```

## アーキテクチャ概要

### 技術スタック
- **Typer**: 型ヒントベースのモダンなCLIフレームワーク
- **Rich**: 美しいターミナル出力（カラー、テーブル、プログレスバー）
- **Poetry**: 依存関係管理とパッケージング
- **Ruff**: 高速なリンターとフォーマッター（Black、isort、flake8の代替）
- **mypy**: 厳格な静的型チェック
- **ffmpeg-python**: FFmpegのPythonラッパー

### コアコンポーネント
- **mp4tomp3.py**: ルートディレクトリのエントリーポイント
- **src/main.py**: Typer CLIの定義。Rich Console、対話的モード、進行状況表示
- **src/converter.py**: `VideoToAudioConverter`クラス。ffmpeg-pythonを使用した変換ロジック
- **src/utils.py**: ファイル検索、FFmpeg検証、ディスク容量チェック、出力パス生成
- **src/exceptions.py**: カスタム例外階層。すべて`VideoConverterError`を継承

### ディレクトリ構造
- `src/`: Pythonソースコード
- `tests/`: pytestテストファイル
- `movie/`: 入力動画ファイルの配置ディレクトリ（対話的モード使用時）
- `mp3/`: デフォルトの出力ディレクトリ（変換されたMP3ファイルが格納される）

### 変換の仕組み
1. `VideoToAudioConverter.__init__()`: FFmpegの存在確認と出力ディレクトリ作成
2. `convert_file()`: 入力検証 → ディスク容量チェック → ffmpeg-pythonでMP3に変換
   - デフォルト設定: 192kbpsビットレート、44.1kHzサンプリングレート、libmp3lameコーデック
3. エラーハンドリング: FFmpegのエラー出力を解析し、適切なカスタム例外に変換

### サポートされている形式
`utils.py`の`SUPPORTED_VIDEO_FORMATS`で定義:
- .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v, .3gp, .ts, .mts, .m2ts

## Pythonコーディング規則とベストプラクティス

### コーディングスタイル
- **Ruff**を使用（PEP 8準拠、自動フォーマット）
- インデントは4スペース
- 行の長さは100文字以内
- 関数名、変数名はsnake_case
- クラス名はPascalCase
- 定数は大文字とアンダースコア（UPPER_CASE）

### 型ヒント
- **Python 3.9+の型ヒント**を使用（`list[Path]`、`dict[str, Any]`など）
- すべての関数の引数と戻り値には型アノテーションを付ける
- **mypy strict mode**で型チェックを実施
- `typing.Optional`よりも`Type | None`を優先

### ドキュメント
- すべての関数とクラスにdocstringを記述
- Google スタイルのdocstringを使用
- 複雑なロジックにはインラインコメントを追加

### エラーハンドリング
- カスタム例外クラスを使用（`exceptions.py`）
- 例外チェーンを使用（`raise ... from e`）
- ファイル操作時はtry-except-finallyまたはwith文を使用

### 依存関係管理
- **Poetry**を使用（`pyproject.toml`で管理）
- `poetry add`で依存関係を追加
- `poetry add --group dev`で開発用依存関係を追加

### テスト
- **pytest**を使用したユニットテスト
- テストカバレッジ80%以上を目標
- テストファイルは`tests/test_*.py`の命名規則

### コード品質チェック
新しいコードを書く際は以下を実行:
1. `poetry run ruff format .` - フォーマット
2. `poetry run ruff check . --fix` - リントと自動修正
3. `poetry run mypy src/` - 型チェック
4. `poetry run pytest` - テスト実行
