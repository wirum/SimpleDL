from __future__ import annotations

import sys
import threading
import tempfile
import os
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets

try:
    import requests
except Exception:
    requests = None

from core.url import limpar_url
from core.metadata import analisar_video


def try_add_poppins():
    """Try to download Poppins TTF and register it with Qt. Silent on failure."""
    if requests is None:
        return
    try:
        css_url = "https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap"
        r = requests.get(css_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if r.status_code != 200:
            return
        import re
        m = re.search(r"url\((https:[^)]*\.ttf)\)", r.text)
        if not m:
            return
        font_url = m.group(1)
        data = requests.get(font_url, timeout=8).content
        tmp = tempfile.gettempdir()
        fname = os.path.join(tmp, "Poppins-Prototmp.ttf")
        with open(fname, "wb") as f:
            f.write(data)
        QtGui.QFontDatabase.addApplicationFont(fname)
    except Exception:
        return


class AnalysisWorker(QtCore.QObject):
    finished = QtCore.Signal(dict)
    error = QtCore.Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    @QtCore.Slot()
    def run(self):
        try:
            url_limpa = limpar_url(self.url)
            metadata = analisar_video(url_limpa)
            if metadata is None:
                self.error.emit("Vídeo não encontrado")
            else:
                self.finished.emit(metadata)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleDL")
        self.resize(640, 520)

        try_add_poppins()

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        # Styles
        self.setStyleSheet("""
        QMainWindow { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #071026, stop:1 #0b2a4a); }
        QLabel#title { color: #E6F3FF; font-size:22px; font-weight:700; }
        QLabel#subtitle { color: #BBDDF8; font-size:12px; }
        QLineEdit, QComboBox { background: rgba(255,255,255,0.04); color: #E6F3FF; border-radius:8px; padding:8px; }
        QPushButton#accent { background: #1E90FF; color: white; border-radius:10px; padding:8px; }
        QPushButton#accent:hover { background: #187BDB; }
        QProgressBar { background: rgba(255,255,255,0.04); border-radius:6px; height:10px; }
        QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4fb3ff, stop:1 #1E90FF); border-radius:6px; }
        QFrame#card { background: rgba(255,255,255,0.03); border-radius:12px; }
        """)

        v = QtWidgets.QVBoxLayout(central)
        v.setContentsMargins(18, 18, 18, 18)
        v.setSpacing(12)

        title = QtWidgets.QLabel("SimpleDL")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("Baixe vídeos do YouTube com elegância")
        subtitle.setObjectName("subtitle")
        v.addWidget(title)
        v.addWidget(subtitle)

        # Entry row
        row = QtWidgets.QHBoxLayout()
        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText("Cole o link do YouTube aqui…")
        row.addWidget(self.url_edit)
        analyze_btn = QtWidgets.QPushButton("Analisar")
        analyze_btn.setObjectName("accent")
        analyze_btn.clicked.connect(self.on_analyze)
        row.addWidget(analyze_btn)
        clear_btn = QtWidgets.QPushButton("Limpar")
        clear_btn.clicked.connect(self.on_clear)
        row.addWidget(clear_btn)
        v.addLayout(row)

        # Card with shadow/glow
        self.card = QtWidgets.QFrame()
        self.card.setObjectName("card")
        card_layout = QtWidgets.QHBoxLayout(self.card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        self.thumb = QtWidgets.QLabel("🎵")
        self.thumb.setFixedSize(120, 80)
        self.thumb.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.addWidget(self.thumb)
        meta_layout = QtWidgets.QVBoxLayout()
        self.title_meta = QtWidgets.QLabel("Aguardando link…")
        self.title_meta.setStyleSheet("color: #E6F3FF; font-weight:700;")
        self.uploader_meta = QtWidgets.QLabel("")
        self.uploader_meta.setStyleSheet("color: #BBDDF8;")
        meta_layout.addWidget(self.title_meta)
        meta_layout.addWidget(self.uploader_meta)
        card_layout.addLayout(meta_layout)

        # drop shadow effect
        shadow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=24, xOffset=0, yOffset=6)
        shadow.setColor(QtGui.QColor(30, 144, 255, 120))
        self.card.setGraphicsEffect(shadow)

        v.addWidget(self.card)

        # Options row
        opts = QtWidgets.QHBoxLayout()
        self.format_cb = QtWidgets.QComboBox()
        self.format_cb.addItems(["mp4", "mp3", "mkv"])
        opts.addWidget(self.format_cb)
        self.quality_cb = QtWidgets.QComboBox()
        self.quality_cb.addItems(["best", "720p", "480p", "360p"])
        opts.addWidget(self.quality_cb)
        self.download_btn = QtWidgets.QPushButton("⬇️ Baixar")
        self.download_btn.setObjectName("accent")
        self.download_btn.clicked.connect(self.on_download)
        opts.addWidget(self.download_btn)
        v.addLayout(opts)

        # Progress
        bottom = QtWidgets.QHBoxLayout()
        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        bottom.addWidget(self.progress)
        self.status_label = QtWidgets.QLabel("Pronto.")
        self.status_label.setStyleSheet("color:#BBDDF8;")
        bottom.addWidget(self.status_label)
        v.addLayout(bottom)

        self.worker_thread: Optional[QtCore.QThread] = None

    def on_clear(self):
        self.url_edit.clear()
        self.title_meta.setText("Aguardando link…")
        self.uploader_meta.setText("")
        self.progress.setValue(0)
        self.status_label.setText("Pronto.")

    def on_analyze(self):
        url = self.url_edit.text().strip()
        if not url:
            self.status_label.setText("Cole um link antes de analisar")
            return
        self.status_label.setText("Buscando…")
        self.progress.setRange(0, 0)

        worker = AnalysisWorker(url)
        thread = QtCore.QThread()
        worker.moveToThread(thread)
        worker.finished.connect(self._on_analysis_done)
        worker.error.connect(self._on_analysis_error)
        thread.started.connect(worker.run)
        # cleanup when finished
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self.worker_thread = thread
        thread.start()

    def _on_analysis_done(self, metadata: dict):
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        title = metadata.get("title", "Título desconhecido")
        uploader = metadata.get("uploader", "Canal desconhecido")
        duration = metadata.get("duration_string", "—")
        self.title_meta.setText(title)
        self.uploader_meta.setText(f"{uploader} • {duration}")
        self.status_label.setText("Pronto — vídeo encontrado")

    def _on_analysis_error(self, mensagem: str):
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_label.setText(f"Erro: {mensagem}")

    def on_download(self):
        if not self.title_meta.text() or self.title_meta.text() == "Aguardando link…":
            self.status_label.setText("Nenhum vídeo para baixar")
            return
        self.status_label.setText("Iniciando download...")
        # simulate progress in background
        threading.Thread(target=self._simulate_download, daemon=True).start()

    def _simulate_download(self):
        for i in range(101):
            QtCore.QThread.msleep(25)
            QtCore.QMetaObject.invokeMethod(self.progress, "setValue", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(int, i))
        QtCore.QMetaObject.invokeMethod(self.status_label, "setText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, "✅ Download concluído"))


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
