import os
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
URL = "https://afisha.yandex.ru/artist/tatu"

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

    if name and ("/concert/" in href or "/event/" in href):
        full_url = (
            href if href.startswith("http")
            else "https://afisha.yandex.ru" + href
        )
        events[full_url] = name

if not events:
    raise RuntimeError("Nie znaleziono wydarzeń na stronie Yandex Afisha")

try:
    with open("seen.json", "r", encoding="utf-8") as f:
        seen = json.load(f)
except FileNotFoundError:
    with open("seen.json", "w", encoding="utf-8") as f:
        json.dump(list(events.keys()), f)
    print("Pierwsze uruchomienie: zapisano istniejące wydarzenia.")
    raise SystemExit(0)

new_events = {
    url: name for url, name in events.items()
    if url not in seen
}

for url, name in new_events.items():
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHANNEL_ID,
            "text": f"🎤 NOWY KONCERT T.A.T.u.!\n\n{name}\n\n{url}"
        },
        timeout=20
    )
    r.raise_for_status()

with open("seen.json", "w", encoding="utf-8") as f:
    json.dump(list(set(seen) | set(events.keys())), f)

print(f"Nowych wydarzeń: {len(new_events)}")
