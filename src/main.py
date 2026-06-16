"""
SimpleDL - Downloader de Mídia Minimalista

Ponto de entrada da aplicação. Responsável por:
1. Receber a URL do usuário
2. Chamar a função de análise
3. Exibir os dados formatados no terminal
"""

from core.metadata import analisar_video


def detectar_playlist(url):
    """
    Detecta se a URL contém parâmetros de playlist.
    
    Args:
        url (str): URL original do YouTube.
    
    Returns:
        tuple: (url_limpa, tem_playlist, parametros)
    """
    parametros = ""
    tem_playlist = False
    
    if '&' in url:
        partes = url.split('&')
        url_limpa = partes[0]
        parametros = '&'.join(partes[1:])
        
        # Verifica se há parâmetros de playlist
        if 'list=' in parametros or 'start_radio=' in parametros:
            tem_playlist = True
    else:
        url_limpa = url
    
    return url_limpa, tem_playlist, parametros


def exibir_aviso_playlist(parametros):
    """
    Exibe um aviso formatado sobre detecção de playlist.
    
    Args:
        parametros (str): String com os parâmetros detectados.
    
    Returns:
        bool: True se usuário deseja continuar, False caso contrário.
    """
    print("\n" + "⚠️ " * 15)
    print("\n🚨 ATENÇÃO 🚨\n")
    print(f"Seu link possui uma playlist embutida:")
    print(f"  {parametros}\n")
    print("Se você não desejava analisar TODA a playlist,")
    print("por favor negue a autorização.\n")
    print("⚠️ " * 15 + "\n")
    
    while True:
        resposta = input("Deseja analisar TODA a playlist? [Sim/Não]: ").strip().lower()
        
        if resposta in ['sim', 's']:
            return True
        elif resposta in ['não', 'nao', 'n']:
            print("\n❌ Análise cancelada pelo usuário.\n")
            return False
        else:
            print("❌ Resposta inválida. Digite 'Sim' ou 'Não'.\n")


def limpar_url(url):
    """
    Remove parâmetros extras da URL (como &list=).
    
    Args:
        url (str): URL do YouTube.
    
    Returns:
        str: URL limpa.
    """
    # Remove tudo após o "&" para eliminar parâmetros extras
    if '&' in url:
        url = url.split('&')[0]
    
    return url.strip()


def formatar_views(views):
    """
    Formata o número de visualizações de forma legível.
    
    Args:
        views (int): Número de visualizações.
    
    Returns:
        str: Número formatado (ex: 1.5M, 500K).
    """
    if views is None or views == 0:
        return "Desconhecido"
    
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    else:
        return str(views)


def exibir_metadados(metadata):
    """
    Exibe os metadados do vídeo de forma formatada no terminal.
    
    Args:
        metadata (dict): Dicionário com os metadados do vídeo.
    """
    print("\n" + "=" * 50)
    print("SimpleDL Metadata")
    print("=" * 50 + "\n")
    
    print(f"Título: {metadata['title']}")
    print(f"Canal: {metadata['uploader']}")
    print(f"Duração: {metadata['duration_string']}")
    print(f"Views: {formatar_views(metadata['view_count'])}")
    print(f"Thumbnail: {metadata['thumbnail']}")
    print(f"URL: {metadata['webpage_url']}")
    
    print("\n" + "=" * 50 + "\n")


def main():
    """
    Função principal da aplicação.
    Orquestra o fluxo: entrada → detecção → limpeza → análise → exibição.
    """
    print("\n🎬 SimpleDL - Analisador de Vídeos\n")
    
    # Recebe a URL do usuário
    url = input("Cole a URL do YouTube: ").strip()
    
    # Valida se a URL não está vazia
    if not url:
        print("❌ Erro: URL não pode estar vazia!")
        return
    
    # Detecta e alerta sobre playlists
    url_limpa, tem_playlist, parametros = detectar_playlist(url)
    
    if tem_playlist:
        if not exibir_aviso_playlist(parametros):
            return
    
    print(f"\n⏳ Analisando: {url_limpa}...")
    
    # Chama a função de análise
    metadata = analisar_video(url_limpa)
    
    # Se conseguiu extrair os metadados, exibe
    if metadata:
        exibir_metadados(metadata)
        print("✅ Análise concluída com sucesso!")
    else:
        print("❌ Não foi possível analisar o vídeo.")


if __name__ == "__main__":
    main()
