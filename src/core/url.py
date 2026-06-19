from urllib.parse import urlparse, parse_qs


def limpar_url(url):
    parsed = urlparse(url)

    parametros = parse_qs(parsed.query)

    video_id = parametros.get("v")

    if not video_id:
        return url

    return f"https://www.youtube.com/watch?v={video_id[0]}"