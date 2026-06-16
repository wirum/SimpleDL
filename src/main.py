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


def exibir_aviso_playlist(url_original, url_limpa, parametros):
    """
    Exibe um aviso formatado sobre detecção de playlist e permite escolha.
    
    Args:
        url_original (str): URL com parâmetros.
        url_limpa (str): URL sem parâmetros.
        parametros (str): String com os parâmetros detectados.
    
    Returns:
        str: URL a ser analisada ('limpa' ou 'original') ou None se cancelar.
    """
    print("\n" + "[!] " * 20)
    print("\n[ATENCAO]")
    print("\nSeu link possui uma playlist embutida:")
    print(f"  {parametros}\n")
    print("Escolha uma opcao:\n")
    print("[1] Analisar APENAS este video (sem playlist)")
    print("[2] Analisar TODA a playlist")
    print("[3] Cancelar\n")
    print("[!] " * 20 + "\n")
    
    while True:
        resposta = input("Digite sua opcao [1/2/3]: ").strip()
        
        if resposta == '1':
            print("\n[OK] Analisando apenas este video...\n")
            return url_limpa
        elif resposta == '2':
            print("\n[OK] Analisando toda a playlist...\n")
            return url_original
        elif resposta == '3':
            print("\n[X] Analise cancelada pelo usuario.\n")
            return None
        else:
            print("[X] Opcao invalida. Digite 1, 2 ou 3.\n")


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
    
    print(f"Titulo: {metadata['title']}")
    print(f"Canal: {metadata['uploader']}")
    print(f"Duracao: {metadata['duration_string']}")
    print(f"Views: {formatar_views(metadata['view_count'])}")
    print(f"Thumbnail: {metadata['thumbnail']}")
    print(f"URL: {metadata['webpage_url']}")
    
    print("\n" + "=" * 50 + "\n")


def main():
    """
    Função principal da aplicação.
    Orquestra o fluxo: entrada → detecção → escolha → análise → exibição.
    """
    print("\n[>>>] SimpleDL - Analisador de Videos\n")
    
    # Recebe a URL do usuário
    url = input("Cole a URL do YouTube: ").strip()
    
    # Valida se a URL não está vazia
    if not url:
        print("[X] Erro: URL nao pode estar vazia!")
        return
    
    # Detecta e alerta sobre playlists
    url_limpa, tem_playlist, parametros = detectar_playlist(url)
    
    if tem_playlist:
        url_final = exibir_aviso_playlist(url, url_limpa, parametros)
        if url_final is None:
            return
    else:
        url_final = url_limpa
    
    print(f"[...] Analisando: {url_final}...")
    
    # Chama a função de análise
    metadata = analisar_video(url_final)
    
    # Se conseguiu extrair os metadados, exibe
    if metadata:
        exibir_metadados(metadata)
        print("[OK] Analise concluida com sucesso!")
    else:
        print("[X] Nao foi possivel analisar o video.")


if __name__ == "__main__":
    main()
