from yt_dlp import YoutubeDL

url = input("URL: ")

with YoutubeDL({}) as ydl:
    info = ydl.extract_info(url, download=False)

print(info["title"])