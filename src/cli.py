from core.downloader import download_video


def run_cli():
    """Loop CLI for SimpleDL.

    Commands:
      - paste a YouTube URL to download
      - :q or quit -> exit
      - :folder -> set output folder
      - :logs -> show log file path
    """
    import os
    import sys
    from pathlib import Path
    import logging

    # default out dir
    default_out = Path.cwd() / "downloads"
    out_dir = default_out
    out_dir.mkdir(parents=True, exist_ok=True)

    # logging info
    log_path = Path.cwd() / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    logfile = log_path / "downloads.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logfile, encoding="utf-8"),
        ],
    )

    print("SimpleDL CLI — loop mode. Ctrl+C cancels current download.")
    print("Commands: ':q' or 'quit' to exit, ':folder' to choose folder, ':logs' to show log file")
    print(f"Current output folder: {out_dir}")
    try:
        while True:
            try:
                txt = input("URL or command: ").strip()
            except EOFError:
                print("EOF — exiting")
                break

            if not txt:
                continue
            if txt.lower() in (":q", "q", "quit", "exit"):
                print("Saindo...")
                break
            if txt.lower() in (":folder", "folder"):
                p = input(f"Digite o caminho da pasta (atual: {out_dir}): ").strip()
                if not p:
                    print("Nada alterado")
                    continue
                newp = Path(p).expanduser()
                try:
                    newp.mkdir(parents=True, exist_ok=True)
                    out_dir = newp
                    print(f"Pasta de saída alterada para: {out_dir}")
                except Exception as e:
                    print(f"Falha ao criar pasta: {e}")
                continue
            if txt.lower() in (":logs", "logs"):
                print(f"Log em: {logfile}")
                continue

            url = txt
            try:
                print(f"Iniciando download de: {url}")
                download_video(url, out_dir)
            except KeyboardInterrupt:
                # download_video captures cancellation, but also protect here
                print("Download cancelado pelo usuário")
            except Exception as e:
                logging.exception("Erro durante o download")
                print(f"Erro: {e}")
    except KeyboardInterrupt:
        print("Recebido Ctrl+C — saindo")


if __name__ == '__main__':
    run_cli()
