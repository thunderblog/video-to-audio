"""ユーティリティ関数のテスト"""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.exceptions import FFmpegNotFoundError, InsufficientSpaceError
from src.utils import (
    SUPPORTED_VIDEO_FORMATS,
    check_disk_space,
    check_ffmpeg_installed,
    create_output_directory,
    format_file_size,
    get_output_path,
    get_video_files,
    is_supported_video_format,
    validate_ffmpeg,
)


class TestFFmpegValidation:
    """FFmpeg検証のテスト"""

    @patch("subprocess.run")
    def test_check_ffmpeg_installed_success(self, mock_run: MagicMock) -> None:
        """FFmpegがインストールされている場合"""
        mock_run.return_value = MagicMock(returncode=0)
        assert check_ffmpeg_installed() is True
        mock_run.assert_called_once_with(["ffmpeg", "-version"], capture_output=True, check=True)

    @patch("subprocess.run")
    def test_check_ffmpeg_installed_not_found(self, mock_run: MagicMock) -> None:
        """FFmpegがインストールされていない場合"""
        mock_run.side_effect = FileNotFoundError()
        assert check_ffmpeg_installed() is False

    @patch("subprocess.run")
    def test_check_ffmpeg_installed_error(self, mock_run: MagicMock) -> None:
        """FFmpegコマンド実行エラー"""
        mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
        assert check_ffmpeg_installed() is False

    @patch("src.utils.check_ffmpeg_installed")
    def test_validate_ffmpeg_success(self, mock_check: MagicMock) -> None:
        """FFmpeg検証成功"""
        mock_check.return_value = True
        validate_ffmpeg()  # 例外が発生しないことを確認

    @patch("src.utils.check_ffmpeg_installed")
    def test_validate_ffmpeg_failure(self, mock_check: MagicMock) -> None:
        """FFmpeg検証失敗"""
        mock_check.return_value = False
        with pytest.raises(FFmpegNotFoundError) as exc_info:
            validate_ffmpeg()
        assert "FFmpegがインストールされていません" in str(exc_info.value)


class TestFileFormatValidation:
    """ファイル形式検証のテスト"""

    def test_is_supported_video_format_valid(self) -> None:
        """サポートされている形式"""
        for ext in SUPPORTED_VIDEO_FORMATS:
            file_path = Path(f"test{ext}")
            assert is_supported_video_format(file_path) is True

    def test_is_supported_video_format_uppercase(self) -> None:
        """大文字拡張子もサポート"""
        assert is_supported_video_format(Path("test.MP4")) is True
        assert is_supported_video_format(Path("test.AVI")) is True

    def test_is_supported_video_format_invalid(self) -> None:
        """サポートされていない形式"""
        assert is_supported_video_format(Path("test.txt")) is False
        assert is_supported_video_format(Path("test.pdf")) is False
        assert is_supported_video_format(Path("test.mp3")) is False


class TestFileOperations:
    """ファイル操作のテスト"""

    def test_get_output_path(self, tmp_path: Path) -> None:
        """出力パス生成"""
        input_path = Path("movie/video.mp4")
        output_dir = tmp_path / "output"
        result = get_output_path(input_path, output_dir)

        assert result == output_dir / "video.mp3"
        assert result.suffix == ".mp3"

    def test_get_output_path_japanese(self, tmp_path: Path) -> None:
        """日本語ファイル名の出力パス生成"""
        input_path = Path("movie/動画ファイル.mp4")
        output_dir = tmp_path / "output"
        result = get_output_path(input_path, output_dir)

        assert result == output_dir / "動画ファイル.mp3"

    def test_create_output_directory(self, tmp_path: Path) -> None:
        """出力ディレクトリ作成"""
        output_dir = tmp_path / "test_output" / "nested" / "dir"
        assert not output_dir.exists()

        create_output_directory(output_dir)
        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_create_output_directory_already_exists(self, tmp_path: Path) -> None:
        """既存ディレクトリの場合"""
        output_dir = tmp_path / "existing"
        output_dir.mkdir()

        create_output_directory(output_dir)  # エラーが発生しないことを確認
        assert output_dir.exists()


class TestGetVideoFiles:
    """動画ファイル検索のテスト"""

    def test_get_video_files_empty_directory(self, tmp_path: Path) -> None:
        """空のディレクトリ"""
        result = get_video_files(tmp_path)
        assert result == []

    def test_get_video_files_with_videos(self, tmp_path: Path) -> None:
        """動画ファイルが存在する場合"""
        # テスト用ファイルを作成
        (tmp_path / "video1.mp4").touch()
        (tmp_path / "video2.avi").touch()
        (tmp_path / "document.txt").touch()  # 除外される
        (tmp_path / "image.jpg").touch()  # 除外される

        result = get_video_files(tmp_path)
        assert len(result) == 2
        assert all(f.suffix in SUPPORTED_VIDEO_FORMATS for f in result)

    def test_get_video_files_sorted(self, tmp_path: Path) -> None:
        """ファイル名でソートされる"""
        (tmp_path / "c.mp4").touch()
        (tmp_path / "a.mp4").touch()
        (tmp_path / "b.mp4").touch()

        result = get_video_files(tmp_path)
        assert [f.name for f in result] == ["a.mp4", "b.mp4", "c.mp4"]

    def test_get_video_files_nonexistent_directory(self) -> None:
        """存在しないディレクトリ"""
        result = get_video_files(Path("nonexistent"))
        assert result == []


class TestDiskSpace:
    """ディスク容量チェックのテスト"""

    @patch("shutil.disk_usage")
    def test_check_disk_space_sufficient(self, mock_disk_usage: MagicMock, tmp_path: Path) -> None:
        """十分な空き容量がある場合"""
        mock_disk_usage.return_value = MagicMock(
            free=1024 * 1024 * 1024  # 1GB
        )

        check_disk_space(tmp_path / "output.mp3", 100)  # 100MB必要
        # 例外が発生しないことを確認

    @patch("shutil.disk_usage")
    def test_check_disk_space_insufficient(
        self, mock_disk_usage: MagicMock, tmp_path: Path
    ) -> None:
        """空き容量が不足している場合"""
        mock_disk_usage.return_value = MagicMock(
            free=50 * 1024 * 1024  # 50MB
        )

        with pytest.raises(InsufficientSpaceError) as exc_info:
            check_disk_space(tmp_path / "output.mp3", 100)  # 100MB必要

        assert "空き容量が不足しています" in str(exc_info.value)
        assert "必要: 100MB" in str(exc_info.value)

    @patch("shutil.disk_usage")
    def test_check_disk_space_os_error(self, mock_disk_usage: MagicMock, tmp_path: Path) -> None:
        """ディスク容量チェックでOSエラー"""
        mock_disk_usage.side_effect = OSError("Disk error")

        with pytest.raises(InsufficientSpaceError) as exc_info:
            check_disk_space(tmp_path / "output.mp3", 100)

        assert "容量チェック中にエラーが発生しました" in str(exc_info.value)


class TestFormatFileSize:
    """ファイルサイズフォーマットのテスト"""

    def test_format_bytes(self) -> None:
        """バイト単位"""
        assert format_file_size(512) == "512 B"
        assert format_file_size(1023) == "1023 B"

    def test_format_kilobytes(self) -> None:
        """キロバイト単位"""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"

    def test_format_megabytes(self) -> None:
        """メガバイト単位"""
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(int(1.5 * 1024 * 1024)) == "1.5 MB"

    def test_format_gigabytes(self) -> None:
        """ギガバイト単位"""
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_file_size(int(2.5 * 1024 * 1024 * 1024)) == "2.5 GB"

    def test_format_zero(self) -> None:
        """ゼロバイト"""
        assert format_file_size(0) == "0 B"
