import os
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

URL = "https://afisha.yandex.ru/artist/tatu"

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHANNEL_ID,
            "text": text,
            "disable_web_page_preview": False
        },
        timeout=20
    ).raise_for_status()

response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

events = {}
for link in soup.select("a[href]"):
    href = link.get("href", "")
    name = link.get_text(" ", strip=True)

    if "/concert/" in href and name:
        full_url = (
            href if href.startswith("http")
            else "https://afisha.yandex.ru" + href
        )
        events[full_url] = name

if not events:
    print("Nie znaleziono wydarzeń. Strona może ładować dane dynamicznie.")
    raise SystemExit(0)

try:
    with open("seen.json", "r", encoding="utf-8") as file:
        seen = json.load(file)
except FileNotFoundError:
    seen = []

new_events = {
    url: name for url, name in events.items()
    if url not in seen
}

for url, name in new_events.items():
    send_message(f"🎤 NOWY KONCERT T.A.T.u.!\n\n{name}\n\n{url}")

with open("seen.json", "w", encoding="utf-8") as file:
    json.dump(list(set(seen) | set(events)), file, ensure_ascii=False)

print(f"Znaleziono {len(events)} wydarzeń, nowych: {len(new_events)}")
