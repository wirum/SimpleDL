"""
SimpleDL - Downloader de Mídia Minimalista

Ponto de entrada da aplicação. Responsável por:
1. Receber a URL do usuário
2. Chamar a função de análise
3. Exibir os dados formatados no terminal
"""

from core.metadata import analisar_video


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
    Orquestra o fluxo: entrada → limpeza → análise → exibição.
    """
    print("\n🎬 SimpleDL - Analisador de Vídeos\n")
    
    # Recebe a URL do usuário
    url = input("Cole a URL do YouTube: ").strip()
    
    # Valida se a URL não está vazia
    if not url:
        print("❌ Erro: URL não pode estar vazia!")
        return
    
    # Limpa a URL removendo parâmetros extras
    url_limpa = limpar_url(url)
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
