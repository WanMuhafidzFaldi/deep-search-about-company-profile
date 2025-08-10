import argparse
import json
from .harvester import CompanyProfileHarvester

def main():
    parser = argparse.ArgumentParser(
        prog="company-profile",
        description="Search & scrape company profiles from Google, Bing, and DuckDuckGo."
    )
    parser.add_argument("--query", required=True, help="Nama perusahaan, mis. 'Telkom Indonesia'")
    parser.add_argument("--engine", default="all", choices=["ddg","google","bing","all"], help="Mesin pencari")
    parser.add_argument("--limit", type=int, default=10, help="Jumlah hasil per mesin")
    parser.add_argument("--lang", default="id", help="Kode bahasa (id/en/...)")
    parser.add_argument("--region", default="id", help="Kode region (id/us/...)")

    # API keys init (CLI)
    parser.add_argument("--google-api-key", default=None)
    parser.add_argument("--google-cse-id", default=None)
    parser.add_argument("--bing-api-key", default=None)

    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--request-delay-ms", type=int, default=0)
    parser.add_argument("--out", default=None, help="Path file JSON output")

    args = parser.parse_args()

    engines = ["ddg","google","bing"] if args.engine == "all" else [args.engine]

    harvester = CompanyProfileHarvester(
        googleApiKey=args.google_api_key,
        googleCseId=args.google_cse_id,
        bingApiKey=args.bing_api_key,
        timeoutSeconds=args.timeout_seconds,
        requestDelayMs=args.request_delay_ms
    )

    docs = harvester.searchAndScrape(
        query=args.query,
        engines=engines,
        limit=args.limit,
        lang=args.lang,
        region=args.region
    )

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(docs)} records to {args.out}")
    else:
        print(json.dumps(docs, ensure_ascii=False, indent=2))
