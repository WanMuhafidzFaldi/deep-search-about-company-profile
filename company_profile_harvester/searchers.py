from typing import List, Dict, Optional
import httpx
from duckduckgo_search import DDGS

def buildResult(source: str, title: str, url: str, snippet: Optional[str]) -> Dict:
    return {
        "source": source,
        "title": title or "",
        "url": url,
        "snippet": snippet or ""
    }

class DuckDuckGoSearcher:
    def __init__(self, timeoutSeconds: int = 20):
        self.timeoutSeconds = timeoutSeconds

    def searchCompanies(self, query: str, limit: int = 10, lang: str = "en", region: str = "us") -> List[Dict]:
        # DDG tidak butuh API key
        results: List[Dict] = []
        with DDGS(timeout=self.timeoutSeconds) as ddg:
            for r in ddg.text(query, region=region, safesearch="Off", timelimit=None, max_results=limit):
                results.append(buildResult("ddg", r.get("title",""), r.get("href",""), r.get("body","")))
        return results

class GoogleSearcher:
    def __init__(self, apiKey: Optional[str], cseId: Optional[str], timeoutSeconds: int = 20):
        self.apiKey = apiKey
        self.cseId = cseId
        self.timeoutSeconds = timeoutSeconds

    def searchCompanies(self, query: str, limit: int = 10, lang: str = "en", region: str = "us") -> List[Dict]:
        if not self.apiKey or not self.cseId:
            return []
        # Google Custom Search JSON API
        params = {
            "key": self.apiKey,
            "cx": self.cseId,
            "q": query,
            "gl": region.lower(),
            "lr": f"lang_{lang.lower()}",
            "num": min(10, max(1, limit))  # Google API per page
        }
        results: List[Dict] = []
        with httpx.Client(timeout=self.timeoutSeconds) as client:
            resp = client.get("https://www.googleapis.com/customsearch/v1", params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            items = data.get("items", [])
            for it in items:
                results.append(buildResult("google", it.get("title",""), it.get("link",""), it.get("snippet","")))
        return results

class BingSearcher:
    def __init__(self, apiKey: Optional[str], timeoutSeconds: int = 20):
        self.apiKey = apiKey
        self.timeoutSeconds = timeoutSeconds

    def searchCompanies(self, query: str, limit: int = 10, lang: str = "en", region: str = "us") -> List[Dict]:
        if not self.apiKey:
            return []
        headers = {"Ocp-Apim-Subscription-Key": self.apiKey}
        params = {
            "q": query,
            "count": min(50, max(1, limit)),
            "mkt": f"{lang}-{region}".lower()
        }
        results: List[Dict] = []
        with httpx.Client(timeout=self.timeoutSeconds, headers=headers) as client:
            resp = client.get("https://api.bing.microsoft.com/v7.0/search", params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            webPages = data.get("webPages", {}).get("value", [])
            for it in webPages:
                results.append(buildResult("bing", it.get("name",""), it.get("url",""), it.get("snippet","")))
        return results
