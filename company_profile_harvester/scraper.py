from typing import Dict, Optional
import time
import httpx
from bs4 import BeautifulSoup
import trafilatura
from trafilatura.metadata import extract_metadata
import dateparser

def getFavicon(soup: BeautifulSoup, baseUrl: str) -> Optional[str]:
    icon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    if icon and icon.get("href"):
        href = icon["href"]
        if href.startswith("http"):
            return href
        # handle relative
        if href.startswith("//"):
            return "https:" + href
        if href.startswith("/"):
            # crude base
            try:
                from urllib.parse import urlparse, urljoin
                return urljoin(baseUrl, href)
            except:
                return None
        return href
    return None

def extractDateFromSoup(soup: BeautifulSoup) -> Optional[str]:
    candidates = [
        ("meta", {"property":"article:published_time"}),
        ("meta", {"name":"date"}),
        ("meta", {"name":"pubdate"}),
        ("meta", {"name":"DC.date"}),
        ("time", {"datetime": True}),
    ]
    for tag, attrs in candidates:
        el = soup.find(tag, attrs=attrs)
        if el:
            dt = el.get("content") or el.get("datetime")
            if dt:
                try:
                    parsed = dateparser.parse(dt)
                    if parsed:
                        return parsed.date().isoformat()
                except:
                    pass
    return None

def firstParagraph(text: str, minLen: int = 120) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    parts = [p.strip() for p in text.split("\n") if p.strip()]
    for p in parts:
        if len(p) >= minLen:
            return p
    return parts[0] if parts else ""

def naiveSummary(text: str, maxSentences: int = 3) -> str:
    # simple split by period; avoids heavy NLP deps
    text = (text or "").replace("\n", " ").strip()
    if not text:
        return ""
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    return ". ".join(sentences[:maxSentences]) + ("." if sentences else "")

def scrapePage(url: str, hintLang: str = "en", timeoutSeconds: int = 20, requestDelayMs: int = 0) -> Dict:
    if requestDelayMs > 0:
        time.sleep(requestDelayMs / 1000.0)

    # Try Trafilatura first (robust extraction + metadata)
    downloaded = trafilatura.fetch_url(url)
    title = ""
    description = ""
    summary = ""
    dateIso = None
    language = None
    contentType = "text/html"

    if downloaded:
        extracted = trafilatura.extract(downloaded, include_comments=False, include_tables=False, favor_recall=True)
        meta = extract_metadata(downloaded)
        if meta:
            title = getattr(meta, "title", "") or ""
            description = getattr(meta, "description", "") or ""
            language = getattr(meta, "lang", "") or hintLang
            if getattr(meta, "date", None):
                try:
                    parsed = dateparser.parse(meta.date)
                    if parsed:
                        dateIso = parsed.date().isoformat()
                except:
                    pass
        if not description:
            description = firstParagraph(extracted or "")
        summary = naiveSummary(extracted or description)

    # Fallback: fetch raw for favicon & more meta
    favicon = None
    try:
        with httpx.Client(timeout=timeoutSeconds, headers={"User-Agent":"Mozilla/5.0 (compatible; company-profile-harvester/0.1)"}) as client:
            resp = client.get(url)
            if resp.headers.get("content-type","").lower().startswith("application/pdf"):
                contentType = "application/pdf"
            soup = BeautifulSoup(resp.text, "lxml")
            if not title:
                t = soup.find("title")
                title = t.text.strip() if t else title
            if not description:
                md = soup.find("meta", attrs={"name":"description"})
                if md and md.get("content"):
                    description = md["content"].strip()
            if not dateIso:
                dateIso = extractDateFromSoup(soup)
            favicon = getFavicon(soup, baseUrl=str(resp.url))
    except:
        pass

    return {
        "title": title or "",
        "description": description or "",
        "summary": summary or description,
        "date": dateIso,
        "sourceUrl": url,
        "favicon": favicon,
        "language": language or hintLang,
        "contentType": contentType
    }
