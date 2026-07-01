from core.downloader import download_video
from core.metadata import analisar_video


def run_cli():
    """Loop CLI for SimpleDL.

    Commands:
      - paste a YouTube URL to download
      - :q or quit -> exit
      - :folder -> set output folder
      - :logs -> show log file path
      - :format -> choose output format/quality (persisted)
      - :config -> open or create config.yml
      - :ejs -> toggle remote_components (EJS solver) on/off and save to config
    """
    import os
    import sys
    import platform
    from pathlib import Path
    import logging

    # try to import project config (works both when running from repo root and from src/)
    try:
        import config as project_config
    except Exception:
        try:
            from src import config as project_config
        except Exception:
            project_config = None

    # default out dir
    if project_config and project_config.CONFIG.get("default_out_dir"):
        default_out = Path(project_config.CONFIG.get("default_out_dir"))
    else:
        default_out = Path.cwd() / "downloads"
    out_dir = default_out
    out_dir.mkdir(parents=True, exist_ok=True)

    # default format/quality
    if project_config:
        current_format = project_config.CONFIG.get("default_format", "mp4")
        current_quality = project_config.CONFIG.get("default_quality", "best")
        config_path = project_config.CONFIG_PATH
    else:
        current_format = "mp4"
        current_quality = "best"
        config_path = Path.cwd() / "config.yml"

    # logging info
    log_path = Path(project_config.CONFIG.get("log_path")) if project_config else (Path.cwd() / "logs" / "downloads.log")
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )

    print("SimpleDL CLI — loop mode. Ctrl+C cancels current download.")
    print("Commands: ':q' or 'quit' to exit, ':folder' to choose folder, ':logs' to show log file, ':format' to set format/quality, ':config' to open config, ':ejs' to toggle EJS solver")
    print(f"Current output folder: {out_dir}")
    print(f"Current format: {current_format}, quality: {current_quality}")

    def open_in_editor(path: Path):
        try:
            if platform.system() == "Windows":
                os.startfile(str(path))
            elif platform.system() == "Darwin":
                import subprocess
                subprocess.run(["open", str(path)])
            else:
                import subprocess
                subprocess.run(["xdg-open", str(path)])
        except Exception:
            print(f"Abra o arquivo manualmente: {path}")

    def _show_metadata(metadata: dict):
        print("\n=== METADADOS ===")
        print(f"Title       : {metadata.get('title','')}")
        print(f"Artist      : {metadata.get('artist','')}")
        if metadata.get('artists'):
            print(f"Artists     : {', '.join([a for a in metadata.get('artists') if a])}")
        print(f"Album       : {metadata.get('album','')}")
        print(f"Track       : {metadata.get('track_number') or ''}")
        print(f"Year        : {metadata.get('year') or ''}")
        if metadata.get('tags'):
            print(f"Tags        : {', '.join(metadata.get('tags'))}")
        print(f"Duration    : {metadata.get('duration') or ''} s")
        if metadata.get('thumbnail'):
            print(f"Thumbnail   : {metadata.get('thumbnail')}")
        print("=================\n")

    def _edit_metadata_interactive(metadata: dict):
        for key, label in (("title","Title"), ("artist","Artist"), ("album","Album"), ("track_number","Track"), ("year","Year")):
            current = metadata.get(key) or ""
            new = input(f"{label} [{current}]: ").strip()
            if new:
                if key in ("track_number","year"):
                    try:
                        metadata[key] = int(new)
                    except Exception:
                        metadata[key] = new
                else:
                    metadata[key] = new
        return metadata

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
                print(f"Log em: {log_path}")
                continue
            if txt.lower() in (":format", "format"):
                fmt = input("Formato desejado (mp4/mp3/m4a/mkv) [current: %s]: " % current_format).strip().lower()
                if fmt:
                    if fmt not in ("mp4", "mp3", "m4a", "mkv"):
                        print("Formato inválido — mantendo atual")
                    else:
                        current_format = fmt
                qual = input("Qualidade (best/720p/480p/360p/audio-only) [current: %s]: " % current_quality).strip().lower()
                if qual:
                    if qual not in ("best", "720p", "480p", "360p", "audio-only"):
                        print("Qualidade inválida — mantendo atual")
                    else:
                        current_quality = qual
                print(f"Formato atualizado: {current_format}, qualidade: {current_quality}")
                continue
            if txt.lower() in (":config", "config"):
                print(f"Caminho do arquivo de configuração: {config_path}")
                if not config_path.exists():
                    print("Nenhum config.yml encontrado — você pode criar a partir de config.example.yml")
                    create = input("Criar config.yml a partir do exemplo? (y/N): ").strip().lower()
                    if create == "y":
                        ex = Path.cwd() / "config.example.yml"
                        if ex.exists():
                            try:
                                import shutil
                                shutil.copy(ex, config_path)
                                print(f"config.yml criado em {config_path}")
                            except Exception as e:
                                print(f"Falha ao criar config.yml: {e}")
                        else:
                            print("config.example.yml não encontrado")
                else:
                    edit = input("Abrir config.yml no editor padrão? (y/N): ").strip().lower()
                    if edit == "y":
                        open_in_editor(config_path)
                continue
            if txt.lower() in (":ejs", "ejs"):
                # toggle remote_components in config
                if not project_config:
                    print("Módulo de config não disponível — crie config.yml manualmente")
                    continue
                cur = project_config.CONFIG.get("remote_components")
                if cur:
                    print(f"EJS atualmente ativado: {cur}")
                    off = input("Desativar EJS? (y/N): ").strip().lower()
                    if off == "y":
                        project_config.CONFIG["remote_components"] = None
                        try:
                            project_config.save_config()
                            print("EJS desativado e salvo em config.yml")
                        except Exception as e:
                            print(f"Falha ao salvar config: {e}")
                else:
                    on = input("Ativar EJS (remote_components) com 'ejs:github'? (Y/n): ").strip().lower()
                    if on == "" or on == "y":
                        project_config.CONFIG["remote_components"] = "ejs:github"
                        try:
                            project_config.save_config()
                            print("EJS ativado e salvo em config.yml")
                        except Exception as e:
                            print(f"Falha ao salvar config: {e}")
                continue

            url = txt
            try:
                # Analyze metadata first and interact
                meta = None
                try:
                    meta = analisar_video(url)
                except Exception as e:
                    print(f"Falha ao analisar metadados: {e}")

                if meta and meta.get("is_playlist"):
                    title = meta.get("title", "(playlist)")
                    entries = meta.get("entries", [])
                    print(f"Playlist: {title} — {len(entries)} itens")
                    choice = input("Baixar todos? (y) / intervalo (e) / cancelar (n): ").strip().lower()
                    if choice == "n":
                        continue
                    if choice == "e":
                        rng = input("Intervalo (ex: 1-10): ").strip()
                        try:
                            a, b = rng.split("-")
                            a_i = max(1, int(a))
                            b_i = min(len(entries), int(b))
                        except Exception:
                            print("Intervalo inválido — abortando")
                            continue
                        sel = entries[a_i - 1:b_i]
                    else:
                        sel = entries
                    for i, entry in enumerate(sel, start=1):
                        print(f"[{i}/{len(sel)}] {entry.get('title')}")
                        # recursive call: analyze and download each
                        # small sleep could be added to avoid hammering
                        download_video(entry.get('webpage_url'), out_dir, fmt=current_format, quality=current_quality)
                    continue

                # single video
                if meta:
                    _show_metadata(meta)
                    resp = input("Confirmar download? [Enter=sim / e=editar / n=cancelar]: ").strip().lower()
                    if resp == "n":
                        print("Cancelado pelo usuário.")
                        continue
                    if resp == "e":
                        meta = _edit_metadata_interactive(meta)
                    # build filename template
                    artist = meta.get('artist') or ""
                    title_meta = meta.get('title') or ""
                    def _safe(s: str) -> str:
                        return "".join(c for c in s if c.isalnum() or c in " .-_()").strip()
                    safe_artist = _safe(artist)[:120]
                    safe_title = _safe(title_meta)[:120]
                    filename_template = f"{safe_artist} - {safe_title}" if safe_artist else safe_title
                    # pass filename template to downloader
                    download_video(url, out_dir, fmt=current_format, quality=current_quality, filename_template=filename_template)
                else:
                    # if no metadata, proceed with default download
                    download_video(url, out_dir, fmt=current_format, quality=current_quality)

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
