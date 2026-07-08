#!/usr/bin/env python3
"""
Build or update the FERPA legal corpus from public sources.

Usage:
    python scripts/build_ferpa_corpus.py
    python scripts/build_ferpa_corpus.py --courtlistener-only
    python scripts/build_ferpa_corpus.py --dry-run

Environment:
    COURTLISTENER_API_TOKEN — optional; increases CourtListener API rate limits

Outputs:
    docs/ferpa/ferpa_corpus.json (merged, deduplicated by id)
    docs/ferpa/courtlistener_candidates.json (raw API results for review)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = REPO_ROOT / 'docs' / 'ferpa' / 'ferpa_corpus.json'
CANDIDATES_PATH = REPO_ROOT / 'docs' / 'ferpa' / 'courtlistener_candidates.json'

COURTLISTENER_SEARCH_URL = 'https://www.courtlistener.com/api/rest/v4/search/'
SEARCH_QUERIES = [
    'FERPA',
    '"education records" FERPA',
    '"Family Educational Rights and Privacy Act"',
    'Owasso Falvo',
    'Gonzaga FERPA',
]

SPPO_REFERENCE_URLS = [
    {
        'id': 'sppo-findings-archive',
        'title': 'SPPO Findings Letters Archive',
        'source_url': 'https://studentprivacy.ed.gov/topic/findings-letters',
        'type': 'sppo_archive_index',
    },
    {
        'id': 'sppo-letters-importance',
        'title': 'SPPO Letters of Importance',
        'source_url': 'https://studentprivacy.ed.gov/topic/letters-importance',
        'type': 'sppo_archive_index',
    },
    {
        'id': 'sppo-historical-archive',
        'title': 'SPPO Historical Archive of Issued Letters',
        'source_url': 'https://studentprivacy.ed.gov/historical-archive-issued-letters',
        'type': 'sppo_archive_index',
    },
]


def load_corpus() -> dict:
    if CORPUS_PATH.exists():
        with CORPUS_PATH.open(encoding='utf-8') as f:
            return json.load(f)
    return {
        'metadata': {
            'title': 'FERPA Legal Corpus for PRAMS',
            'version': '1.0.0',
            'entries': [],
        },
        'entries': [],
    }


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        f.write('\n')


def fetch_courtlistener(query: str, token: str | None, page_size: int = 20) -> list[dict]:
    params = {
        'q': query,
        'type': 'o',
        'page_size': str(page_size),
    }
    url = f'{COURTLISTENER_SEARCH_URL}?{urllib.parse.urlencode(params)}'
    headers = {'User-Agent': 'PRAMS-FERPA-Corpus-Builder/1.0'}
    if token:
        headers['Authorization'] = f'Token {token}'

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode('utf-8'))
    except urllib.error.URLError as exc:
        print(f'CourtListener request failed for "{query}": {exc}', file=sys.stderr)
        return []

    results = []
    for item in payload.get('results', []):
        case_name = item.get('caseName') or item.get('caseNameFull') or 'Unknown'
        citation = ''
        if item.get('citation'):
            citation = item['citation'][0] if isinstance(item['citation'], list) else str(item['citation'])
        entry_id = f"cl-{item.get('cluster_id', case_name.lower().replace(' ', '-'))}"
        results.append({
            'id': entry_id,
            'type': 'courtlistener_candidate',
            'citation': citation or case_name,
            'title': case_name,
            'holding': 'Candidate opinion — review and curate holding before relying on it.',
            'education_record_test': [],
            'violation_type': None,
            'source_url': f"https://www.courtlistener.com{item.get('absolute_url', '')}",
            'court': item.get('court', ''),
            'date_filed': item.get('dateFiled', ''),
            'relevance_to_prams': ['courtlistener_auto_discovered'],
            'search_query': query,
            'curated': False,
        })
    return results


def merge_entries(existing: list[dict], new_entries: list[dict]) -> list[dict]:
    by_id = {entry['id']: entry for entry in existing}
    for entry in new_entries:
        entry_id = entry['id']
        if entry_id in by_id:
            if entry.get('curated') is False:
                continue
            by_id[entry_id] = {**by_id[entry_id], **entry}
        else:
            by_id[entry_id] = entry
    return sorted(by_id.values(), key=lambda e: e.get('id', ''))


def build_corpus(*, courtlistener_only: bool = False, dry_run: bool = False) -> dict:
    corpus = load_corpus()
    token = os.environ.get('COURTLISTENER_API_TOKEN', '').strip() or None

    candidates: list[dict] = []
    for query in SEARCH_QUERIES:
        print(f'Querying CourtListener: {query}')
        candidates.extend(fetch_courtlistener(query, token))

    deduped_candidates = merge_entries([], candidates)
    if not dry_run:
        save_json(CANDIDATES_PATH, {
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'count': len(deduped_candidates),
            'entries': deduped_candidates,
        })
        print(f'Wrote {len(deduped_candidates)} candidates to {CANDIDATES_PATH}')

    if courtlistener_only:
        return corpus

    sppo_refs = [
        {
            **ref,
            'holding': 'SPPO archive index — download ZIP/PDF letters for manual curation.',
            'education_record_test': [],
            'violation_type': None,
            'relevance_to_prams': ['enforcement_fact_patterns'],
            'curated': True,
        }
        for ref in SPPO_REFERENCE_URLS
    ]

    corpus['entries'] = merge_entries(corpus.get('entries', []), sppo_refs)
    corpus['metadata']['last_updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    corpus['metadata']['courtlistener_candidates'] = str(CANDIDATES_PATH.relative_to(REPO_ROOT))
    corpus['metadata']['build_script'] = 'scripts/build_ferpa_corpus.py'

    if not dry_run:
        save_json(CORPUS_PATH, corpus)
        print(f'Updated corpus at {CORPUS_PATH} ({len(corpus["entries"])} entries)')
    else:
        print(f'Dry run: would write {len(corpus["entries"])} corpus entries')

    return corpus


def main() -> int:
    parser = argparse.ArgumentParser(description='Build or update FERPA legal corpus')
    parser.add_argument(
        '--courtlistener-only',
        action='store_true',
        help='Only fetch CourtListener candidates; do not merge SPPO refs into corpus',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch and report without writing files',
    )
    args = parser.parse_args()
    build_corpus(courtlistener_only=args.courtlistener_only, dry_run=args.dry_run)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
