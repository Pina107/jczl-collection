import requests

resp = requests.get(
    "https://prts.wiki/api.php",
    params={"action": "opensearch", "search": "珍藏陈列室", "limit": 20, "format": "json"},
    timeout=30,
)
print(resp.json())
