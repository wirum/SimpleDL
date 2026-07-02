"""Enhanced error handling for SimpleDL.

Provides user-friendly error messages while logging full details for debugging.
"""
import logging
import traceback
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger("simpledl")


class SimpleDLError(Exception):
    """Base exception for SimpleDL."""
    def __init__(self, user_message: str, technical_details: Optional[str] = None):
        self.user_message = user_message
        self.technical_details = technical_details or str(self)
        super().__init__(user_message)


class DownloadError(SimpleDLError):
    """Error during download."""
    pass


class PlaylistError(SimpleDLError):
    """Error processing playlist."""
    pass


class ConfigError(SimpleDLError):
    """Error reading/writing config."""
    pass


def user_friendly_error(func: Callable) -> Callable:
    """Decorator to catch exceptions and show user-friendly messages.
    
    Full traceback is logged, but user sees only the friendly message.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except SimpleDLError as e:
            # Our custom exception: show user message, log technical details
            print(f"\nError: {e.user_message}")
            logger.error(f"[{func.__name__}] {e.user_message}")
            logger.debug(f"Technical details: {e.technical_details}\n{traceback.format_exc()}")
            return None
        except KeyboardInterrupt:
            print("\nDownload cancelado pelo usuário.")
            logger.info("Download cancelado pelo usuário (KeyboardInterrupt)")
            return None
        except Exception as e:
            # Unexpected exception: show generic message, log full traceback
            user_msg = "Erro inesperado durante a operação. Verifique o arquivo de log para detalhes."
            print(f"\nError: {user_msg}")
            logger.error(f"[{func.__name__}] Unexpected error: {type(e).__name__}: {str(e)}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            return None
    return wrapper


def handle_yt_dlp_error(exception: Exception) -> str:
    """Convert yt-dlp error to user-friendly message.
    
    Args:
        exception: Exception from yt-dlp
    
    Returns:
        User-friendly error message
    """
    exc_type = type(exception).__name__
    exc_msg = str(exception)
    
    # Map common yt-dlp errors to friendly messages
    if "403" in exc_msg or "Forbidden" in exc_msg:
        return "Vídeo não acessível (erro 403 - Forbidden). Pode estar bloqueado ou privado."
    elif "404" in exc_msg or "Not Found" in exc_msg:
        return "Vídeo não encontrado (erro 404). URL pode estar incorreta ou vídeo removido."
    elif "HTTP" in exc_msg:
        return f"Erro de conexão: {exc_msg.split(':')[0]}"
    elif "signature" in exc_msg.lower():
        return "Não foi possível resolver a assinatura do vídeo. Tente ativar EJS solver (:ejs)."
    elif "no video" in exc_msg.lower() or "no formats" in exc_msg.lower():
        return "Nenhum formato disponível para este vídeo."
    elif "unavailable" in exc_msg.lower():
        return "Vídeo indisponível ou removido."
    else:
        return f"Erro ao baixar: {exc_msg[:100]}"
