from yt_dlp import YoutubeDL

def baixar_video(url):
    with YoutubeDL({}) as ydl:
        ydl.download([url])