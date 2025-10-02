"""ユーティリティ関数

このモジュールは、動画変換ツール全体で使用される共通ユーティリティ関数を提供します。

主な機能:
    - FFmpeg検証: システムにFFmpegがインストールされているか確認
    - ファイル検索: サポートされている動画ファイルの検索と一覧取得
    - パス生成: 入力ファイルから出力ファイルパスを自動生成
    - ディスク管理: 空き容量チェック、出力ディレクトリ作成
    - ファイルサイズフォーマット: 人間が読みやすい形式への変換

サポート形式:
    .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v, .3gp, .ts, .mts, .m2ts

使用例:
    # FFmpegの存在確認
    validate_ffmpeg()

    # 動画ファイルの検索
    video_files = get_video_files(Path("movie"))

    # 出力パスの生成
    output_path = get_output_path(Path("input.mp4"), Path("output"))
"""

import shutil
import subprocess
from pathlib import Path

from exceptions import FFmpegNotFoundError, InsufficientSpaceError

# サポートする動画形式
SUPPORTED_VIDEO_FORMATS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".3gp",
    ".ts",
    ".mts",
    ".m2ts",
}


def check_ffmpeg_installed() -> bool:
    """
    FFmpegがインストールされているかチェックする

    Returns:
        bool: インストールされている場合True
    """
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def validate_ffmpeg() -> None:
    """
    FFmpegの存在を検証し、なければ例外を発生させる

    Raises:
        FFmpegNotFoundError: FFmpegがインストールされていない場合
    """
    if not check_ffmpeg_installed():
        raise FFmpegNotFoundError(
            "FFmpegがインストールされていません。\n"
            "以下のサイトからダウンロードしてインストールしてください:\n"
            "https://ffmpeg.org/download.html"
        )


def is_supported_video_format(file_path: Path) -> bool:
    """
    ファイルがサポートされている動画形式かチェックする

    Args:
        file_path: チェックするファイルパス

    Returns:
        bool: サポートされている場合True
    """
    return file_path.suffix.lower() in SUPPORTED_VIDEO_FORMATS


def get_video_files(directory: Path) -> list[Path]:
    """
    指定されたディレクトリからサポートされている動画ファイルを取得する

    Args:
        directory: 検索するディレクトリ

    Returns:
        List[Path]: 動画ファイルのパスのリスト
    """
    if not directory.exists() or not directory.is_dir():
        return []

    video_files = []
    for file_path in directory.iterdir():
        if file_path.is_file() and is_supported_video_format(file_path):
            video_files.append(file_path)

    return sorted(video_files)


def get_output_path(input_path: Path, output_dir: Path) -> Path:
    """
    入力ファイルパスから出力ファイルパスを生成する

    Args:
        input_path: 入力ファイルパス
        output_dir: 出力ディレクトリ

    Returns:
        Path: 出力ファイルパス（拡張子がmp3）
    """
    output_name = input_path.stem + ".mp3"
    return output_dir / output_name


def check_disk_space(file_path: Path, required_space_mb: int = 100) -> None:
    """
    十分な空き容量があるかチェックする

    Args:
        file_path: チェック対象のディスクパス
        required_space_mb: 必要な空き容量（MB）

    Raises:
        InsufficientSpaceError: 空き容量が不足している場合
    """
    try:
        disk_usage = shutil.disk_usage(file_path.parent)
        free_space_mb = disk_usage.free / (1024 * 1024)

        if free_space_mb < required_space_mb:
            raise InsufficientSpaceError(
                f"空き容量が不足しています。必要: {required_space_mb}MB, "
                f"利用可能: {free_space_mb:.1f}MB"
            )
    except OSError as e:
        raise InsufficientSpaceError(f"容量チェック中にエラーが発生しました: {e}") from e


def format_file_size(size_bytes: int) -> str:
    """
    ファイルサイズを人間が読みやすい形式でフォーマットする

    Args:
        size_bytes: ファイルサイズ（バイト）

    Returns:
        str: フォーマットされたファイルサイズ
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def create_output_directory(output_dir: Path) -> None:
    """
    出力ディレクトリが存在しない場合は作成する

    Args:
        output_dir: 出力ディレクトリパス
    """
    output_dir.mkdir(parents=True, exist_ok=True)
