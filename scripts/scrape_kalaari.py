#!/usr/bin/env python3
"""Refresh raw portfolio and team data from kalaari.com.

kalaari.com is a WordPress site. Portfolio companies live at /portfolio/<slug>/ and
team members at /kalaari_team/<slug>/. This script tries the WP REST API first
(fast, structured) and falls back to the sitemap plus HTML parsing.

It writes data/kalaari_site_raw.json. It does NOT overwrite data/kalaari.json:
review the raw pull, merge what changed (new companies, status flips, new team
members), then run scripts/build.py.

Usage:
    python scripts/scrape_kalaari.py            # full pull
    python scripts/scrape_kalaari.py --limit 20 # smoke test

Requires only the standard library. Run it from a network that can reach
kalaari.com; the environment this repo was first built in could not.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Iterable

BASE = "https://kalaari.com"
UA = "kalaari-decoded/1.0 (+https://github.com/modiparv/Kalaari_decoded)"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "kalaari_site_raw.json"


def get(url: str, timeout: int = 30) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"  ! {url}: {e}", file=sys.stderr)
        return None


def strip(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def wp_rest(post_type: str, limit: int | None) -> list[dict] | None:
    """Try the WP REST API for a custom post type. Returns None if unavailable."""
    items: list[dict] = []
    page = 1
    while True:
        url = f"{BASE}/wp-json/wp/v2/{post_type}?per_page=100&page={page}&_embed=1"
        body = get(url)
        if body is None:
            return None if page == 1 else items
        try:
            batch = json.loads(body)
        except json.JSONDecodeError:
            return None
        if not isinstance(batch, list):
            return None
        for p in batch:
            items.append({
                "slug": p.get("slug"),
                "url": p.get("link"),
                "title": strip(p.get("title", {}).get("rendered", "")),
                "excerpt": strip(p.get("excerpt", {}).get("rendered", "")),
                "content": strip(p.get("content", {}).get("rendered", ""))[:2000],
                "date": p.get("date"),
                "modified": p.get("modified"),
                "terms": [t.get("name") for group in p.get("_embedded", {}).get("wp:term", []) for t in group],
                "meta": p.get("meta") or {},
                "acf": p.get("acf") or {},
            })
            if limit and len(items) >= limit:
                return items
        if len(batch) < 100:
            return items
        page += 1
        time.sleep(0.4)


def sitemap_urls(pattern: str) -> list[str]:
    urls: list[str] = []
    for sm in ("sitemap.xml", "sitemap_index.xml", "wp-sitemap.xml"):
        body = get(f"{BASE}/{sm}")
        if not body:
            continue
        for loc in re.findall(r"<loc>(.*?)</loc>", body):
            if loc.endswith(".xml"):
                sub = get(loc)
                if sub:
                    urls += [u for u in re.findall(r"<loc>(.*?)</loc>", sub) if pattern in u]
            elif pattern in loc:
                urls.append(loc)
        if urls:
            break
    return sorted(set(urls))


def parse_page(url: str) -> dict:
    body = get(url) or ""
    title = strip(re.search(r"<title>(.*?)</title>", body, re.S).group(1)) if "<title>" in body else ""
    desc = ""
    m = re.search(r'<meta name="description" content="([^"]*)"', body)
    if m:
        desc = html.unescape(m.group(1))
    og = {k: html.unescape(v) for k, v in re.findall(r'<meta property="og:(\w+)" content="([^"]*)"', body)}
    # Kalaari portfolio pages show label/value pairs such as Sector, Stage, Year, Status.
    pairs = {}
    for lab, val in re.findall(r"<(?:dt|h[3-6]|span)[^>]*>\s*(Sector|Stage|Year|Status|Website|Founded|Location)\s*</(?:dt|h[3-6]|span)>\s*<(?:dd|p|span|a)[^>]*>(.*?)</(?:dd|p|span|a)>", body, re.I | re.S):
        pairs[lab.lower()] = strip(val)
    site = re.search(r'href="(https?://(?!kalaari\.com)[^"]+)"[^>]*>\s*(?:Visit|Website)', body, re.I)
    return {
        "url": url,
        "slug": url.rstrip("/").rsplit("/", 1)[-1],
        "title": title.replace(" – Kalaari Capital", "").strip(),
        "description": desc or og.get("description", ""),
        "fields": pairs,
        "website": site.group(1) if site else "",
        "body_excerpt": strip(body)[:1500],
    }


def crawl(pattern: str, limit: int | None) -> list[dict]:
    urls = sitemap_urls(pattern)
    if limit:
        urls = urls[:limit]
    out = []
    for i, u in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {u}")
        out.append(parse_page(u))
        time.sleep(0.4)
    return out


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=None, help="stop after N items per type (smoke test)")
    args = ap.parse_args(argv)

    result: dict = {"source": BASE, "pulled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "portfolio": [], "team": [], "posts": []}

    print("portfolio: trying WP REST…")
    port = wp_rest("portfolio", args.limit)
    if port is None:
        print("portfolio: REST unavailable, crawling sitemap")
        port = crawl("/portfolio/", args.limit)
    result["portfolio"] = port

    print("team: trying WP REST…")
    team = wp_rest("kalaari_team", args.limit)
    if team is None:
        print("team: REST unavailable, crawling sitemap")
        team = crawl("/kalaari_team/", args.limit)
    result["team"] = team

    print("why-we-invested posts…")
    posts = wp_rest("posts", args.limit) or []
    result["posts"] = [p for p in posts if "why-we-invested" in (p.get("slug") or "") or "why we invested" in (p.get("title") or "").lower()]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT} — portfolio {len(result['portfolio'])}, team {len(result['team'])}, posts {len(result['posts'])}")
    if not result["portfolio"]:
        print("no portfolio pages found: check network access to kalaari.com", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
