"""カスタム例外クラス

このモジュールは、動画変換ツールで使用される例外クラスの階層を定義します。
すべての例外は基底クラス VideoConverterError を継承しており、エラーメッセージとファイルパス情報を保持します。

例外階層:
    VideoConverterError (基底クラス)
    ├── FileNotFoundError: 入力ファイルが見つからない
    ├── UnsupportedFormatError: サポートされていないファイル形式
    ├── FFmpegNotFoundError: FFmpegがインストールされていない
    ├── ConversionError: 変換処理中の一般的なエラー
    ├── InsufficientSpaceError: ディスク容量不足
    ├── PermissionError: ファイルアクセス権限エラー
    └── FileInUseError: ファイルが他のプロセスで使用中

使用例:
    try:
        converter.convert_file(input_path)
    except VideoConverterError as e:
        # すべての変換エラーを一括でキャッチ
        print(f"エラー: {e}")
        if e.file_path:
            print(f"対象ファイル: {e.file_path}")
"""

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
