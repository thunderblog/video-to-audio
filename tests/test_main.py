"""メインCLIのテスト"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from src.main import app, convert_single_file, list_video_files_table

runner = CliRunner()


@pytest.fixture
def mock_converter() -> Any:
    """VideoToAudioConverterのモック"""
    with patch("src.main.VideoToAudioConverter") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


class TestCLIBasicCommands:
    """基本的なCLIコマンドのテスト"""

    def test_help_command(self) -> None:
        """ヘルプコマンド"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "動画ファイルをMP3に変換します" in result.stdout

    @patch("src.main.list_video_files_table")
    def test_list_files_option(self, mock_list: MagicMock) -> None:
        """ファイル一覧表示オプション"""
        mock_list.return_value = []
        result = runner.invoke(app, ["-l"])
        assert result.exit_code == 0
        mock_list.assert_called_once()


class TestConvertCommand:
    """変換コマンドのテスト"""

    @patch("src.main.VideoToAudioConverter")
    @patch("src.main.convert_single_file")
    def test_convert_specific_file(
        self, mock_convert: MagicMock, mock_converter_class: MagicMock, tmp_path: Path
    ) -> None:
        """特定ファイル変換"""
        test_file = tmp_path / "test.mp4"
        test_file.touch()
        mock_convert.return_value = True

        result = runner.invoke(app, ["-f", str(test_file)])

        # converter が初期化されたことを確認
        mock_converter_class.assert_called_once()
        mock_convert.assert_called_once()

    def test_convert_nonexistent_file(self) -> None:
        """存在しないファイルを指定"""
        result = runner.invoke(app, ["-f", "nonexistent.mp4"])
        assert result.exit_code == 1
        assert "ファイルが見つかりません" in result.stdout

    @patch("src.main.VideoToAudioConverter")
    def test_convert_unsupported_format(
        self, mock_converter_class: MagicMock, tmp_path: Path
    ) -> None:
        """サポートされていない形式"""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        result = runner.invoke(app, ["-f", str(test_file)])
        assert result.exit_code == 1
        assert "対応していない形式" in result.stdout

    @pytest.mark.skip(reason="CLI integration test - requires full mocking setup")
    def test_convert_with_custom_bitrate(self) -> None:
        """カスタムビットレート指定"""
        pass

    def test_convert_invalid_bitrate(self) -> None:
        """無効なビットレート"""
        result = runner.invoke(app, ["-b", "999k"])
        assert result.exit_code == 1
        assert "無効なビットレート" in result.stdout

    @pytest.mark.skip(reason="CLI integration test - requires full mocking setup")
    def test_convert_with_custom_output(self) -> None:
        """カスタム出力ディレクトリ"""
        pass


class TestListVideoFilesTable:
    """list_video_files_table関数のテスト"""

    @patch("src.main.get_video_files")
    def test_list_empty_directory(self, mock_get_files: MagicMock, tmp_path: Path) -> None:
        """空のディレクトリ"""
        mock_get_files.return_value = []
        result = list_video_files_table(tmp_path)
        assert result == []

    @patch("src.main.get_video_files")
    def test_list_with_files(self, mock_get_files: MagicMock, tmp_path: Path) -> None:
        """ファイルが存在する場合"""
        test_files = [
            tmp_path / "video1.mp4",
            tmp_path / "video2.avi",
        ]
        for f in test_files:
            f.write_text("dummy content")

        mock_get_files.return_value = test_files
        result = list_video_files_table(tmp_path)

        assert len(result) == 2
        assert result == test_files


class TestConvertSingleFile:
    """convert_single_file関数のテスト"""

    def test_convert_success(self, tmp_path: Path, mock_converter: Any) -> None:
        """変換成功"""
        test_file = tmp_path / "test.mp4"
        test_file.touch()
        output_file = tmp_path / "test.mp3"

        mock_converter.convert_file.return_value = output_file
        mock_converter.get_file_info.return_value = {
            "filename": "test.mp4",
            "size": "10 MB",
            "duration": 120.0,
            "format_name": "mp4",
            "video_codec": "h264",
            "audio_codec": "aac",
        }
        mock_converter.format_duration.return_value = "02:00"

        result = convert_single_file(test_file, mock_converter, show_info=False)
        assert result is True
        mock_converter.convert_file.assert_called_once()

    def test_convert_with_info(self, tmp_path: Path, mock_converter: Any) -> None:
        """ファイル情報表示付き変換"""
        test_file = tmp_path / "test.mp4"
        test_file.touch()
        output_file = tmp_path / "test.mp3"

        mock_converter.convert_file.return_value = output_file
        mock_converter.get_file_info.return_value = {
            "filename": "test.mp4",
            "size": "10 MB",
            "duration": 120.0,
            "format_name": "mp4",
            "video_codec": "h264",
            "audio_codec": "aac",
        }
        mock_converter.format_duration.return_value = "02:00"

        result = convert_single_file(test_file, mock_converter, show_info=True)
        assert result is True
        mock_converter.get_file_info.assert_called_once_with(test_file)

    def test_convert_info_error(self, tmp_path: Path, mock_converter: Any) -> None:
        """ファイル情報取得エラー"""
        test_file = tmp_path / "test.mp4"
        test_file.touch()
        output_file = tmp_path / "test.mp3"

        mock_converter.convert_file.return_value = output_file
        mock_converter.get_file_info.return_value = {"error": "情報取得失敗"}

        result = convert_single_file(test_file, mock_converter, show_info=True)
        assert result is True  # 変換は成功


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    @patch("src.main.VideoToAudioConverter")
    def test_converter_initialization_error(self, mock_converter_class: MagicMock) -> None:
        """コンバーター初期化エラー"""
        from src.exceptions import FFmpegNotFoundError

        mock_converter_class.side_effect = FFmpegNotFoundError("FFmpeg not found")
        result = runner.invoke(app, [])
        assert result.exit_code == 1

    @patch("src.main.VideoToAudioConverter")
    @patch("src.main.convert_single_file")
    def test_conversion_error_handling(
        self, mock_convert: MagicMock, mock_converter_class: MagicMock, tmp_path: Path
    ) -> None:
        """変換エラー処理"""
        test_file = tmp_path / "test.mp4"
        test_file.touch()
        mock_convert.return_value = False  # 変換失敗

        result = runner.invoke(app, ["-f", str(test_file)])
        assert result.exit_code == 1
