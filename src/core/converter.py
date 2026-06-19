import subprocess
from pathlib import Path


def converter_video(arquivo_entrada, formato_saida="mp4"):
    """
    Converte um arquivo usando FFmpeg.

    Args:
        arquivo_entrada (str): Caminho do arquivo original.
        formato_saida (str): Formato desejado (mp4, mp3, etc).

    Returns:
        str: Caminho do arquivo convertido.
    """

    entrada = Path(arquivo_entrada)

    saida = entrada.with_suffix(f".{formato_saida}")

    comando = [
        "ffmpeg",
        "-i",
        str(entrada),
        str(saida)
    ]

    subprocess.run(
        comando,
        capture_output=True,
        text=True
    )

    return str(saida)