from typing import List, Dict

def uniqueByUrl(items: List[Dict]) -> List[Dict]:
    seen = set()
    out = []
    for it in items:
        url = it.get("url")
        if not url:
            continue
        if url in seen:
            continue
        seen.add(url)
        out.append(it)
    return out

def safeLang(lang: str) -> str:
    lang = (lang or "en").lower()
    if len(lang) > 2:
        return lang[:2]
    return lang

def clampInt(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))
