from .fetch import crawl
from .config import SEED_SOURCES
import argparse

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-list", default=None)
    ap.add_argument("--max-per-site", type=int, default=50)
    args = ap.parse_args()
    seeds = []
    if args.source_list:
        seeds = SEED_SOURCES.get(args.source_list, [])
    else:
        for v in SEED_SOURCES.values():
            seeds.extend(v)
    crawl(seeds, max_per_site=args.max_per_site)
    print("Fetch complete.")
