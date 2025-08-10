from .harvester import CompanyProfileHarvester  # pastikan class ini ada di harvester.py

__all__ = ["CompanyProfileHarvester", "fromEnv", "__version__"]
__version__ = "0.1.0"


def fromEnv(
    *,
    googleApiKey=None,
    googleCseId=None,
    bingApiKey=None,
    timeoutSeconds: int = 20,
    requestDelayMs: int = 0
) -> CompanyProfileHarvester:
    import os

    googleApiKey = googleApiKey or os.getenv("GOOGLE_API_KEY")
    googleCseId = googleCseId or os.getenv("GOOGLE_CSE_ID")
    bingApiKey = bingApiKey or os.getenv("BING_API_KEY")

    return CompanyProfileHarvester(
        googleApiKey=googleApiKey,
        googleCseId=googleCseId,
        bingApiKey=bingApiKey,
        timeoutSeconds=timeoutSeconds,
        requestDelayMs=requestDelayMs,
    )