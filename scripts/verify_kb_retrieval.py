"""Quick smoke test that Plant 7 KB returns grounded hits (Task 11).

Runs two semantic queries against the `kb-plant7` Search indexes and prints
the top hits with source paths. Acceptable result: at least one hit per
query cites a file under `plants/plant7/kb/`.
"""
from __future__ import annotations

import os
import sys

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

load_dotenv()

QUERIES = [
    ("ks-plant7-ehs", "What LOTO procedure applies to L1-PRS-001?"),
    ("ks-plant7-maintenance", "What is the PM schedule for the brake caliper line?"),
    ("ks-plant7-quality-ops", "What are common quality defects on Line 1?"),
]


def main() -> int:
    endpoint = os.environ["SEARCH_PLANT_ENDPOINT"]
    cred = DefaultAzureCredential()
    failed = 0
    for index, q in QUERIES:
        print(f"\n[{index}] {q}")
        sc = SearchClient(endpoint=endpoint, index_name=index, credential=cred)
        results = list(sc.search(search_text=q, top=3, query_type="semantic",
                                  semantic_configuration_name="default"))
        if not results:
            print("  NO HITS")
            failed += 1
            continue
        for r in results:
            score = r.get("@search.reranker_score") or r["@search.score"]
            print(f"  {score:.3f}  {r.get('source_path')}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
