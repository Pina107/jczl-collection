import requests

resp = requests.get(
    "https://prts.wiki/api.php",
    params={
        "action": "query",
        "list": "allpages",
        "apprefix": "珍",
        "aplimit": 50,
        "format": "json",
    },
    timeout=30,
)
data = resp.json()
for page in data.get("query", {}).get("allpages", []):
    print(page["title"])
