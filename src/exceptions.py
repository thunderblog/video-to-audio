"""カスタム例外クラス"""

from typing import Optional


class VideoConverterError(Exception):
    """ビデオ変換に関する基底例外クラス"""

    def __init__(self, message: str, file_path: Optional[str] = None) -> None:
        """
        初期化
        
        Args:
            message: エラーメッセージ
            file_path: エラーが発生したファイルパス
        """
        super().__init__(message)
        self.message = message
        self.file_path = file_path

    def __str__(self) -> str:
        if self.file_path:
            return f"{self.message} (ファイル: {self.file_path})"
        return self.message


class FileNotFoundError(VideoConverterError):
    """入力ファイルが見つからない場合の例外"""
    pass


class UnsupportedFormatError(VideoConverterError):
    """対応していない形式の場合の例外"""
    pass


class FFmpegNotFoundError(VideoConverterError):
    """FFmpegがシステムに見つからない場合の例外"""
    pass


class ConversionError(VideoConverterError):
    """変換処理中にエラーが発生した場合の例外"""
    pass


class InsufficientSpaceError(VideoConverterError):
    """十分な空き容量がない場合の例外"""
    pass


class PermissionError(VideoConverterError):
    """ファイルアクセス権限がない場合の例外"""
    pass


class FileInUseError(VideoConverterError):
    """ファイルが他のプロセスで使用中の場合の例外"""
    pass
