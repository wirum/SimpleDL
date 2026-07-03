from core.downloader import download_video
from core.metadata import analisar_video
from logger import setup_logging, log_download_context, log_download_result
from errors import handle_yt_dlp_error
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def normalize_domain(url: str) -> str:
    """Converte qualquer domínio do YouTube para youtube.com.
    Mantém todos os parâmetros originais.
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    # Caso especial: youtu.be
    if netloc == 'youtu.be':
        path = parsed.path.lstrip('/')
        if path:
            query = parsed.query
            new_query = f"v={path}" + (f"&{query}" if query else "")
            return urlunparse(('https', 'youtube.com', '/watch', '', new_query, ''))
        return url

    # Qualquer subdomínio de youtube.com -> youtube.com
    if netloc.endswith('.youtube.com'):
        return urlunparse(parsed._replace(netloc='youtube.com'))

    # Se não for um domínio conhecido, retorna a URL original
    return url

def strip_playlist_parameters(url: str) -> str:
    """Remove parâmetros relacionados a playlist (list, index, start_radio)."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    playlist_params = {'list', 'index', 'start_radio'}
    new_qs = {k: v for k, v in qs.items() if k not in playlist_params}
    new_query = urlencode(new_qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def ask_playlist_or_single(url: str, logger: logging.Logger) -> str:
    """Se URL contém 'list', pergunta ao usuário se deseja apenas o vídeo ou a playlist.
    Se 'list' existe mas 'v' não, não oferece a opção de vídeo único (pois não há vídeo).
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    if 'list' not in qs:
        return url

    # Se não houver 'v', a URL é apenas uma playlist, não um vídeo único
    if 'v' not in qs:
        logger.info("URL contains 'list' but no 'v' – treating as pure playlist")
        print("URL detectada como apenas uma playlist (não há um vídeo único associado).")
        return url

    # Agora temos 'list' e 'v' -> oferecer as opções
    print("\nFoi detectado que esta URL faz parte de uma playlist.")
    print("O que deseja baixar?")
    print("1. Apenas este vídeo")
    print("2. A playlist inteira")
    choice = input("Escolha: ").strip()

    if choice == "1":
        logger.info("User selected: single video")
        new_url = strip_playlist_parameters(url)
        print("URL ajustada para apenas o vídeo.")
        return new_url
    else:
        logger.info("User selected: playlist")
        print("Mantendo a playlist.")
        return url
    
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
        log_path = project_config.CONFIG.get("log_path", "./logs/downloads.log")
        verbosity = project_config.CONFIG.get("verbosity", "info")
    else:
        current_format = "mp4"
        current_quality = "best"
        config_path = Path.cwd() / "config.yml"
        log_path = "./logs/downloads.log"
        verbosity = "info"

    # Setup enhanced logging
    logger = setup_logging(log_path, verbosity)
    logger.info("SimpleDL CLI started")
    logger.debug(f"Config: {config_path}")

    banner_width = 60
    sep = "=" * banner_width
    print(sep)
    print("SimpleDL CLI".center(banner_width))
    print(sep)
    print()
    print("Comandos:")
    print("  :q       sair")
    print("  :folder  escolher pasta de saida")
    print("  :logs    mostrar caminho do log")
    print("  :format  definir formato/qualidade")
    print("  :config  abrir/criar config.yml")
    print("  :ejs     ativar/desativar EJS solver")
    print()
    print("-" * banner_width)
    print(f"Pasta de saida : {out_dir}")
    print(f"Formato atual  : {current_format}")
    print(f"Qualidade atual: {current_quality}")
    print("-" * banner_width)
    print()
    print("Ctrl+C cancela o download atual.")
    print()

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
        except Exception as e:
            logger.warning(f"Could not open editor: {e}")
            print(f"Please open manually: {path}")

    def _log_metadata(logger, metadata: dict):
        """Write key metadata fields to the log file for traceability."""
        logger.info("--- Metadata ---")
        logger.info(f"Title: {metadata.get('title','')}")
        logger.info(f"Artist: {metadata.get('artist','')}")
        if metadata.get('album'):
            logger.info(f"Album: {metadata.get('album')}")
        if metadata.get('track_number'):
            logger.info(f"Track: {metadata.get('track_number')}")
        if metadata.get('year'):
            logger.info(f"Year: {metadata.get('year')}")
        if metadata.get('duration'):
            logger.info(f"Duration (metadata): {metadata.get('duration')}s")
        logger.info("----------------")

    def _strip_mix_radio(url: str) -> str:
        """If the URL points to an auto-generated YouTube Mix/Radio
        (list=RD...), strip the playlist params so only the single video
        is downloaded. Real playlists (PL, UU, LL, etc.) are left as-is.

        This prevents accidentally downloading YouTube's auto-generated
        mixes, which can contain hundreds of tracks, when the person only
        wanted the one video/song they clicked on.
        """
        try:
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(url.strip())
            q = parse_qs(parsed.query)
            list_id = (q.get("list") or [""])[0]
            if list_id.startswith("RD"):
                from core.url import limpar_url
                try:
                    return limpar_url(url)
                except Exception:
                    return url
        except Exception:
            pass
        return url

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

    def _parse_playlist_range(input_str: str, total: int) -> tuple:
        """Parse playlist range input.
        
        Accepts: single number (5), range (1-10), or comma-separated (1,3,5)
        Returns: (start_idx, end_idx) for slicing, or None if invalid
        """
        input_str = input_str.strip()
        try:
            if ',' in input_str:
                # List of numbers: not implemented yet, but parse first for now
                indices = [int(x.strip()) for x in input_str.split(',')]
                return min(indices) - 1, max(indices)
            elif '-' in input_str:
                # Range
                parts = input_str.split('-')
                a = int(parts[0].strip())
                b = int(parts[1].strip())
                return max(1, a) - 1, min(total, b)
            else:
                # Single number
                n = int(input_str)
                return n - 1, n
        except Exception:
            return None

    try:
        while True:
            try:
                txt = input("URL or command: ").strip()
            except EOFError:
                print("EOF - exiting")
                logger.info("CLI exited via EOF")
                break

            if not txt:
                continue
            if txt.lower() in (":q", "q", "quit", "exit"):
                print("Goodbye!")
                logger.info("CLI exited via :q command")
                break
            if txt.lower() in (":folder", "folder"):
                p = input(f"Enter folder path (current: {out_dir}): ").strip()
                if not p:
                    print("No change.")
                    continue
                newp = Path(p).expanduser()
                try:
                    newp.mkdir(parents=True, exist_ok=True)
                    out_dir = newp
                    # Save to config
                    if project_config:
                        project_config.CONFIG["default_out_dir"] = str(out_dir)
                        try:
                            project_config.save_config()
                            logger.info(f"Output folder changed and saved: {out_dir}")
                        except Exception as e:
                            logger.warning(f"Could not save config: {e}")
                    print(f"Output folder changed to: {out_dir}")
                except Exception as e:
                    logger.error(f"Failed to create folder: {e}")
                    print(f"Error: {e}")
                continue
            if txt.lower() in (":logs", "logs"):
                print(f"Log file: {log_path}")
                continue
            if txt.lower() in (":format", "format"):
                print()
                print("O que deseja baixar?")
                print()
                print("1. Video")
                print("2. Audio")
                kind = input("> ").strip()

                if kind == "1":
                    video_formats = ("mp4", "mkv", "webm")
                    print()
                    print("Formato de video:")
                    print()
                    print("1. MP4")
                    print("2. MKV")
                    print("3. WEBM")
                    fmt_choice = input("> ").strip()
                    fmt_map = {"1": "mp4", "2": "mkv", "3": "webm"}
                    new_fmt = fmt_map.get(fmt_choice)
                    if not new_fmt:
                        print(f"Opcao invalida - mantendo formato atual ({current_format})")
                        new_fmt = current_format if current_format in video_formats else "mp4"

                    print()
                    qual = input(f"Qualidade (best/720p/480p/360p) [atual: {current_quality}]: ").strip().lower()
                    if qual:
                        if qual not in ("best", "720p", "480p", "360p"):
                            print("Qualidade invalida - mantendo atual")
                        else:
                            current_quality = qual
                    current_format = new_fmt

                elif kind == "2":
                    audio_formats = ("mp3", "m4a", "flac", "opus", "wav")
                    print()
                    print("Formato de audio:")
                    print()
                    print("1. MP3")
                    print("2. M4A")
                    print("3. FLAC")
                    print("4. OPUS")
                    print("5. WAV")
                    fmt_choice = input("> ").strip()
                    fmt_map = {"1": "mp3", "2": "m4a", "3": "flac", "4": "opus", "5": "wav"}
                    new_fmt = fmt_map.get(fmt_choice)
                    if not new_fmt:
                        print(f"Opcao invalida - mantendo formato atual ({current_format})")
                        new_fmt = current_format if current_format in audio_formats else "mp3"

                    print()
                    default_bitrate = current_quality if current_quality not in ("best", "720p", "480p", "360p") else "192k"
                    bitrate = input(f"Bitrate (ex: 128k/192k/256k/320k) [atual: {default_bitrate}]: ").strip().lower()
                    if bitrate:
                        current_quality = bitrate
                    elif current_quality in ("best", "720p", "480p", "360p"):
                        current_quality = "192k"
                    current_format = new_fmt

                else:
                    print("Opcao invalida - nenhuma alteracao feita")
                    continue

                print()
                print(f"Atualizado: format={current_format}, quality={current_quality}")
                logger.info(f"Format/quality changed: {current_format}/{current_quality}")
                continue
            if txt.lower() in (":config", "config"):
                print(f"Config file: {config_path}")
                if not Path(config_path).exists():
                    print("No config.yml found - you can create from config.example.yml")
                    create = input("Create config.yml from example? (y/N): ").strip().lower()
                    if create == "y":
                        ex = Path(config_path).parent / "config.example.yml"
                        if ex.exists():
                            try:
                                import shutil
                                shutil.copy(ex, config_path)
                                logger.info(f"Config created from example")
                                print(f"config.yml created at {config_path}")
                                # Reload the config module so commands like :ejs
                                # see it immediately, without restarting the CLI
                                try:
                                    import importlib
                                    if project_config:
                                        importlib.reload(project_config)
                                    else:
                                        try:
                                            import config as project_config
                                        except Exception:
                                            from src import config as project_config
                                    print("Config loaded - :ejs and other config commands are now available")
                                except Exception as e:
                                    logger.warning(f"Config created but could not be reloaded automatically: {e}")
                                    print("Config created, but you may need to restart the CLI for it to take effect")
                            except Exception as e:
                                logger.error(f"Failed to create config: {e}")
                                print(f"Error: {e}")
                        else:
                            print("config.example.yml not found")
                else:
                    edit = input("Open config.yml in editor? (y/N): ").strip().lower()
                    if edit == "y":
                        open_in_editor(Path(config_path))
                continue
            if txt.lower() in (":ejs", "ejs"):
                if not project_config:
                    print("Config module not available - edit config.yml manually")
                    continue
                cur = project_config.CONFIG.get("remote_components")
                if cur:
                    print(f"EJS currently enabled: {cur}")
                    off = input("Disable EJS? (y/N): ").strip().lower()
                    if off == "y":
                        project_config.CONFIG["remote_components"] = None
                        try:
                            project_config.save_config()
                            logger.info("EJS disabled via CLI")
                            print("EJS disabled and saved")
                        except Exception as e:
                            logger.error(f"Failed to save config: {e}")
                            print(f"Error: {e}")
                else:
                    on = input("Enable EJS (ejs:github)? (Y/n): ").strip().lower()
                    if on == "" or on == "y":
                        project_config.CONFIG["remote_components"] = "ejs:github"
                        try:
                            project_config.save_config()
                            logger.info("EJS enabled via CLI")
                            print("EJS enabled and saved")
                        except Exception as e:
                            logger.error(f"Failed to save config: {e}")
                            print(f"Error: {e}")
                continue

            url = txt
            url = normalize_domain(txt)
            url = ask_playlist_or_single(url, logger)
            start_time = time.time()
            download_type = "unknown"
            
            try:
                # Analyze metadata first
                meta = None
                try:
                    meta = analisar_video(url)
                except Exception as e:
                    user_msg = "Could not analyze metadata. Continue anyway? (y/N): "
                    if input(user_msg).strip().lower() != "y":
                        logger.warning(f"Metadata analysis failed: {e}")
                        continue
                    logger.debug(f"Metadata analysis failed: {e}")

                if meta and meta.get("is_playlist"):
                    download_type = "playlist"
                    title = meta.get("title", "(playlist)")
                    entries = meta.get("entries", [])
                    num_items = len(entries)
                    print(f"\nPlaylist: {title} - {num_items} items")
                    choice = input("Download all (y) / range (r) / cancel (n): ").strip().lower()
                    
                    if choice == "n":
                        logger.info("Playlist download cancelled by user")
                        continue
                    
                    sel_indices = None
                    if choice == "r":
                        print()
                        print(f"Playlist com {num_items} videos.")
                        print()
                        rng = input(f"Intervalo (1-{num_items}): ").strip()
                        parsed = _parse_playlist_range(rng, num_items)
                        if not parsed:
                            print("Intervalo invalido - digite novamente (ex: 7, 1-10, 1,3,5)")
                            logger.warning(f"Invalid playlist range: {rng}")
                            rng = input(f"Intervalo (1-{num_items}): ").strip()
                            parsed = _parse_playlist_range(rng, num_items)
                            if not parsed:
                                print("Intervalo invalido - cancelado")
                                logger.warning(f"Invalid playlist range (retry): {rng}")
                                continue
                        a_i, b_i = parsed
                        sel_indices = range(a_i, b_i)
                    else:
                        sel_indices = range(num_items)
                    
                    sel = [entries[i] for i in sel_indices if i < num_items]
                    
                    # Download playlist items
                    success_count = 0
                    fail_count = 0
                    for i, entry in enumerate(sel, 1):
                        item_url = entry.get('webpage_url')
                        item_title = entry.get('title', f'Item {i}')
                        print(f"\n[{i}/{len(sel)}] {item_title}")
                        logger.info(f"Downloading playlist item {i}/{len(sel)}: {item_title}")
                        
                        try:
                            item_start = time.time()
                            log_download_context(logger, item_url, "playlist_item", current_format, current_quality, str(out_dir))
                            download_video(item_url, out_dir, fmt=current_format, quality=current_quality)
                            duration = time.time() - item_start
                            log_download_result(logger, True, duration, filename=item_title)
                            success_count += 1
                        except Exception as e:
                            fail_count += 1
                            duration = time.time() - item_start
                            try:
                                user_msg = handle_yt_dlp_error(e)
                            except Exception:
                                user_msg = "Falha inesperada neste item."
                            print(f"  Erro: {user_msg}")
                            logger.error(f"Playlist item failed: {e}", exc_info=True)
                            log_download_result(logger, False, duration, error=str(e))
                            # Item failure does not stop the playlist - continue with next item
                    
                    logger.info(f"Playlist complete: {success_count} succeeded, {fail_count} failed")
                    print(f"\nPlaylist complete: {success_count} succeeded, {fail_count} failed out of {len(sel)}")
                    continue

                # Single video (or audio, depending on current_format)
                audio_formats = ("mp3", "m4a", "flac", "opus", "wav")
                download_type = "audio" if current_format in audio_formats else "video"
                if meta:
                    _show_metadata(meta)
                    _log_metadata(logger, meta)
                    resp = input("Confirm download? [Enter=yes / e=edit / n=cancel]: ").strip().lower()
                    if resp == "n":
                        print("Cancelled by user.")
                        logger.info("Download cancelled by user (metadata confirmation)")
                        continue
                    if resp == "e":
                        meta = _edit_metadata_interactive(meta)
                    # Build filename template
                    artist = meta.get('artist') or ""
                    title_meta = meta.get('title') or ""
                    def _safe(s: str) -> str:
                        return "".join(c for c in s if c.isalnum() or c in " .-_()").strip()
                    safe_artist = _safe(artist)[:120]
                    safe_title = _safe(title_meta)[:120]
                    filename_template = f"{safe_artist} - {safe_title}" if safe_artist else safe_title
                    log_download_context(logger, url, download_type, current_format, current_quality, str(out_dir))
                    download_video(url, out_dir, fmt=current_format, quality=current_quality, filename_template=filename_template)
                else:
                    log_download_context(logger, url, download_type, current_format, current_quality, str(out_dir))
                    download_video(url, out_dir, fmt=current_format, quality=current_quality)
                
                duration = time.time() - start_time
                log_download_result(logger, True, duration)

            except KeyboardInterrupt:
                duration = time.time() - start_time
                print("\nDownload cancelled by user.")
                logger.warning(f"Download cancelled by user (Ctrl+C) after {duration:.2f}s")
                log_download_result(logger, False, duration, error="User cancelled (Ctrl+C)")
            except Exception as e:
                duration = time.time() - start_time
                try:
                    user_msg = handle_yt_dlp_error(e)
                except Exception:
                    # Never let error formatting itself crash the CLI or leak a traceback
                    user_msg = "Ocorreu um erro inesperado. Verifique o arquivo de log para detalhes."
                print(f"\nErro: {user_msg}")
                logger.error(f"Download failed: {e}", exc_info=True)
                log_download_result(logger, False, duration, error=str(e))
                # Safe mode: continue the CLI loop instead of propagating
                
    except KeyboardInterrupt:
        print("\nExiting...")
        logger.info("CLI exited via Ctrl+C")


if __name__ == '__main__':
    run_cli()