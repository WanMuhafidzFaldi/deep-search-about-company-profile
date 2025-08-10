# deep-search-about-company-profile

Library untuk mencari & scrape profil perusahaan (DuckDuckGo, Google CSE, Bing).

## Install dari Git
```bash
pip install "git+https://github.com/WanMuhafidzFaldi/deep-search-about-company-profile.git"
```

## Pakai di Python :
```python
from company_profile_harvester import CompanyProfileHarvester, fromEnv

# cara 1: via ENV
harvester = fromEnv()

# cara 1: langsung
harvester = CompanyProfileHarvester(
  googleApiKey="YOUR_GOOGLE_API_KEY",
  googleCseId="YOUR_GOOGLE_CSE_ID",
  bingApiKey="YOUR_BING_API_KEY"
)

docs = harvester.searchAndScrape(
  query="Telkom Indonesia",
  engines=["ddg","google","bing"],
  limit=8, lang="id", region="id"
)
print(docs[:1])
```



## ENV Variable:
```bash
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
BING_API_KEY=
```

