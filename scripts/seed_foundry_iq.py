"""Seed Foundry IQ KBs (= Azure AI Search KBs) per profile.yaml.

Per D16: a Foundry IQ KB is an Azure AI Search knowledge base. For each KB
source in the profile, we create a Search index, push parsed docs into it,
register it as a knowledge source, then create the KB referencing all sources.

Run:
  python scripts/seed_foundry_iq.py --plant plant7
  python scripts/seed_foundry_iq.py --enterprise
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

import yaml
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    KnowledgeBase,
    KnowledgeSourceReference,
    SearchableField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexKnowledgeSource,
    SearchIndexKnowledgeSourceParameters,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
    SimpleField,
)
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".yaml", ".yml"}


def _doc_id(path: Path) -> str:
    return hashlib.sha1(str(path).encode("utf-8")).hexdigest()


def _index_name(scope: str, source: str) -> str:
    return f"ks-{scope}-{source}".lower().replace("_", "-")


def _build_index(name: str) -> SearchIndex:
    return SearchIndex(
        name=name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String),
            SimpleField(name="source_path", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="source_name", type=SearchFieldDataType.String, filterable=True),
        ],
        semantic_search=SemanticSearch(
            default_configuration_name="default",
            configurations=[
                SemanticConfiguration(
                    name="default",
                    prioritized_fields=SemanticPrioritizedFields(
                        content_fields=[SemanticField(field_name="content")],
                    ),
                ),
            ],
        ),
    )


def _walk_docs(paths: list[str]) -> list[dict]:
    docs: list[dict] = []
    for rel in paths:
        base = ROOT / rel
        if not base.exists():
            print(f"    WARN: source path '{rel}' does not exist, skipping")
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in TEXT_SUFFIXES:
                docs.append({
                    "id": _doc_id(p),
                    "content": f"[binary file: {p.name}]",
                    "source_path": str(p.relative_to(ROOT)).replace("\\", "/"),
                })
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = p.read_text(encoding="latin-1")
            docs.append({
                "id": _doc_id(p),
                "content": text,
                "source_path": str(p.relative_to(ROOT)).replace("\\", "/"),
            })
    return docs


def _seed(search_endpoint: str, scope: str, sources: dict[str, dict], kb_name: str) -> None:
    cred = DefaultAzureCredential()
    idx_client = SearchIndexClient(endpoint=search_endpoint, credential=cred)

    ks_refs: list[KnowledgeSourceReference] = []
    for source_key, src in sources.items():
        idx_name = _index_name(scope, source_key)

        print(f"  [{source_key}] creating index '{idx_name}'...")
        idx_client.create_or_update_index(_build_index(idx_name))

        docs = _walk_docs(src["paths"])
        for d in docs:
            d["source_name"] = source_key
        print(f"  [{source_key}] uploading {len(docs)} docs...")
        if docs:
            sc = SearchClient(endpoint=search_endpoint, index_name=idx_name, credential=cred)
            BATCH = 100
            for i in range(0, len(docs), BATCH):
                sc.upload_documents(documents=docs[i : i + BATCH])

        print(f"  [{source_key}] creating knowledge source '{idx_name}'...")
        ks = SearchIndexKnowledgeSource(
            name=idx_name,
            description=f"MMC {scope} / {source_key}",
            search_index_parameters=SearchIndexKnowledgeSourceParameters(
                search_index_name=idx_name,
            ),
        )
        idx_client.create_or_update_knowledge_source(ks)
        ks_refs.append(KnowledgeSourceReference(name=idx_name))

    print(f"  creating knowledge base '{kb_name}' with {len(ks_refs)} sources...")
    kb = KnowledgeBase(
        name=kb_name,
        description=f"MMC {scope} grounding KB (auto-seeded)",
        knowledge_sources=ks_refs,
    )
    idx_client.create_or_update_knowledge_base(kb)
    print(f"  done. KB '{kb_name}' is ready.")


def seed_plant(plant_id: str) -> None:
    profile = yaml.safe_load(
        (ROOT / "plants" / plant_id / "profile.yaml").read_text(encoding="utf-8")
    )
    search_ep = os.environ["SEARCH_PLANT_ENDPOINT"]
    kb_name = f"kb-{plant_id}"
    print(f"Seeding plant '{plant_id}' -> {search_ep}")
    _seed(search_ep, plant_id, profile["kb"]["sources"], kb_name)
    print(f"  FOUNDRY_IQ_KB_PLANT7_ID={kb_name}")


def seed_enterprise() -> None:
    search_ep = os.environ["SEARCH_ENTERPRISE_ENDPOINT"]
    nodes = {
        "supply_chain": {"paths": ["enterprise/supply-chain/data"]},
    }
    nodes = {k: v for k, v in nodes.items() if (ROOT / v["paths"][0]).exists()}
    if not nodes:
        print("No enterprise data found yet (Gate B populates remaining nodes).")
        return
    print(f"Seeding enterprise -> {search_ep}")
    _seed(search_ep, "enterprise", nodes, "kb-enterprise")
    print("  FOUNDRY_IQ_KB_ENTERPRISE_ID=kb-enterprise")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plant")
    ap.add_argument("--enterprise", action="store_true")
    args = ap.parse_args()
    if not args.plant and not args.enterprise:
        ap.error("specify --plant <id> or --enterprise")
    if args.plant:
        seed_plant(args.plant)
    if args.enterprise:
        seed_enterprise()
    return 0


if __name__ == "__main__":
    sys.exit(main())
