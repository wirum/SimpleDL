import subprocess
from pathlib import Path


def converter_video(arquivo_entrada: str, formato_saida: str = "mp4") -> str:
    """
    Converte um arquivo usando FFmpeg.

    Args:
        arquivo_entrada (str): Caminho do arquivo original.
        formato_saida (str): Formato desejado (mp4, mp3, etc).

    Returns:
        str: Caminho do arquivo convertido.

    Raises:
        FileNotFoundError: Se o arquivo de entrada não existir.
        RuntimeError: Se o FFmpeg retornar erro durante a conversão.
    """
    entrada = Path(arquivo_entrada)

    if not entrada.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {entrada}")

    saida = entrada.with_suffix(f".{formato_saida}")

    comando = [
        "ffmpeg",
        "-i", str(entrada),
        str(saida)
    ]

    resultado = subprocess.run(comando)

    if resultado.returncode != 0:
        raise RuntimeError(
            f"FFmpeg falhou ao converter '{entrada}' para '{formato_saida}' "
            f"(código {resultado.returncode})"
        )

    return str(saida)