"""VideoToAudioConverterクラスのテスト"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.converter import VideoToAudioConverter
from src.exceptions import (
    ConversionError,
    FileInUseError,
    FileNotFoundError,
    InsufficientSpaceError,
    PermissionError,
    UnsupportedFormatError,
)


@pytest.fixture
def mock_validate_ffmpeg() -> Any:
    """FFmpeg検証をモック"""
    with patch("src.converter.validate_ffmpeg"):
        yield


@pytest.fixture
def mock_create_output_directory() -> Any:
    """出力ディレクトリ作成をモック"""
    with patch("src.converter.create_output_directory"):
        yield


@pytest.fixture
def converter(
    tmp_path: Path, mock_validate_ffmpeg: Any, mock_create_output_directory: Any
) -> VideoToAudioConverter:
    """テスト用のコンバーターインスタンス"""
    return VideoToAudioConverter(output_dir=tmp_path / "output", bitrate="192k")


class TestConverterInitialization:
    """コンバーター初期化のテスト"""

    def test_init_default_params(
        self, mock_validate_ffmpeg: Any, mock_create_output_directory: Any
    ) -> None:
        """デフォルトパラメータでの初期化"""
        converter = VideoToAudioConverter()
        assert converter.output_dir == Path("mp3")
        assert converter.bitrate == "192k"

    def test_init_custom_params(
        self, tmp_path: Path, mock_validate_ffmpeg: Any, mock_create_output_directory: Any
    ) -> None:
        """カスタムパラメータでの初期化"""
        output_dir = tmp_path / "custom_output"
        converter = VideoToAudioConverter(output_dir=output_dir, bitrate="320k")
        assert converter.output_dir == output_dir
        assert converter.bitrate == "320k"

    @patch("src.converter.validate_ffmpeg")
    def test_init_validates_ffmpeg(self, mock_validate: MagicMock) -> None:
        """初期化時にFFmpegを検証"""
        with patch("src.converter.create_output_directory"):
            VideoToAudioConverter()
            mock_validate.assert_called_once()

    @patch("src.converter.create_output_directory")
    def test_init_creates_output_directory(
        self, mock_create: MagicMock, mock_validate_ffmpeg: Any, tmp_path: Path
    ) -> None:
        """初期化時に出力ディレクトリを作成"""
        output_dir = tmp_path / "output"
        VideoToAudioConverter(output_dir=output_dir)
        mock_create.assert_called_once_with(output_dir)


class TestConvertFile:
    """convert_fileメソッドのテスト"""

    def test_convert_file_not_exists(self, converter: VideoToAudioConverter) -> None:
        """存在しないファイルの変換"""
        non_existent = Path("nonexistent.mp4")
        with pytest.raises(FileNotFoundError) as exc_info:
            converter.convert_file(non_existent)
        assert "入力ファイルが見つかりません" in str(exc_info.value)

    def test_convert_file_unsupported_format(
        self, converter: VideoToAudioConverter, tmp_path: Path
    ) -> None:
        """サポートされていない形式"""
        text_file = tmp_path / "test.txt"
        text_file.touch()

        with pytest.raises(UnsupportedFormatError) as exc_info:
            converter.convert_file(text_file)
        assert "対応していない形式" in str(exc_info.value)

    @patch("src.converter.ffmpeg")
    @patch("src.converter.check_disk_space")
    @patch("src.converter.get_output_path")
    def test_convert_file_success(
        self,
        mock_get_output: MagicMock,
        mock_check_space: MagicMock,
        mock_ffmpeg: MagicMock,
        converter: VideoToAudioConverter,
        tmp_path: Path,
    ) -> None:
        """正常な変換"""
        input_file = tmp_path / "input.mp4"
        input_file.write_text("dummy video data")
        output_file = tmp_path / "output.mp3"
        mock_get_output.return_value = output_file

        # ffmpeg-pythonのモック設定
        mock_stream = MagicMock()
        mock_ffmpeg.input.return_value = mock_stream
        mock_ffmpeg.output.return_value = mock_stream
        mock_ffmpeg.overwrite_output.return_value = mock_stream

        result = converter.convert_file(input_file)

        assert result == output_file
        mock_ffmpeg.input.assert_called_once_with(str(input_file))
        mock_ffmpeg.run.assert_called_once()

    @patch("src.converter.ffmpeg")
    @patch("src.converter.check_disk_space")
    @patch("src.converter.get_output_path")
    def test_convert_file_with_progress_callback(
        self,
        mock_get_output: MagicMock,
        mock_check_space: MagicMock,
        mock_ffmpeg: MagicMock,
        converter: VideoToAudioConverter,
        tmp_path: Path,
    ) -> None:
        """進行状況コールバック付き変換"""
        input_file = tmp_path / "input.mp4"
        input_file.write_text("dummy")
        output_file = tmp_path / "output.mp3"
        mock_get_output.return_value = output_file

        mock_stream = MagicMock()
        mock_ffmpeg.input.return_value = mock_stream
        mock_ffmpeg.output.return_value = mock_stream
        mock_ffmpeg.overwrite_output.return_value = mock_stream

        callback = MagicMock()
        converter.convert_file(input_file, progress_callback=callback)

        # コールバックが2回呼ばれたことを確認
        assert callback.call_count >= 2

    @patch("src.converter.ffmpeg")
    @patch("src.converter.check_disk_space")
    @patch("src.converter.get_output_path")
    def test_convert_file_permission_error(
        self,
        mock_get_output: MagicMock,
        mock_check_space: MagicMock,
        mock_ffmpeg: MagicMock,
        converter: VideoToAudioConverter,
        tmp_path: Path,
    ) -> None:
        """権限エラー"""
        input_file = tmp_path / "input.mp4"
        input_file.write_text("dummy")
        mock_get_output.return_value = tmp_path / "output.mp3"

        # ffmpegエラーをシミュレート
        import ffmpeg

        error = ffmpeg.Error("ffmpeg", None, b"Permission denied")
        mock_ffmpeg.input.return_value = MagicMock()
        mock_ffmpeg.output.return_value = MagicMock()
        mock_ffmpeg.overwrite_output.return_value = MagicMock()
        mock_ffmpeg.run.side_effect = error
        mock_ffmpeg.Error = ffmpeg.Error

        with pytest.raises(PermissionError) as exc_info:
            converter.convert_file(input_file)
        assert "ファイルアクセス権限がありません" in str(exc_info.value)

    @patch("src.converter.ffmpeg")
    @patch("src.converter.check_disk_space")
    @patch("src.converter.get_output_path")
    def test_convert_file_in_use_error(
        self,
        mock_get_output: MagicMock,
        mock_check_space: MagicMock,
        mock_ffmpeg: MagicMock,
        converter: VideoToAudioConverter,
        tmp_path: Path,
    ) -> None:
        """ファイル使用中エラー"""
        input_file = tmp_path / "input.mp4"
        input_file.write_text("dummy")
        mock_get_output.return_value = tmp_path / "output.mp3"

        import ffmpeg

        error = ffmpeg.Error("ffmpeg", None, b"being used by another process")
        mock_ffmpeg.input.return_value = MagicMock()
        mock_ffmpeg.output.return_value = MagicMock()
        mock_ffmpeg.overwrite_output.return_value = MagicMock()
        mock_ffmpeg.run.side_effect = error
        mock_ffmpeg.Error = ffmpeg.Error

        with pytest.raises(FileInUseError) as exc_info:
            converter.convert_file(input_file)
        assert "ファイルが他のプロセスで使用中です" in str(exc_info.value)

    @patch("src.converter.ffmpeg")
    @patch("src.converter.check_disk_space")
    @patch("src.converter.get_output_path")
    def test_convert_file_no_space_error(
        self,
        mock_get_output: MagicMock,
        mock_check_space: MagicMock,
        mock_ffmpeg: MagicMock,
        converter: VideoToAudioConverter,
        tmp_path: Path,
    ) -> None:
        """容量不足エラー"""
        input_file = tmp_path / "input.mp4"
        input_file.write_text("dummy")
        mock_get_output.return_value = tmp_path / "output.mp3"

        import ffmpeg

        error = ffmpeg.Error("ffmpeg", None, b"No space left on device")
        mock_ffmpeg.input.return_value = MagicMock()
        mock_ffmpeg.output.return_value = MagicMock()
        mock_ffmpeg.overwrite_output.return_value = MagicMock()
        mock_ffmpeg.run.side_effect = error
        mock_ffmpeg.Error = ffmpeg.Error

        with pytest.raises(InsufficientSpaceError) as exc_info:
            converter.convert_file(input_file)
        assert "容量が不足しています" in str(exc_info.value)

    @patch("src.converter.ffmpeg")
    @patch("src.converter.check_disk_space")
    @patch("src.converter.get_output_path")
    def test_convert_file_general_error(
        self,
        mock_get_output: MagicMock,
        mock_check_space: MagicMock,
        mock_ffmpeg: MagicMock,
        converter: VideoToAudioConverter,
        tmp_path: Path,
    ) -> None:
        """一般的な変換エラー"""
        input_file = tmp_path / "input.mp4"
        input_file.write_text("dummy")
        mock_get_output.return_value = tmp_path / "output.mp3"

        import ffmpeg

        error = ffmpeg.Error("ffmpeg", None, b"Invalid codec")
        mock_ffmpeg.input.return_value = MagicMock()
        mock_ffmpeg.output.return_value = MagicMock()
        mock_ffmpeg.overwrite_output.return_value = MagicMock()
        mock_ffmpeg.run.side_effect = error
        mock_ffmpeg.Error = ffmpeg.Error

        with pytest.raises(ConversionError) as exc_info:
            converter.convert_file(input_file)
        assert "変換中にエラーが発生しました" in str(exc_info.value)


class TestGetFileInfo:
    """get_file_infoメソッドのテスト"""

    @patch("src.converter.ffmpeg")
    def test_get_file_info_success(
        self, mock_ffmpeg: MagicMock, converter: VideoToAudioConverter, tmp_path: Path
    ) -> None:
        """ファイル情報取得成功"""
        input_file = tmp_path / "test.mp4"
        input_file.touch()

        # ffmpeg.probeのモック
        mock_ffmpeg.probe.return_value = {
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "bit_rate": "128000",
                    "sample_rate": "44100",
                },
            ],
            "format": {"size": "10485760", "duration": "120.5", "format_name": "mp4"},
        }

        info = converter.get_file_info(input_file)

        assert info["filename"] == "test.mp4"
        assert info["video_codec"] == "h264"
        assert info["audio_codec"] == "aac"
        assert info["duration"] == 120.5

    @patch("src.converter.ffmpeg")
    def test_get_file_info_error(
        self, mock_ffmpeg: MagicMock, converter: VideoToAudioConverter, tmp_path: Path
    ) -> None:
        """ファイル情報取得エラー"""
        input_file = tmp_path / "test.mp4"
        input_file.touch()

        mock_ffmpeg.probe.side_effect = Exception("Probe error")

        info = converter.get_file_info(input_file)

        assert "error" in info
        assert "ファイル情報の取得に失敗しました" in info["error"]


class TestFormatDuration:
    """format_durationメソッドのテスト"""

    def test_format_duration_hours(self, converter: VideoToAudioConverter) -> None:
        """時間付き"""
        assert converter.format_duration(3661) == "01:01:01"
        assert converter.format_duration(7200) == "02:00:00"

    def test_format_duration_minutes_only(self, converter: VideoToAudioConverter) -> None:
        """分のみ"""
        assert converter.format_duration(125) == "02:05"
        assert converter.format_duration(60) == "01:00"

    def test_format_duration_seconds_only(self, converter: VideoToAudioConverter) -> None:
        """秒のみ"""
        assert converter.format_duration(45) == "00:45"
        assert converter.format_duration(0) == "00:00"
