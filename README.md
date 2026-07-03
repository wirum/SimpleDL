# SimpleDL

Um downloader em Python baseado em yt-dlp, com foco em automação, organização e flexibilidade.

## 📌 Sobre o projeto

O SimpleDL é uma ferramenta de linha de comando para download de vídeos e áudios, com suporte a playlists, normalização de URLs e automações de instalação.

O objetivo é simplificar o uso do yt-dlp com uma camada extra de conveniência e configuração automatizada.

## 🚀 Funcionalidades

- Download de vídeos e áudios via yt-dlp
- Suporte a playlists (com escolha entre vídeo único ou playlist completa)
- Normalização de URLs (YouTube, YouTube Music, youtu.be)
- Sistema de bootstrap com instalação automática de dependências
- Integração com FFmpeg para processamento de mídia
- Sistema de configuração via YAML

## 🛠️ Tecnologias utilizadas

- Python
- yt-dlp
- FFmpeg (ou FFmpeg for yt-dlp)
- PyYAML

## 📂 Estrutura do projeto

SimpleDL/
│
├── main.py            -> Entrada principal
├── cli.py             -> Interface de linha de comando
├── core/
│   ├── downloader.py  -> Sistema de download (yt-dlp wrapper)
│   ├── url.py         -> Normalização e tratamento de URLs
│   ├── metadata.py    -> Extração de metadados
│
├── config.py          -> Gerenciamento de configuração
├── bootstrap.bat      -> Instalador automático
├── requirements.txt   -> Dependências Python
└── docs/              -> Documentação

## ⚙️ Instalação

Clone o repositório:

```bash
git clone https://github.com/wirum/SimpleDL.git
```

Acesse a pasta:

```bash
cd SimpleDL
```

Execute o bootstrap:

```bash
bootstrap.bat
```

## 📦 Dependências

- yt-dlp
- FFmpeg (ou pacote equivalente para Windows)
- Python 3.10+

## 🧠 Objetivo

O SimpleDL foi criado como um projeto de aprendizado e experimentação em:

- automação de downloads
- integração com ferramentas externas
- processamento de mídia
- design de CLIs mais inteligentes

## 📈 Futuras melhorias

- interface gráfica
- histórico de downloads
- melhor sistema de filas
- suporte a múltiplas plataformas além do YouTube
- sistema de plugins

## 👨‍💻 Autor

Desenvolvido por um estudante tentando não enlouquecer com URLs e dependências externas e um pouco de IA kkk
