"""
Módulo de análise de metadados de vídeos.

Este módulo é responsável por extrair informações
de vídeos usando yt-dlp sem fazer o download.
"""

import yt_dlp


def analisar_video(url):
    """
    Analisa os metadados de um vídeo a partir de uma URL.
    
    Args:
        url (str): URL do vídeo já limpa (sem parâmetros extras).
    
    Returns:
        dict: Dicionário contendo os metadados do vídeo ou None se houver erro.
              As chaves retornadas são:
              - title: Título do vídeo
              - uploader: Nome do canal/criador
              - duration: Duração em segundos
              - duration_string: Duração formatada (HH:MM:SS)
              - thumbnail: URL da thumbnail
              - view_count: Número de visualizações
              - webpage_url: URL da página
    
    Raises:
        ValueError: Quando a URL é inválida ou o vídeo não pode ser acessado.
    """
    
    try:
        # Validação básica da URL
        if not url or not isinstance(url, str):
            raise ValueError("URL inválida: deve ser uma string não-vazia")
        
        # Configuração do yt-dlp para apenas extrair metadados
        # Não faz download (download=False)
        ydl_opts = {
            'quiet': False,          # Mostra warnings
        }
        
        # Usa um contexto (with) para garantir que os recursos sejam liberados
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extrai as informações do vídeo
            info = ydl.extract_info(url, download=False)
        
        # Monta o dicionário com os metadados desejados
        # Usa .get() para evitar KeyError se algum campo não existir
        metadata = {
            'title': info.get('title', 'Desconhecido'),
            'uploader': info.get('uploader', 'Desconhecido'),
            'duration': info.get('duration', 0),
            'duration_string': info.get('duration_string', '00:00'),
            'thumbnail': info.get('thumbnail', ''),
            'view_count': info.get('view_count', 0),
            'webpage_url': info.get('webpage_url', url),
        }
        
        return metadata
    
    except yt_dlp.utils.DownloadError as e:
        # Erro ao fazer download/extrair informações
        print(f"❌ Erro ao acessar o vídeo: {e}")
        return None
    
    except Exception as e:
        # Qualquer outro erro inesperado
        print(f"❌ Erro desconhecido: {e}")
        return None
