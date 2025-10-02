"""例外クラスのテスト"""

import pytest

from src.exceptions import (
    ConversionError,
    FFmpegNotFoundError,
    FileInUseError,
    FileNotFoundError,
    InsufficientSpaceError,
    PermissionError,
    UnsupportedFormatError,
    VideoConverterError,
)


class TestVideoConverterError:
    """VideoConverterError基底クラスのテスト"""

    def test_basic_error(self) -> None:
        """基本的なエラーメッセージ"""
        error = VideoConverterError("テストエラー")
        assert str(error) == "テストエラー"
        assert error.message == "テストエラー"
        assert error.file_path is None

    def test_error_with_file_path(self) -> None:
        """ファイルパス付きエラー"""
        error = VideoConverterError("テストエラー", "/path/to/file.mp4")
        assert "テストエラー" in str(error)
        assert "/path/to/file.mp4" in str(error)
        assert error.file_path == "/path/to/file.mp4"

    def test_error_inheritance(self) -> None:
        """Exceptionを継承している"""
        error = VideoConverterError("test")
        assert isinstance(error, Exception)


class TestFileNotFoundError:
    """FileNotFoundError例外のテスト"""

    def test_file_not_found_error(self) -> None:
        """ファイルが見つからないエラー"""
        error = FileNotFoundError("ファイルが見つかりません", "movie/video.mp4")
        assert isinstance(error, VideoConverterError)
        assert "ファイルが見つかりません" in str(error)
        assert "movie/video.mp4" in str(error)


class TestUnsupportedFormatError:
    """UnsupportedFormatError例外のテスト"""

    def test_unsupported_format_error(self) -> None:
        """対応していない形式のエラー"""
        error = UnsupportedFormatError("対応していない形式", "file.txt")
        assert isinstance(error, VideoConverterError)
        assert "対応していない形式" in str(error)


class TestFFmpegNotFoundError:
    """FFmpegNotFoundError例外のテスト"""

    def test_ffmpeg_not_found_error(self) -> None:
        """FFmpegが見つからないエラー"""
        error = FFmpegNotFoundError("FFmpegがインストールされていません")
        assert isinstance(error, VideoConverterError)
        assert "FFmpegがインストールされていません" in str(error)

    def test_ffmpeg_error_no_file_path(self) -> None:
        """ファイルパスなしでも動作"""
        error = FFmpegNotFoundError("FFmpegがインストールされていません")
        assert error.file_path is None


class TestConversionError:
    """ConversionError例外のテスト"""

    def test_conversion_error(self) -> None:
        """変換エラー"""
        error = ConversionError("変換に失敗しました", "input.mp4")
        assert isinstance(error, VideoConverterError)
        assert "変換に失敗しました" in str(error)
        assert "input.mp4" in str(error)


class TestInsufficientSpaceError:
    """InsufficientSpaceError例外のテスト"""

    def test_insufficient_space_error(self) -> None:
        """容量不足エラー"""
        error = InsufficientSpaceError("空き容量が不足しています")
        assert isinstance(error, VideoConverterError)
        assert "空き容量が不足しています" in str(error)


class TestPermissionError:
    """PermissionError例外のテスト"""

    def test_permission_error(self) -> None:
        """権限エラー"""
        error = PermissionError("アクセス権限がありません", "protected.mp4")
        assert isinstance(error, VideoConverterError)
        assert "アクセス権限がありません" in str(error)
        assert "protected.mp4" in str(error)


class TestFileInUseError:
    """FileInUseError例外のテスト"""

    def test_file_in_use_error(self) -> None:
        """ファイル使用中エラー"""
        error = FileInUseError("ファイルが使用中です", "locked.mp4")
        assert isinstance(error, VideoConverterError)
        assert "ファイルが使用中です" in str(error)
        assert "locked.mp4" in str(error)


class TestExceptionHierarchy:
    """例外階層のテスト"""

    def test_all_inherit_from_base(self) -> None:
        """すべての例外がVideoConverterErrorを継承"""
        exceptions = [
            FileNotFoundError("test"),
            UnsupportedFormatError("test"),
            FFmpegNotFoundError("test"),
            ConversionError("test"),
            InsufficientSpaceError("test"),
            PermissionError("test"),
            FileInUseError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, VideoConverterError)
            assert isinstance(exc, Exception)

    def test_catch_all_with_base_class(self) -> None:
        """基底クラスですべてキャッチできる"""
        try:
            raise ConversionError("変換エラー", "test.mp4")
        except VideoConverterError as e:
            assert "変換エラー" in str(e)
            assert e.file_path == "test.mp4"

    def test_specific_exception_handling(self) -> None:
        """特定の例外を個別にキャッチできる"""
        with pytest.raises(FileNotFoundError):
            raise FileNotFoundError("ファイルなし")

        with pytest.raises(PermissionError):
            raise PermissionError("権限なし")
