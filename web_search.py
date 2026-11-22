"""Optional public-web search. Internet availability and site markup may vary."""
import re
import urllib.parse
import urllib.request
from html import unescape

def search(query, limit=5):
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=12) as res:
            html = res.read().decode("utf-8", errors="ignore")
        pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)".*?>(.*?)</a>'
        found = re.findall(pattern, html, flags=re.S)
        results = []
        for href, title in found[:limit]:
            title = unescape(re.sub(r"<.*?>", "", title)).strip()
            results.append({"title": title, "url": unescape(href)})
        return results
    except Exception as e:
        return [{"error": f"جست‌وجوی وب ناموفق بود: {e}"}]
