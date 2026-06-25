from urllib.parse import urlparse, parse_qs


def limpar_url(url: str) -> str:
    """
    Normaliza uma URL do YouTube para o formato padrão watch?v=ID.

    Suporta:
        - https://www.youtube.com/watch?v=ID
        - https://youtu.be/ID
        - https://www.youtube.com/shorts/ID

    Returns:
        str: URL limpa no formato https://www.youtube.com/watch?v=ID

    Raises:
        ValueError: Se a URL não for reconhecida como um link válido do YouTube.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL inválida: deve ser uma string não-vazia.")

    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")

    # youtu.be/ID
    if host == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/")[0]
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

    # youtube.com
    if host in ("youtube.com", "m.youtube.com"):
        # /shorts/ID
        if parsed.path.startswith("/shorts/"):
            video_id = parsed.path.removeprefix("/shorts/").split("/")[0]
            if video_id:
                return f"https://www.youtube.com/watch?v={video_id}"

        # /watch?v=ID
        parametros = parse_qs(parsed.query)
        video_id = parametros.get("v")
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id[0]}"

    raise ValueError(f"URL não reconhecida como YouTube válido: {url}")