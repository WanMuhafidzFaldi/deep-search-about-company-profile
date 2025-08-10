from typing import List, Dict, Optional
from .searchers import DuckDuckGoSearcher, GoogleSearcher, BingSearcher
from .scraper import scrapePage
from .utils import uniqueByUrl, safeLang, clampInt
from tqdm import tqdm

class CompanyProfileHarvester:
    def __init__(
        self,
        googleApiKey: Optional[str] = None,
        googleCseId: Optional[str] = None,
        bingApiKey: Optional[str] = None,
        timeoutSeconds: int = 20,
        requestDelayMs: int = 0
    ):
        self.googleApiKey = googleApiKey
        self.googleCseId = googleCseId
        self.bingApiKey = bingApiKey
        self.timeoutSeconds = timeoutSeconds
        self.requestDelayMs = requestDelayMs

        self.ddg = DuckDuckGoSearcher(timeoutSeconds=timeoutSeconds)
        self.google = GoogleSearcher(apiKey=googleApiKey, cseId=googleCseId, timeoutSeconds=timeoutSeconds)
        self.bing = BingSearcher(apiKey=bingApiKey, timeoutSeconds=timeoutSeconds)

    def searchOnly(
        self,
        query: str,
        engines: List[str],
        limit: int = 10,
        lang: str = "en",
        region: str = "us"
    ) -> List[Dict]:
        engines = [e.lower() for e in engines] if engines else ["ddg"]
        limit = clampInt(limit, 1, 50)
        lang = safeLang(lang)
        region = region.lower()

        results: List[Dict] = []

        if "ddg" in engines:
            results += self.ddg.searchCompanies(query=query, limit=limit, lang=lang, region=region)
        if "google" in engines:
            results += self.google.searchCompanies(query=query, limit=limit, lang=lang, region=region)
        if "bing" in engines:
            results += self.bing.searchCompanies(query=query, limit=limit, lang=lang, region=region)

        results = uniqueByUrl(results)
        return results[:limit * max(1, len(engines))]

    def searchAndScrape(
        self,
        query: str,
        engines: List[str],
        limit: int = 10,
        lang: str = "en",
        region: str = "us",
        maxConcurrency: int = 4
    ) -> List[Dict]:
        searchResults = self.searchOnly(query=query, engines=engines, limit=limit, lang=lang, region=region)
        finalDocs: List[Dict] = []

        # Simple sequential scrape (reliable; lower complexity). Can be parallelized if needed.
        for item in tqdm(searchResults, desc="Scraping", unit="page"):
            url = item.get("url")
            try:
                pageData = scrapePage(
                    url=url,
                    hintLang=lang,
                    timeoutSeconds=self.timeoutSeconds,
                    requestDelayMs=self.requestDelayMs
                )
                merged = {**item, **pageData}
                finalDocs.append(merged)
            except Exception as ex:
                # Graceful skip
                continue

        return finalDocs
