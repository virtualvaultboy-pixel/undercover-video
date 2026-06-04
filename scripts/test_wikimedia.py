"""Test rapide : peut-on tirer des videos courtes utilisables sur Wikimedia Commons ?"""
import urllib.request
import urllib.parse
import json

API = "https://commons.wikimedia.org/w/api.php"

def search(query, limit=5):
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": f"filetype:video {query}",
        "srnamespace": "6",  # File namespace
        "srlimit": str(limit),
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "UndercoverApp/1.0 (test)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get_file_info(title):
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|mediatype|duration",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "UndercoverApp/1.0 (test)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


for q in ["cat", "dog", "coffee pouring", "burger", "tennis"]:
    print(f"\n=== {q!r} ===")
    res = search(q, 3)
    for hit in res.get("query", {}).get("search", []):
        title = hit["title"]
        info = get_file_info(title)
        pages = info.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            ii = page.get("imageinfo", [{}])[0]
            mime = ii.get("mime", "?")
            duration = ii.get("duration", 0)
            size = ii.get("size", 0) // 1024
            url = ii.get("url", "")
            print(f"  - {title}")
            print(f"    {mime}  {duration:.1f}s  {size}KB")
            print(f"    {url}")
