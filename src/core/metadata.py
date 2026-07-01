"""
Módulo de análise de metadados de vídeos.

Este módulo é responsável por extrair informações
de vídeos usando yt-dlp sem fazer o download.
"""

import logging
from typing import Optional

# Import yt_dlp lazily/optionally so missing dependency doesn't crash at import time.
try:
    import yt_dlp
    from yt_dlp.utils import DownloadError
    YTDLP_AVAILABLE = True
except Exception:
    yt_dlp = None  # type: ignore
    DownloadError = Exception
    YTDLP_AVAILABLE = False


def analisar_video(url: str) -> Optional[dict]:
    """
    Analisa os metadados de um vídeo a partir de uma URL.

    Args:
        url (str): URL do vídeo já limpa (sem parâmetros extras).

    Returns:
        dict: Dicionário contendo os metadados do vídeo ou None se houver erro.

    Raises:
        RuntimeError: Se a dependência yt-dlp não estiver instalada.
        ValueError: Quando a URL é inválida.
    """
    logger = logging.getLogger("simpledl.metadata")

    if not YTDLP_AVAILABLE:
        # Raise at runtime with a helpful message; callers should catch and show to users.
        raise RuntimeError("Dependência ausente: instale 'yt-dlp' (pip install yt-dlp)")

    try:
        # Validação básica da URL
        if not url or not isinstance(url, str):
            raise ValueError("URL inválida: deve ser uma string não-vazia")

        # Configuração do yt-dlp para apenas extrair metadados
        ydl_opts = {
            "quiet": True,
            # não baixar, só extrair
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        metadata = {
            "title": info.get("title", "Desconhecido"),
            "uploader": info.get("uploader", "Desconhecido"),
            "duration": info.get("duration", 0),
            "duration_string": info.get("duration_string", "00:00"),
            "thumbnail": info.get("thumbnail", ""),
            "view_count": info.get("view_count", 0),
            "webpage_url": info.get("webpage_url", url),
        }
        return metadata

    except DownloadError as e:
        logger.warning("Erro ao acessar o vídeo: %s", e)
        return None
    except Exception as e:
        logger.exception("Erro ao analisar metadados")
        return None
