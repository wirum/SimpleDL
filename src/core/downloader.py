"""Downloader with progress, cancellation, format/quality selection, and logging.

Uses yt_dlp and a progress hook to update a console progress bar.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Optional

try:
    from yt_dlp import YoutubeDL
except Exception:  # pragma: no cover - runtime dependency
    YoutubeDL = None


# simple progress bar implementation to avoid requiring extra deps
class ConsoleProgress:
    def __init__(self, width: int = 40):
        self.width = width
        self.lock = threading.Lock()
        self.last_len = 0

    def update(self, downloaded: int, total: Optional[int]):
        with self.lock:
            if total and total > 0:
                frac = downloaded / total
                pct = int(frac * 100)
                bars = int(frac * self.width)
                barstr = "#" * bars + "-" * (self.width - bars)
                out = f"[{barstr}] {pct}% ({downloaded}/{total} bytes)"
            else:
                out = f"Downloaded {downloaded} bytes"
            print("\r" + out + " " * max(0, self.last_len - len(out)), end="", flush=True)
            self.last_len = len(out)

    def done(self):
        print()


class DownloadCancelled(Exception):
    pass


def _build_ydl_opts(out_dir: Path, fmt: str, quality: str) -> dict:
    """Map simple format/quality choices into yt_dlp options.

    This is intentionally conservative: it sets sensible defaults and keeps
    options readable. For advanced users they can edit the downloader.
    """
    out_dir = Path(out_dir)
    opts: dict = {
        "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
        # avoid console clutter
        "quiet": True,
        "noprogress": True,
    }

    # format selection
    if fmt in ("mp3", "m4a"):
        # For audio extraction prefer best audio
        opts["format"] = "bestaudio/best"
        # postprocessors to extract audio
        pp = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3" if fmt == "mp3" else "m4a",
            "preferredquality": "192",
        }]
        # embed thumbnail and metadata when possible
        pp.append({"key": "EmbedThumbnail"})
        pp.append({"key": "FFmpegMetadata"})
        opts["postprocessors"] = pp
        # keepvideo False so final file is audio
        opts["keepvideo"] = False
    else:
        # video formats
        # try to map quality to a simple yt-dlp format string
        if quality == "best":
            opts["format"] = "best"
        elif quality.endswith("p"):
            # e.g. 720p -> bestvideo[height<=720]+bestaudio/best
            try:
                h = int(quality[:-1])
                opts["format"] = f"bestvideo[height<=?{h}]+bestaudio/best"
            except Exception:
                opts["format"] = "best"
        elif quality == "audio-only":
            opts["format"] = "bestaudio/best"
        else:
            opts["format"] = "best"

    # try to write thumbnail separately always (helps embedding)
    opts.setdefault("writethumbnail", True)
    opts.setdefault("embedthumbnail", True)
    opts.setdefault("addmetadata", True)

    return opts


def download_video(url: str, out_dir: str | Path, fmt: str = "mp4", quality: str = "best") -> None:
    """Download a video/audio to out_dir.

    - fmt: desired final format (mp4/mp3/m4a/mkv)
    - quality: simple quality hint (best/720p/480p/360p/audio-only)
    """
    if YoutubeDL is None:
        raise RuntimeError("yt_dlp is required. Install with: pip install yt-dlp")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("simpledl.downloader")

    cancel_event = threading.Event()

    progress = ConsoleProgress()

    def progress_hook(d):
        try:
            status = d.get("status")
            if status == "downloading":
                downloaded = d.get("downloaded_bytes") or 0
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                progress.update(downloaded, total)
                # check cancellation
                if cancel_event.is_set():
                    logger.info("Cancellation requested — aborting download")
                    # raising KeyboardInterrupt will stop the download
                    raise KeyboardInterrupt()
            elif status == "finished":
                progress.done()
                logger.info("Download finished: %s", d.get("filename"))
        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception("Erro no hook de progresso")

    ydl_opts = _build_ydl_opts(Path(out_dir), fmt, quality)
    ydl_opts["progress_hooks"] = [progress_hook]

    try:
        with YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except KeyboardInterrupt:
                # user cancelled
                cancel_event.set()
                logger.warning("Download cancelado pelo usuário")
                raise
            except Exception:
                logger.exception("Erro durante o download")
                raise
    except KeyboardInterrupt:
        # re-raise to let caller inform the user
        raise
    except Exception:
        raise
