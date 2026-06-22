import customtkinter as ctk
import pywinstyles
from core.url import limpar_url
from core.metadata import analisar_video

# Configuração inicial do CustomTkinter (Estilo Apple Dark)
ctk.set_appearance_mode("System")  # Segue o tema do sistema (Light/Dark)
ctk.set_default_color_theme("blue") 

class SimpleDLGui(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("SimpleDL")
        self.geometry("500x400")
        
        # Ativa o efeito "Mica" ou "Acrylic" (vidro translúcido do Windows 11)
        # Nota: Se estiver no macOS, o sistema já lida com transparências nativamente se configurado
        pywinstyles.apply_style(self, "mica")
        
        # Deixa o fundo levemente transparente para o efeito aparecer melhor
        self.wm_attributes("-alpha", 0.95)

        # --- Elementos da Interface (UI) ---
        
        # Título Principal
        self.title_label = ctk.CTkLabel(
            self, 
            text="SimpleDL", 
            font=ctk.CTkFont(family="SF Pro Display", size=28, weight="bold")
        )
        self.title_label.pack(pady=(30, 20))

        # Campo de Entrada da URL
        self.url_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Cole a URL do YouTube aqui...", 
            width=400,
            height=40,
            corner_radius=10, # Cantos arredondados estilo Apple
            border_width=1
        )
        self.url_entry.pack(pady=10)

        # Botão de Ação
        self.action_button = ctk.CTkButton(
            self, 
            text="Analisar Vídeo", 
            command=self.processar_link,
            width=200,
            height=40,
            corner_radius=10,
            fg_color="#007AFF", # Azul clássico da Apple
            hover_color="#0056b3"
        )
        self.action_button.pack(pady=15)

        # Card de Status / Metadados (inicia invisível ou limpo)
        self.status_label = ctk.CTkLabel(
            self, 
            text="Aguardando URL...", 
            font=ctk.CTkFont(family="SF Pro Text", size=14)
        )
        self.status_label.pack(pady=20)

    def processar_link(self):
        url_crua = self.url_entry.get().strip()
        if not url_crua:
            self.status_label.configure(text="❌ Por favor, insira uma URL.")
            return

        self.status_label.configure(text="🔍 Analisando...")
        self.update()

        # Usando as funções que você já criou!
        url_limpa = limpar_url(url_crua)
        metadata = analisar_video(url_limpa)

        if metadata:
            texto_status = f"🎬 {metadata['title']}\n👤 {metadata['uploader']}\n⏱️ {metadata['duration_string']}"
            self.status_label.configure(text=texto_status)
            # Aqui você poderia liberar um botão de "Baixar"
        else:
            self.status_label.configure(text="❌ Não foi possível analisar o vídeo.")

if __name__ == "__main__":
    app = SimpleDLGui()
    app.mainloop()