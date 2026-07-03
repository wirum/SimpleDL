"""Downloader with progress, cancellation, format/quality selection, and enhanced logging.

Uses yt_dlp and a progress hook to update a console progress bar.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError as YtDlpDownloadError
except Exception:
    YoutubeDL = None
    YtDlpDownloadError = Exception


logger = logging.getLogger("simpledl.downloader")


class _DedupLoggerAdapter:
    """Wraps a logger and suppresses immediately-repeated messages.

    yt-dlp can emit the same warning dozens of times in a row (e.g. missing
    JS runtime, one per format probed). This keeps the terminal/log readable
    by collapsing consecutive duplicates into a single line plus a count,
    without dropping genuinely different messages.
    """
    def __init__(self, wrapped: logging.Logger):
        self._wrapped = wrapped
        self._last_msg = None
        self._repeat_count = 0

    def _flush_repeat_notice(self):
        if self._repeat_count > 0:
            self._wrapped.debug(f"(previous message repeated {self._repeat_count} more time(s))")
        self._repeat_count = 0

    def _emit(self, level_func, msg):
        if msg == self._last_msg:
            self._repeat_count += 1
            return
        self._flush_repeat_notice()
        self._last_msg = msg
        level_func(msg)

    def debug(self, msg):
        # yt-dlp routes some warnings through debug() prefixed with '[warning]'
        self._emit(self._wrapped.debug, msg)

    def info(self, msg):
        self._emit(self._wrapped.info, msg)

    def warning(self, msg):
        self._emit(self._wrapped.warning, msg)

    def error(self, msg):
        self._emit(self._wrapped.error, msg)


def _make_dedup_logger(base_logger: logging.Logger) -> _DedupLoggerAdapter:
    return _DedupLoggerAdapter(base_logger)


class ConsoleProgress:
    def __init__(self, width: int = 40):
        self.width = width
        self.lock = threading.Lock()
        self.last_len = 0
        self.start_time = None

    def update(self, downloaded: int, total: Optional[int]):
        with self.lock:
            if self.start_time is None:
                self.start_time = datetime.now()
            
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
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            logger.debug(f"Progress tracking duration: {duration:.2f}s")


class DownloadCancelled(Exception):
    pass


def _build_ydl_opts(out_dir: Path, fmt: str, quality: str, filename_template: Optional[str] = None) -> dict:
    """Map simple format/quality choices into yt_dlp options.

    This is intentionally conservative: it sets sensible defaults and keeps
    options readable. For advanced users they can edit the downloader.
    """
    out_dir = Path(out_dir)
    if filename_template:
        outtmpl = str(out_dir / (filename_template + ".%(ext)s"))
    else:
        outtmpl = str(out_dir / "%(title)s.%(ext)s")

    opts: dict = {
        "outtmpl": outtmpl,
        "noprogress": True,
    }

    # format selection
    if fmt in ("mp3", "m4a", "flac", "opus", "wav"):
        opts["format"] = "bestaudio/best"

        # quality here is a bitrate hint like "192k" (or legacy "audio-only"/"best").
        # FFmpegExtractAudio expects a bare number (e.g. "192"); flac/wav are
        # lossless and preferredquality doesn't apply to them.
        preferred_quality = "192"
        if isinstance(quality, str) and quality.endswith("k"):
            digits = quality[:-1]
            if digits.isdigit():
                preferred_quality = digits

        pp = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": fmt,
            "preferredquality": preferred_quality,
        }]
        pp.append({"key": "EmbedThumbnail"})
        pp.append({"key": "FFmpegMetadata"})
        opts["postprocessors"] = pp
        opts["keepvideo"] = False
    else:
        if quality == "best":
            opts["format"] = "best"
        elif quality.endswith("p"):
            try:
                h = int(quality[:-1])
                opts["format"] = f"bestvideo[height<=?{h}]+bestaudio/best"
            except Exception:
                opts["format"] = "best"
        elif quality == "audio-only":
            opts["format"] = "bestaudio/best"
        else:
            opts["format"] = "best"

    opts.setdefault("writethumbnail", True)
    opts.setdefault("embedthumbnail", True)
    opts.setdefault("addmetadata", True)

    return opts


def _load_project_config():
    """Load project config module if available."""
    try:
        import config as project_config
        return project_config
    except Exception:
        try:
            from src import config as project_config
            return project_config
        except Exception:
            return None


def download_video(url: str, out_dir: str | Path, fmt: str = "mp4", quality: str = "best", filename_template: Optional[str] = None) -> None:
    """Download a video/audio to out_dir.

    - fmt: desired final format (mp4/mp3/m4a/mkv)
    - quality: simple quality hint (best/720p/480p/360p/audio-only)
    - filename_template: optional sanitized filename (without extension) to use instead of video title
    """
    if YoutubeDL is None:
        raise RuntimeError("yt_dlp is required. Install with: pip install yt-dlp")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cancel_event = threading.Event()
    progress = ConsoleProgress()

    def progress_hook(d):
        try:
            status = d.get("status")
            if status == "downloading":
                downloaded = d.get("downloaded_bytes") or 0
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                progress.update(downloaded, total)
                if cancel_event.is_set():
                    logger.info("Cancellation requested - aborting download")
                    raise KeyboardInterrupt()
            elif status == "finished":
                progress.done()
                logger.info("Download finished: %s", d.get("filename"))
        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception("Error in progress hook")

    ydl_opts = _build_ydl_opts(Path(out_dir), fmt, quality, filename_template)
    ydl_opts["logger"] = _make_dedup_logger(logger)
    ydl_opts["progress_hooks"] = [progress_hook]

    project_config = _load_project_config()
    if project_config:
        rc = project_config.CONFIG.get("remote_components")
        if rc:
            # A API yt-dlp espera uma lista de strings, não uma string única.
            if isinstance(rc, str):
                ydl_opts["remote_components"] = [rc]
            else:
                ydl_opts["remote_components"] = rc
            logger.debug(
                "Using remote_components=%r (type=%s)",
                ydl_opts["remote_components"],
                type(ydl_opts["remote_components"]).__name__,
            )

    try:
        with YoutubeDL(ydl_opts) as ydl:
            logger.debug(f"Starting download with options: format={fmt}, quality={quality}")
            try:
                ydl.download([url])
            except KeyboardInterrupt:
                cancel_event.set()
                logger.warning("Download cancelled by user")
                raise
            except YtDlpDownloadError as e:
                logger.error(f"yt-dlp download error: {e}")
                raise
            except Exception as e:
                logger.exception("Unexpected error during download")
                raise
    except KeyboardInterrupt:
        raise
    except Exception:
        raise