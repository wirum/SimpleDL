# gui.py
# Versão refeita: visual limpo, estilo Apple-like, compatível com customtkinter
# Observações:
# - Não usa cores de 8 dígitos (alpha) nem tuplas com 'transparent'.
# - Mantém chamadas para limpar_url() e analisar_video() do seu core.
# - Download é um placeholder; substitua pela sua engine real.
# - Requer customtkinter; pywinstyles é opcional (aplica mica/acrylic no Windows).

import platform
import threading
import time
import webbrowser
from typing import Optional

import customtkinter as ctk
try:
    import pywinstyles
except Exception:
    pywinstyles = None
try:
    import requests
except Exception:
    requests = None
try:
    from PIL import Image
    from PIL import ImageTk
    PIL_AVAILABLE = True
except Exception:
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False
import tempfile
import os
import ctypes
import sys

from core.url import limpar_url
from core.metadata import analisar_video

# Aparência
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Modern blue-themed palette (light, dark)
ACCENT = "#1E90FF"  # blue accent
ACCENT_HOVER = "#187BDB"
SUCCESS = "#30D158"
WARNING = "#FF9F0A"
ERROR = "#FF3B30"
# Background: light / dark (we care mostly about dark mode here)
BG = ("#FFFFFF", "#071026")
# Card background slightly lighter than window to create depth
CARD_BG = ("#F7F7F7", "#0E2940")
# Subtle border (kept very soft)
BORDER = ("#E6E6E6", "#11314A")
TEXT_PRIMARY = ("#0B1A2B", "#E6F3FF")
TEXT_SECONDARY = ("#34526A", "#BBDDF8")
MUTED = ("#8E8E93", "#7DA6C9")


def _add_font_from_url(family_name: str, css_url: str = None):
    """Download a Google Fonts CSS and register the first font file on Windows.
    Returns True on success, False otherwise.
    """
    if sys.platform != "win32":
        return False
    if requests is None:
        return False
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        if css_url is None:
            css_url = "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap"
        r = requests.get(css_url, headers=headers, timeout=10)
        if r.status_code != 200:
            return False
        # parse url(...) in css
        import re
        m = re.search(r"url\((https:[^)]*\.ttf)\)", r.text)
        if not m:
            m = re.search(r"url\((https:[^)]*\.woff2)\)", r.text)
        if not m:
            return False
        font_url = m.group(1)
        font_data = requests.get(font_url, headers=headers, timeout=10).content
        tmp = tempfile.gettempdir()
        fname = os.path.join(tmp, f"{family_name}.ttf")
        with open(fname, "wb") as f:
            f.write(font_data)
        FR_PRIVATE = 0x10
        AddFontResourceEx = ctypes.windll.gdi32.AddFontResourceExW
        res = AddFontResourceEx(fname, FR_PRIVATE, 0)
        return res != 0
    except Exception:
        return False

# Tipografias (tenta SF Pro, cai para família padrão)
def font(name: str, size: int, weight: str = "normal"):
    try:
        return ctk.CTkFont(family=name, size=size, weight=weight)
    except Exception:
        return ctk.CTkFont(size=size, weight=weight)


# Dimensões
WINDOW_W, WINDOW_H = 560, 480
PADDING = 20


class SimpleDLGui(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Try to install Poppins from Google Fonts (Windows only, optional)
        installed = _add_font_from_url("Poppins")
        family = "Poppins" if installed else None

        # Fonts — create after root exists
        self.TITLE_FONT = font(family or "Segoe UI", 26, "bold")
        self.SUB_FONT = font(family or "Segoe UI", 11)
        self.ENTRY_FONT = font(family or "Segoe UI", 12)
        self.META_TITLE_FONT = font(family or "Segoe UI", 13, "bold")
        self.META_SUB_FONT = font(family or "Segoe UI", 11)

        self.title("SimpleDL")
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)

        # Optional glass style
        self._apply_glass_style()

        # Root layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top header and optional background pattern
        self.configure(fg_color=BG)
        if PIL_AVAILABLE:
            try:
                # generate a simple vertical blue gradient
                w, h = WINDOW_W, WINDOW_H
                img = Image.new("RGB", (w, h), "#071026")
                top = (6, 30, 80)
                bottom = (10, 60, 120)
                for y in range(h):
                    t = y / (h - 1)
                    r = int(top[0] * (1 - t) + bottom[0] * t)
                    g = int(top[1] * (1 - t) + bottom[1] * t)
                    b = int(top[2] * (1 - t) + bottom[2] * t)
                    for x in range(w):
                        img.putpixel((x, y), (r, g, b))
                from customtkinter import CTkImage
                bg_image = CTkImage(img, size=(w, h))
                bg_label = ctk.CTkLabel(self, image=bg_image, text="")
                bg_label.grid(row=1, column=0, sticky="nsew")
            except Exception:
                pass
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING, pady=(PADDING, 8))
        header.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(header, text="SimpleDL", font=self.TITLE_FONT, text_color=TEXT_PRIMARY)
        self.title_label.grid(row=0, column=0, sticky="w")
        self.subtitle = ctk.CTkLabel(header, text="Primeiro teste com GUI", font=self.SUB_FONT, text_color=TEXT_SECONDARY)
        self.subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Main content frame
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=1, column=0, sticky="nsew", padx=PADDING, pady=(0, PADDING))
        main.grid_columnconfigure(0, weight=1)

        # URL entry area
        entry_frame = ctk.CTkFrame(main, fg_color="transparent")
        entry_frame.grid(row=0, column=0, sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(entry_frame, placeholder_text="Cole o link do YouTube aqui…", font=self.ENTRY_FONT, height=44, corner_radius=12)
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.url_entry.bind("<Return>", lambda e: self.processar_link())

        btns = ctk.CTkFrame(entry_frame, fg_color="transparent")
        btns.grid(row=0, column=1)

        self.analyze_btn = ctk.CTkButton(btns, text="Analisar", width=120, height=44, fg_color=ACCENT, hover_color=ACCENT_HOVER, font=self.ENTRY_FONT, command=self.processar_link)
        self.analyze_btn.grid(row=0, column=0, padx=(0, 8))

        self.clear_btn = ctk.CTkButton(btns, text="Limpar", width=90, height=44, fg_color="transparent", hover_color=("#F2F2F7", "#2E2E30"), font=self.ENTRY_FONT, command=self._clear_entry)
        self.clear_btn.grid(row=0, column=1)

        # Result card with subtle glow (outer frame)
        outer = ctk.CTkFrame(main, corner_radius=18, fg_color=ACCENT, border_width=0)
        outer.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        outer.grid_columnconfigure(0, weight=1)
        # inner card sits inside outer to create glow/border effect
        self.result_card = ctk.CTkFrame(outer, corner_radius=14, fg_color=CARD_BG, border_width=0)
        self.result_card.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.result_card.grid_columnconfigure(1, weight=1)

        # Thumbnail / placeholder
        self.thumb = ctk.CTkLabel(self.result_card, text="", width=120, height=80, fg_color=("#2E0E0E", "#4A1A1A"), corner_radius=12, font=self.META_TITLE_FONT)
        # small decorative badge icon in thumb
        self.thumb.configure(text="Thumb")
        self.thumb.grid(row=0, column=0, rowspan=2, padx=12, pady=12)

        # Metadata
        self.title_meta = ctk.CTkLabel(self.result_card, text="Aguardando link…", font=self.META_TITLE_FONT, text_color=TEXT_PRIMARY, anchor="w")
        self.title_meta.grid(row=0, column=1, sticky="w", padx=(6, 12), pady=(14, 0))
        self.uploader_meta = ctk.CTkLabel(self.result_card, text="", font=self.META_SUB_FONT, text_color=TEXT_SECONDARY, anchor="w")
        self.uploader_meta.grid(row=1, column=1, sticky="w", padx=(6, 12))

        # Options (format / quality)
        opts = ctk.CTkFrame(main, fg_color="transparent")
        opts.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        opts.grid_columnconfigure((0,1,2), weight=1)

        self.format_menu = ctk.CTkOptionMenu(opts, values=["mp4", "mp3", "mkv"], font=self.SUB_FONT)
        self.format_menu.grid(row=0, column=0, padx=(0, 8))
        self.quality_menu = ctk.CTkOptionMenu(opts, values=["best", "720p", "480p", "360p"], font=self.SUB_FONT)
        self.quality_menu.grid(row=0, column=1, padx=(0, 8))

        self.download_btn = ctk.CTkButton(opts, text="⬇️ Baixar", fg_color=ACCENT, hover_color=ACCENT_HOVER, font=self.ENTRY_FONT, command=self._start_download, corner_radius=14)
        self.download_btn.grid(row=0, column=2)

        # Progress bar and status
        status_frame = ctk.CTkFrame(main, fg_color="transparent")
        status_frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        status_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(status_frame)
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.status_label = ctk.CTkLabel(status_frame, text="Pronto.", font=self.SUB_FONT, text_color=TEXT_SECONDARY)
        self.status_label.grid(row=0, column=1)

        # State
        self.metadata_atual: Optional[dict] = None
        self._progress_anim = False
        self._progress_after = None

        self._show_idle_state()

    # ---------- Estilo de Plataforma ----------
    def _apply_glass_style(self):
        try:
            ver = platform.release()
            if pywinstyles:
                if ver == "11":
                    pywinstyles.apply_style(self, "mica")
                else:
                    pywinstyles.apply_style(self, "acrylic")
        except Exception:
            # não crítico — segue sem efeito
            pass
        try:
            self.wm_attributes("-alpha", 0.99)
        except Exception:
            pass
    # (Old component builders removed; UI constructed inline in __init__)

    # ---------- Helpers UI ----------
    def _on_entry_change(self, event=None):
        texto = self.url_entry.get().strip()
        if not texto:
            self.url_entry.configure(border_color=BORDER)
        elif "youtube.com/" in texto or "youtu.be/" in texto:
            self.url_entry.configure(border_color=ACCENT)
        else:
            self.url_entry.configure(border_color=WARNING)

    def _show_idle_state(self):
        self.status_label.configure(text="Aguardando link ✨", text_color=TEXT_SECONDARY)
        self._set_progress_value(0.0)
        self._hide_meta()
        self.download_btn.configure(state="disabled")

    def _show_error(self, mensagem: str):
        self._stop_progress_anim()
        self.status_label.configure(text=mensagem, text_color=ERROR)
        self._hide_meta()
        self.download_btn.configure(state="disabled")

    def _show_message(self, mensagem: str, color=TEXT_PRIMARY):
        self.status_label.configure(text=mensagem, text_color=color)

    def _show_meta(self, title: str, uploader: str, duration: str):
        self.title_meta.configure(text=title)
        self.uploader_meta.configure(text=f"Canal: {uploader} • {duration}")
        self.download_btn.configure(state="normal")

    def _hide_meta(self):
        self.title_meta.configure(text="Aguardando link…")
        self.uploader_meta.configure(text="")

    # ---------- Clipboard / Entry ----------
    def _copy_link(self):
        link = self.url_entry.get().strip()
        if link:
            try:
                self.clipboard_clear()
                self.clipboard_append(link)
                self._show_message("Link copiado ✅")
            except Exception:
                self._show_error("Falha ao copiar")

    def _clear_entry(self):
        self.url_entry.delete(0, "end")
        self._show_idle_state()

    # ---------- Progresso animado (simula busca) ----------
    def _start_progress_anim(self, text="Buscando"):
        if self._progress_anim:
            return
        self._progress_anim = True
        self._animate_progress(0.02, text)

    def _animate_progress(self, value: float, text: str):
        if not self._progress_anim:
            return
        # Cicla entre 0.2 e 0.95 para parecer ativo
        next_value = value + 0.02
        if next_value > 0.95:
            next_value = 0.2
        self.progress.set(next_value)
        self.status_label.configure(text=f"{text}…", text_color=TEXT_SECONDARY)
        self._progress_after = self.after(60, lambda: self._animate_progress(next_value, text))

    def _stop_progress_anim(self, final: float = 0.0):
        if self._progress_after:
            try:
                self.after_cancel(self._progress_after)
            except Exception:
                pass
            self._progress_after = None
        self._progress_anim = False
        self._set_progress_value(final)

    def _set_progress_value(self, value: float):
        try:
            # set progress bar
            self.progress.set(value)
        except Exception:
            pass
        # show percentage text; make 0% use primary (white) color
        try:
            pct = int(value * 100)
            if pct == 0:
                self.status_label.configure(text=f"{pct}%", text_color=TEXT_PRIMARY)
            else:
                self.status_label.configure(text=f"{pct}%", text_color=TEXT_SECONDARY)
        except Exception:
            pass

    # ---------- Fluxo principal: análise do link ----------
    def processar_link(self):
        url_crua = self.url_entry.get().strip()
        if not url_crua:
            self._show_error("❌ Cole um link antes de analisar")
            return

        self._start_progress_anim("Vasculhando o YouTube")
        self._hide_meta()
        self.update()

        threading.Thread(target=self._run_analysis_thread, args=(url_crua,), daemon=True).start()

    def _run_analysis_thread(self, url_crua: str):
        try:
            url_limpa = limpar_url(url_crua)
            metadata = analisar_video(url_limpa)
            self.after(0, lambda: self._on_analysis_done(metadata))
        except Exception as e:
            self.after(0, lambda: self._on_analysis_error(f"⚠️ Erro inesperado: {e}"))

    def _on_analysis_done(self, metadata: Optional[dict]):
        self._stop_progress_anim(0.0)
        if metadata:
            self.metadata_atual = metadata
            title = metadata.get("title", "Título desconhecido")
            uploader = metadata.get("uploader", "Canal desconhecido")
            duration = metadata.get("duration_string", "—")
            self._show_message("Pronto — vídeo encontrado", color=TEXT_PRIMARY)
            self._show_meta(title, uploader, duration)
        else:
            self._on_analysis_error("❌ Vídeo não encontrado. Verifique o link.")

    def _on_analysis_error(self, mensagem: str):
        self._stop_progress_anim(0.0)
        self._show_error(mensagem)

    # ---------- Download (placeholder) ----------
    def _start_download(self):
        if not self.metadata_atual:
            self._show_message("Nenhum vídeo para baixar", color=WARNING)
            return

        # desativa botões enquanto "baixa"
        self.analyze_btn.configure(state="disabled")
        self.download_btn.configure(state="disabled")
        self._show_message("⬇️ Iniciando download...", color=TEXT_PRIMARY)

        threading.Thread(target=self._simulate_download, daemon=True).start()

    def _simulate_download(self):
        # Simula progresso de download
        for i in range(1, 101):
            time.sleep(0.02)
            v = i / 100.0
            self.after(0, lambda vv=v: self._set_progress_value(vv))
        self.after(0, self._on_download_done)

    def _on_download_done(self):
        self._show_message("✅ Download concluído", color=SUCCESS)
        self.analyze_btn.configure(state="normal")
        self.download_btn.configure(state="normal")

    # ---------- Abrir no navegador ----------
    def _open_in_browser(self):
        if not self.metadata_atual:
            self._show_message("Nenhum vídeo para abrir", color=WARNING)
            return
        url = self.metadata_atual.get("webpage_url") or self.metadata_atual.get("url")
        if url:
            try:
                webbrowser.open(url)
            except Exception:
                self._show_message("Não foi possível abrir o navegador", color=ERROR)
        else:
            self._show_message("URL do vídeo indisponível", color=WARNING)


if __name__ == "__main__":
    app = SimpleDLGui()
    app.mainloop()