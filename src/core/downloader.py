"""Downloader with progress, cancellation, and logging.

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


def download_video(url: str, out_dir: str | Path, format: str = "best") -> None:
    """Download a video to out_dir.

    - Shows a console progress bar
    - Supports Ctrl+C to cancel (raises KeyboardInterrupt)
    - Logs errors to logs/downloads.log (caller should configure logging)
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

    ydl_opts = {
        "outtmpl": str(Path(out_dir) / "%(title)s.%(ext)s"),
        "format": format,
        "progress_hooks": [progress_hook],
        # avoid console clutter
        "quiet": True,
        "noprogress": True,  # we implement our own
    }

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
