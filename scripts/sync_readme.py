#!/usr/bin/env python3
"""Auto-syncs README.md from Medium RSS feed and GitHub merged upstream PRs."""

from __future__ import annotations

from email.utils import parsedate_to_datetime
import html
import json
import os
import pathlib
import re
import urllib.parse
import urllib.request

README_PATH = pathlib.Path(__file__).resolve().parent.parent / "README.md"

CURATED_PRS: dict[str, str] = {
    "ggml-org/llama.cpp#30779": (
        "`llama-server` now visits parent slots before their child slots, so requests "
        "that share a prompt prefix no longer need a third forward pass. Released in `b12188`."
    ),
    "AI-Hypercomputer/maxdiffusion#476": (
        "skips the CUDA-only `nvidia-cuda-cccl` dependency on macOS, where no wheels exist, "
        "so local installs no longer fail on Apple Silicon."
    ),
}

CURATED_POSTS: dict[str, tuple[str, str]] = {
    "https://harkanwalbedi.medium.com/inside-system-1-models-e36c0b30c8a9": (
        "Inside System 1 Models",
        "how a transformer stops writing text and starts providing calibrated decisions.",
    ),
    "https://harkanwalbedi.medium.com/thinking-fast-and-slow-for-production-agents-03e5d0f87cc2": (
        "Thinking, Fast and Slow for Production Agents",
        "pairing open-weights System 1 decision models with an LLM so every model plays to its strengths.",
    ),
}


def _fetch(url: str, headers: dict[str, str] | None = None) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Refusing non-HTTPS URL: {url}")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "harkanwalbedi-profile-sync/1.0", **(headers or {})},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", "ignore")


def _strip_html(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text).replace("\u200a", " ")
    return re.sub(r"\s+", " ", text).strip()


def fetch_prs() -> list[tuple[str, str, str]]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = (
        "https://api.github.com/search/issues?"
        "q=is:pr+is:merged+author:harkanwalbedi+-user:harkanwalbedi"
        "&sort=updated&order=desc&per_page=30"
    )
    data = json.loads(_fetch(url, headers))
    out: list[tuple[str, str, str]] = []
    for item in data.get("items", []):
        closed_at = (item.get("closed_at") or item.get("updated_at") or "")[:10]
        if closed_at < "2026-10-01":
            continue
        repo_path = (item.get("repository_url") or "").split("/repos/")[-1]
        if "/" not in repo_path:
            continue
        num = item["number"]
        key = f"{repo_path}#{num}"
        pr_url = f"https://github.com/{repo_path}/pull/{num}"
        desc = CURATED_PRS.get(key, item.get("title", "").strip())
        out.append((f"{repo_path} #{num}", pr_url, desc))
    return out


def fetch_posts() -> list[tuple[str, str, str]]:
    xml = _fetch("https://medium.com/feed/@harkanwalbedi")
    out: list[tuple[str, str, str]] = []
    for item in re.findall(r"<item>([\s\S]*?)</item>", xml):
        t_m = re.search(r"<title><!\[CDATA\[([\s\S]*?)\]\]></title>", item)
        l_m = re.search(r"<link>([^<\s]+)</link>", item)
        b_m = re.search(r"<content:encoded><!\[CDATA\[([\s\S]*?)\]\]></content:encoded>", item)
        if not (t_m and l_m):
            continue
        link = l_m.group(1).split("?")[0]
        if link in CURATED_POSTS:
            title, summary = CURATED_POSTS[link]
            out.append((title, link, summary))
            continue
        title = _strip_html(t_m.group(1))
        body = b_m.group(1) if b_m else ""
        h4_m = re.search(r"<h4>([\s\S]*?)</h4>", body, re.I)
        summary = _strip_html(h4_m.group(1)) if h4_m else ""
        out.append((title, link, summary))
    return out


def main() -> None:
    prs = fetch_prs()
    posts = fetch_posts()

    lines = [
        "Staff Forward Deployed AI Engineer at Google in Seattle. I work on low-latency LLM inference and production AI agents.",
        "",
        "**Merged upstream**",
        "",
    ]
    for label, url, desc in prs:
        lines.append(f"- **[{label}]({url})**: {desc}")
    lines.extend(["", "**Writing**", ""])
    for title, url, summary in posts:
        suffix = f": {summary}" if summary else ""
        lines.append(f"- [{title}]({url}){suffix}")
    lines.extend(
        [
            "",
            "[Website](https://harkanwalbedi.github.io) · [Medium](https://medium.com/@harkanwalbedi) · [LinkedIn](https://www.linkedin.com/in/harkanwalbedi/)",
            "",
        ]
    )
    README_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated {README_PATH} ({len(prs)} PRs, {len(posts)} posts)")


if __name__ == "__main__":
    main()
