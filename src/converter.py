"""動画から音声への変換機能"""

from pathlib import Path
from typing import Any, Callable

import ffmpeg

from exceptions import (
    ConversionError,
    FileInUseError,
    FileNotFoundError,
    InsufficientSpaceError,
    PermissionError,
    UnsupportedFormatError,
)
from utils import (
    check_disk_space,
    create_output_directory,
    format_file_size,
    get_output_path,
    is_supported_video_format,
    validate_ffmpeg,
)


class VideoToAudioConverter:
    """動画を音声に変換するクラス"""

    def __init__(self, output_dir: Path = Path("mp3"), bitrate: str = "192k") -> None:
        """
        初期化

        Args:
            output_dir: 出力ディレクトリ
            bitrate: MP3のビットレート（例: "128k", "192k", "320k"）
        """
        self.output_dir = Path(output_dir)
        self.bitrate = bitrate

        # FFmpegの存在確認
        validate_ffmpeg()

        # 出力ディレクトリを作成
        create_output_directory(self.output_dir)

    def convert_file(
        self, input_path: Path, progress_callback: Callable[[str], None] | None = None
    ) -> Path:
        """
        単一ファイルを変換する

        Args:
            input_path: 入力ファイルパス
            progress_callback: 進行状況コールバック関数

        Returns:
            Path: 出力ファイルパス

        Raises:
            FileNotFoundError: 入力ファイルが見つからない場合
            UnsupportedFormatError: 対応していない形式の場合
            ConversionError: 変換中にエラーが発生した場合
            PermissionError: ファイルアクセス権限がない場合
            FileInUseError: ファイルが使用中の場合
            InsufficientSpaceError: 空き容量が不足している場合
        """
        # 入力ファイルの存在確認
        if not input_path.exists():
            raise FileNotFoundError("入力ファイルが見つかりません", str(input_path))

        # ファイル形式の確認
        if not is_supported_video_format(input_path):
            raise UnsupportedFormatError(
                f"対応していない形式です: {input_path.suffix}",
                str(input_path),
            )

        # 出力パスの生成
        output_path = get_output_path(input_path, self.output_dir)

        # 空き容量チェック
        try:
            input_size_mb = input_path.stat().st_size / (1024 * 1024)
            # 音声ファイルは通常動画ファイルの1/10程度のサイズ + マージン
            estimated_output_size = max(int(input_size_mb * 0.15), 10)
            check_disk_space(output_path, estimated_output_size)
        except OSError as e:
            raise PermissionError(f"ファイルにアクセスできません: {e}", str(input_path)) from e

        try:
            # ffmpeg-pythonを使用してMP3に変換
            input_stream = ffmpeg.input(str(input_path))
            output_stream = ffmpeg.output(
                input_stream,
                str(output_path),
                acodec="libmp3lame",
                ab=self.bitrate,
                ar="44100",  # サンプリングレート 44.1kHz
            )

            # 既存ファイルを上書き
            output_stream = ffmpeg.overwrite_output(output_stream)

            # 変換実行
            if progress_callback:
                progress_callback(f"変換開始: {input_path.name}")

            ffmpeg.run(output_stream, quiet=True, capture_stdout=True, capture_stderr=True)

            if progress_callback:
                progress_callback(f"変換完了: {output_path.name}")

        except ffmpeg.Error as e:
            error_message = e.stderr.decode("utf-8") if e.stderr else str(e)

            # エラーメッセージから具体的な問題を特定
            if "Permission denied" in error_message or "Access is denied" in error_message:
                raise PermissionError("ファイルアクセス権限がありません", str(input_path)) from e
            elif (
                "Resource busy" in error_message
                or "being used by another process" in error_message
            ):
                raise FileInUseError("ファイルが他のプロセスで使用中です", str(input_path)) from e
            elif "No space left" in error_message:
                raise InsufficientSpaceError("容量が不足しています") from e
            else:
                raise ConversionError(
                    f"変換中にエラーが発生しました: {error_message}", str(input_path)
                ) from e

        except Exception as e:
            raise ConversionError(f"予期しないエラーが発生しました: {e}", str(input_path)) from e

        return output_path

    def get_file_info(self, file_path: Path) -> dict[str, Any]:
        """
        ファイルの情報を取得する

        Args:
            file_path: ファイルパス

        Returns:
            Dict[str, Any]: ファイル情報
        """
        try:
            probe = ffmpeg.probe(str(file_path))

            # 動画情報を取得
            video_info = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "video"),
                {},
            )

            # 音声情報を取得
            audio_info = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "audio"),
                {},
            )

            # 一般情報
            format_info = probe.get("format", {})

            info = {
                "filename": file_path.name,
                "size": format_file_size(int(format_info.get("size", 0))),
                "duration": float(format_info.get("duration", 0)),
                "format_name": format_info.get("format_name", "不明"),
                "video_codec": video_info.get("codec_name", "不明"),
                "audio_codec": audio_info.get("codec_name", "不明"),
                "audio_bitrate": audio_info.get("bit_rate", "不明"),
                "sample_rate": audio_info.get("sample_rate", "不明"),
            }

            return info

        except Exception as e:
            return {"error": f"ファイル情報の取得に失敗しました: {e}"}

    def format_duration(self, seconds: float) -> str:
        """
        秒数を時間:分:秒の形式にフォーマットする

        Args:
            seconds: 秒数

        Returns:
            str: フォーマットされた時間文字列
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
