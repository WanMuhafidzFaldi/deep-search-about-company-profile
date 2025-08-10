from company_profile_harvester import CompanyProfileHarvester

harvester = CompanyProfileHarvester(
    googleApiKey="YOUR_GOOGLE_API_KEY",
    googleCseId="YOUR_GOOGLE_CSE_ID",
    bingApiKey="YOUR_BING_API_KEY"
)

docs = harvester.searchAndScrape(
    query="Telkom Indonesia",
    engines=["ddg"],
    limit=8,
    lang="id",
    region="id"
)

print(docs)
