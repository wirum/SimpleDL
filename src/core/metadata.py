"""
Módulo de análise de metadados de vídeos.

Retorna metadados enriquecidos para uso no CLI/UI.
"""
import logging
from typing import Optional, Dict, Any

# Import yt_dlp lazily/optionally so missing dependency doesn't crash at import time.
try:
    import yt_dlp
    from yt_dlp.utils import DownloadError
    YTDLP_AVAILABLE = True
except Exception:
    yt_dlp = None  # type: ignore
    DownloadError = Exception
    YTDLP_AVAILABLE = False

logger = logging.getLogger("simpledl.metadata")


def _best_thumbnail(info: Dict[str, Any]) -> str:
    thumbs = info.get("thumbnails") or []
    if not thumbs:
        return info.get("thumbnail") or ""
    def area(t: Dict[str, Any]):
        return (t.get("width") or 0) * (t.get("height") or 0)
    try:
        best = max(thumbs, key=area)
        return best.get("url") or best.get("url") or ""
    except Exception:
        return info.get("thumbnail") or ""


def analisar_video(url: str) -> Optional[dict]:
    """
    Extrai metadados usando yt-dlp (sem download).

    Retorna dicionário com chaves:
      is_playlist, title, artist, artists, album, track_number, year, tags,
      duration, webpage_url, thumbnail, entries (quando playlist), raw_info
    """
    if not YTDLP_AVAILABLE:
        raise RuntimeError("Dependência ausente: instale 'yt-dlp' (pip install yt-dlp)")

    if not url or not isinstance(url, str):
        raise ValueError("URL inválida: deve ser uma string não-vazia")

    ydl_opts = {"quiet": True, "skip_download": True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except DownloadError as e:
        logger.warning("Erro ao acessar o vídeo/playlist: %s", e)
        return None
    except Exception:
        logger.exception("Erro ao extrair metadados")
        return None

    # Detect playlist
    is_playlist = bool(info.get("entries") and info.get("_type") == "playlist")

    if is_playlist:
        entries = []
        for e in info.get("entries", []):
            if not e:
                continue
            entries.append({
                "id": e.get("id"),
                "title": e.get("title"),
                "webpage_url": e.get("webpage_url") or e.get("url"),
                "duration": e.get("duration"),
            })
        return {
            "is_playlist": True,
            "title": info.get("title") or "",
            "uploader": info.get("uploader") or "",
            "webpage_url": info.get("webpage_url") or url,
            "entries": entries,
            "raw_info": info,
        }

    # single video
    title = info.get("title") or ""
    uploader = info.get("uploader") or ""
    artist = info.get("artist") or uploader or ""
    artists = info.get("artists") or ([info.get("artist")] if info.get("artist") else [])
    album = info.get("album") or ""
    track_number = info.get("track") or info.get("track_number") or None
    year = info.get("release_year") or info.get("year") or None
    tags = info.get("tags") or []
    thumbnail = _best_thumbnail(info)

    metadata = {
        "is_playlist": False,
        "title": title,
        "artist": artist,
        "artists": artists,
        "album": album,
        "track_number": track_number,
        "year": year,
        "tags": tags,
        "duration": info.get("duration"),
        "webpage_url": info.get("webpage_url") or url,
        "thumbnail": thumbnail,
        "raw_info": info,
    }
    return metadata
