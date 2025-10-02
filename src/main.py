#!/usr/bin/env python3
"""MP4からMP3への変換メインプログラム

このモジュールは、動画ファイルをMP3音声ファイルに変換するCLIツールのメインエントリーポイントです。

主な機能:
    - 対話的モード: movieディレクトリ内のファイルをテーブル形式で表示し、選択して変換
    - コマンドラインモード: 特定のファイルを直接変換
    - バッチ変換: 複数ファイルを一括変換
    - ファイル情報表示: FFmpegを使用した詳細なメディア情報の取得
    - Windows環境対応: UTF-8エンコーディングの自動設定

使用例:
    対話的モード:
        $ poetry run mp4tomp3

    特定ファイルを変換:
        $ poetry run mp4tomp3 -f movie/video.mp4

    ビットレート指定:
        $ poetry run mp4tomp3 -f movie/video.mp4 -b 320k
"""

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from src.converter import VideoToAudioConverter
from src.exceptions import VideoConverterError
from src.utils import SUPPORTED_VIDEO_FORMATS, get_video_files, is_supported_video_format

# Windows環境でのUTF-8エンコーディング設定
# PowerShellやコマンドプロンプトでは、デフォルトのコードページがShift-JISなどになっている場合があり、
# 日本語ファイル名が文字化けする問題を防ぐため、UTF-8に強制設定します。
if sys.platform == "win32":
    try:
        import ctypes
        import os

        # Windows APIでコンソールコードページをUTF-8に設定
        # 65001はUTF-8のコードページ番号
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)  # 入力用コードページ
        kernel32.SetConsoleOutputCP(65001)  # 出力用コードページ

        # 標準入出力のエンコーディングをUTF-8に再設定
        # reconfigure()はPython 3.7+で利用可能
        # errors="replace"で、デコードできない文字を?などに置換し、クラッシュを防ぐ
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")

        # 環境変数も設定（FFmpegなど子プロセスでも同じエンコーディングを使用）
        os.environ["PYTHONIOENCODING"] = "utf-8"
        os.environ["PYTHONUTF8"] = "1"  # Python 3.7以降でUTF-8モードを有効化
    except Exception:
        # エラーが発生しても処理を続行（環境によってはcryptoが使えない場合がある）
        pass

app = typer.Typer(
    name="mp4tomp3",
    help="動画ファイルをMP3に変換します。",
    add_completion=False,
)

# Rich Console設定（PowerShell環境での文字化け対策）
console = Console(
    force_terminal=True,
    legacy_windows=False,
)


def print_progress(message: str) -> None:
    """進行状況を表示する"""
    console.print(f"[blue][INFO][/blue] {message}")


def print_error(message: str) -> None:
    """エラーメッセージを表示する"""
    console.print(f"[red][ERROR][/red] {message}")


def print_success(message: str) -> None:
    """成功メッセージを表示する"""
    console.print(f"[green][SUCCESS][/green] {message}")


def list_video_files_table(movie_dir: Path) -> list[Path]:
    """movieディレクトリ内の動画ファイルを表形式で表示する"""
    video_files = get_video_files(movie_dir)

    if not video_files:
        # 動画ファイルがない場合は何も表示せず空リストを返す
        # （呼び出し側で適切なメッセージを表示する）
        return []

    table = Table(title=f"\nmovieディレクトリ内の動画ファイル ({len(video_files)}個)")
    table.add_column("番号", justify="right", style="cyan", no_wrap=True)
    table.add_column("ファイル名", style="magenta")
    table.add_column("サイズ", justify="right", style="green")

    for i, file_path in enumerate(video_files, 1):
        try:
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            table.add_row(str(i), file_path.name, f"{file_size:.1f} MB")
        except OSError:
            table.add_row(str(i), file_path.name, "サイズ不明")

    console.print(table)
    return video_files


def convert_single_file(
    file_path: Path, converter: VideoToAudioConverter, show_info: bool = False
) -> bool:
    """
    単一ファイルを変換する

    Args:
        file_path: 変換するファイルパス
        converter: コンバーターインスタンス
        show_info: ファイル情報を表示するかどうか

    Returns:
        bool: 変換が成功した場合True
    """
    try:
        # ファイル情報を表示
        if show_info:
            info = converter.get_file_info(file_path)
            if "error" in info:
                print_error(info["error"])
            else:
                table = Table(title="ファイル情報")
                table.add_column("項目", style="cyan")
                table.add_column("値", style="green")

                table.add_row("ファイル名", info["filename"])
                table.add_row("サイズ", info["size"])
                table.add_row("時間", converter.format_duration(info["duration"]))
                table.add_row("形式", info["format_name"])
                table.add_row("動画コーデック", info["video_codec"])
                table.add_row("音声コーデック", info["audio_codec"])

                console.print(table)

        # 変換実行
        output_path = converter.convert_file(file_path, print_progress)
        print_success(f"変換完了: {output_path}")
        return True

    except VideoConverterError as e:
        print_error(str(e))
        return False
    except Exception as e:
        print_error(f"予期しないエラー: {e}")
        return False


def convert_interactive(converter: VideoToAudioConverter) -> None:
    """対話的モードで変換を実行する"""
    movie_dir = Path("movie")

    if not movie_dir.exists():
        print_error("movieディレクトリが見つかりません。")
        raise typer.Exit(1)

    while True:
        # ファイル一覧を表示
        video_files = list_video_files_table(movie_dir)

        if not video_files:
            # 動画ファイルがない場合の詳細なメッセージ
            console.print()
            print_error("movieディレクトリに変換可能な動画ファイルがありません。")
            console.print("\n[cyan]対応している動画形式:[/cyan]")
            console.print(f"  {', '.join(sorted(SUPPORTED_VIDEO_FORMATS))}")
            console.print(
                "\n[yellow]ヒント:[/yellow] movieディレクトリに動画ファイルを配置してから再度実行してください。"
            )
            raise typer.Exit(0)

        # ユーザー入力
        console.print(
            "\n[cyan]変換するファイルの番号を入力してください"
            "（0で終了、'all'で全ファイル変換）:[/cyan]"
        )
        try:
            user_input = input("番号: ").strip().lower()

            if user_input in ("0", "exit", "quit"):
                console.print("[yellow]終了します。[/yellow]")
                break
            elif user_input == "all":
                # 全ファイル変換
                success_count = 0
                for file_path in video_files:
                    console.print(f"\n[bold]=== {file_path.name} を変換中 ===[/bold]")
                    if convert_single_file(file_path, converter, show_info=True):
                        success_count += 1

                print_success(
                    f"全{len(video_files)}ファイル中{success_count}ファイルの変換が完了しました。"
                )
            else:
                # 個別ファイル変換
                file_num = int(user_input)

                if 1 <= file_num <= len(video_files):
                    selected_file = video_files[file_num - 1]
                    console.print(f"\n[bold]=== {selected_file.name} を変換中 ===[/bold]")
                    convert_single_file(selected_file, converter, show_info=True)
                else:
                    print_error("無効な番号です。")

        except ValueError:
            print_error("有効な番号を入力してください。")
        except KeyboardInterrupt:
            console.print("\n\n[yellow]変換を中断しました。[/yellow]")
            break


@app.command()
def convert(
    file: Annotated[
        Optional[Path],
        typer.Option("-f", "--file", help="変換する動画ファイルのパス"),
    ] = None,
    bitrate: Annotated[
        str,
        typer.Option(
            "-b",
            "--bitrate",
            help="MP3のビットレート",
        ),
    ] = "192k",
    output: Annotated[
        Path,
        typer.Option("-o", "--output", help="出力ディレクトリ"),
    ] = Path("mp3"),
    list_files: Annotated[
        bool,
        typer.Option("-l", "--list", help="movieディレクトリ内のファイル一覧を表示のみ"),
    ] = False,
    info: Annotated[
        bool,
        typer.Option("--info", help="変換前にファイル情報を表示"),
    ] = False,
) -> None:
    """動画ファイルをMP3に変換します。"""
    # ビットレート検証
    if bitrate not in ("128k", "192k", "256k", "320k"):
        print_error(f"無効なビットレート: {bitrate}. 利用可能: 128k, 192k, 256k, 320k")
        raise typer.Exit(1)

    # ファイル一覧表示のみ
    if list_files:
        movie_dir = Path("movie")
        video_files = list_video_files_table(movie_dir)

        if not video_files:
            console.print()
            print_error("movieディレクトリに変換可能な動画ファイルがありません。")
            console.print("\n[cyan]対応している動画形式:[/cyan]")
            console.print(f"  {', '.join(sorted(SUPPORTED_VIDEO_FORMATS))}")

        return

    try:
        # コンバーター初期化
        print_progress(f"MP3変換ツールを初期化中... (ビットレート: {bitrate})")
        converter = VideoToAudioConverter(output_dir=output, bitrate=bitrate)
        print_success("初期化完了")

        # 特定ファイル変換
        if file:
            if not file.exists():
                print_error(f"ファイルが見つかりません: {file}")
                raise typer.Exit(1)

            if not is_supported_video_format(file):
                print_error(f"対応していない形式です: {file.suffix}")
                raise typer.Exit(1)

            console.print(f"\n[bold]=== {file.name} を変換中 ===[/bold]")
            success = convert_single_file(file, converter, show_info=info)
            raise typer.Exit(0 if success else 1)

        # 対話的モード
        else:
            print_success("対話的モードで開始します")
            convert_interactive(converter)

    except typer.Exit:
        # typer.Exitはそのまま再発生（正常な終了処理）
        raise
    except VideoConverterError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
    except KeyboardInterrupt:
        console.print("\n\n[yellow]ユーザーによって中断されました。[/yellow]")
        raise typer.Exit(1) from None
    except Exception as e:
        print_error(f"予期しないエラーが発生しました: {e}")
        raise typer.Exit(1) from None


def main() -> None:
    """メインエントリーポイント"""
    app()


if __name__ == "__main__":
    main()
