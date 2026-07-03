# SimpleDL

Um downloader em Python baseado em yt-dlp, com foco em automação, organização e flexibilidade.

⚠️ This project is under active development. Expect breaking changes and incomplete features.                              
⚠️ Esse projeto está em desenvolvimento ativo. Espere coisas quebrando e features incompletas.

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
```
SimpleDL/
│
├── src/
│   ├── main.py                    -> Entrada principal
│   ├── cli.py                     -> Interface de linha de comando
│   │
│   └── core/
│       ├── downloader.py          -> Sistema de download (yt-dlp wrapper)
│       ├── url.py                 -> Normalização e tratamento de URLs
│       ├── metadata.py           -> Extração de metadados
│       └── config.py              -> Gerenciamento de configuração
│
├── scripts/
│   ├── bootstrap.bat             -> Instalador automático (Windows)
│   └── bootstrap.sh              -> Instalador automático (Linux/macOS)
│
├── docs/
│   ├── especificacao.md          -> Dependências do projeto
│   ├── known-bugs-and-solutions.md -> Q&A de bugs comuns conhecidos
│   └── video-demonstration/
│       └── demo.mp4              -> Como usar o projeto
│
├── config.yml                   -> Configuração do usuário
├── config.example.yml          -> Exemplo de configuração do usuário
├── requirements.txt            -> Dependências Python
├── LICENSE                     -> Licença
└── README.md                   -> Documentação principal
```
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
