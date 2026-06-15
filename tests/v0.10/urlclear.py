from urllib.parse import urlparse, parse_qs

url = input("URL: ")

parsed = urlparse(url)
video_id = parse_qs(parsed.query).get("v", [""])[0]

url_limpa = f"https://www.youtube.com/watch?v={video_id}"

print(url_limpa)