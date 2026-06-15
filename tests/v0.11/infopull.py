from yt_dlp import YoutubeDL

url = input("URL: ")

url = url.split("&")[0]

with YoutubeDL({}) as ydl:
    info = ydl.extract_info(url, download=False)

print(f"Título: {info.get('title')}")
print(f"Canal: {info.get('uploader')}")
print(f"Duração: {info.get('duration_string')}")
print(f"Thumbnail: {info.get('thumbnail')}")