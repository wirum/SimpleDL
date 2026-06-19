from core.url import limpar_url
from core.metadata import analisar_video
from core.downloader import baixar_video

url = input("URL: ")

url = limpar_url(url)

metadata = analisar_video(url)

baixar_video(url)