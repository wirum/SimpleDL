from core.url import limpar_url
from core.metadata import analisar_video
from core.downloader import baixar_video


def main():
    url_bruta = input("URL: ").strip()

    try:
        url = limpar_url(url_bruta)
    except ValueError as e:
        print(f"❌ {e}")
        return

    print("\n🔍 Buscando informações do vídeo...")
    metadata = analisar_video(url)

    if metadata is None:
        print("❌ Não foi possível obter informações do vídeo. Abortando.")
        return

    print(f"\n🎬 {metadata['title']}")
    print(f"📺 {metadata['uploader']}  •  {metadata['duration_string']}")
    print()

    baixar_video(url)


if __name__ == "__main__":
    main()