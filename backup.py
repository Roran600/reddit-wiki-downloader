#!/usr/bin/env python3
import json
import os
import sys
import time
from pathlib import Path

import requests


CONFIG_FILE = "config.json"
BACKUP_DIR = "backups"
ERROR_LOG_FILE = "errors.log"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def make_request_with_retry(url, headers, max_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 429:
                wait_time = (2**attempt) + 1
                print(f"    [!] Rate limited, čakám {wait_time}s...")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + 1
                print(f"    [!] Chyba: {e}, čakám {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    return None


def get_wiki_pages(subreddit, headers):
    url = f"https://www.reddit.com/r/{subreddit}/wiki/pages/.json"
    try:
        response = make_request_with_retry(url, headers)
        if not response:
            return []
        data = response.json()
        return data["data"]
    except Exception as e:
        print(f"  [!] Chyba pri získavaní zoznamu stránok pre r/{subreddit}: {e}")
        log_error(subreddit, "get_pages", str(e))
        return []


def get_wiki_page_content(subreddit, page, headers):
    url = f"https://www.reddit.com/r/{subreddit}/wiki/{page}.json"
    try:
        response = make_request_with_retry(url, headers)
        if not response:
            return None, None
        data = response.json()

        if "data" in data:
            html_content = data["data"].get("content_html", "")
            md_content = data["data"].get("content_md", "")

            if isinstance(html_content, dict):
                html_content = str(html_content)
            if isinstance(md_content, dict):
                md_content = str(md_content)

            return html_content, md_content
        return None, None
    except Exception as e:
        print(f"  [!] Chyba pri sťahovaní {page}: {e}")
        log_error(subreddit, page, str(e))
        return None, None


def save_content(subreddit, page, html_content, md_content, backup_dir):
    subreddit_dir = Path(backup_dir) / f"r_{subreddit}"
    subreddit_dir.mkdir(parents=True, exist_ok=True)

    safe_page = page.replace("/", "_")

    if page == "index":
        html_file = subreddit_dir / "index.html"
        md_file = subreddit_dir / "index.md"
    else:
        html_file = subreddit_dir / f"{safe_page}.html"
        md_file = subreddit_dir / f"{safe_page}.md"

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    return html_file, md_file


def log_error(subreddit, page, error):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] r/{subreddit} | {page}: {error}\n")


def backup_subreddit(subreddit, config, backup_dir, delay):
    print(f"\n[*] Spracovávam r/{subreddit}...")

    headers = {
        "User-Agent": config.get("user_agent", "RedditWikiBackup/1.0"),
        "Accept": "application/json",
    }

    pages = get_wiki_pages(subreddit, headers)

    if not pages:
        print(f"  [!] Žiadne wiki stránky nenájdené alebo prístup odmietnutý")
        return 0

    print(f"  [*] Nájdených {len(pages)} stránok")

    success_count = 0
    for i, page in enumerate(pages, 1):
        print(f"  [{i}/{len(pages)}] Sťahujem: {page}")

        html_content, md_content = get_wiki_page_content(subreddit, page, headers)

        if html_content and md_content:
            save_content(subreddit, page, html_content, md_content, backup_dir)
            success_count += 1
        else:
            html_content = f"<p>Error: could not fetch page</p>"
            md_content = "Error: could not fetch page"
            save_content(subreddit, page, html_content, md_content, backup_dir)

        if i < len(pages):
            time.sleep(delay)

    print(f"  [✓] Úspešne zálohované: {success_count}/{len(pages)}")
    return success_count


def main():
    print("=" * 50)
    print("  Reddit Wiki Backup")
    print("=" * 50)

    if not os.path.exists(CONFIG_FILE):
        print(f"[-] Konfiguračný súbor {CONFIG_FILE} neexistuje!")
        sys.exit(1)

    config = load_config()

    subreddits = config.get("subreddits", [])
    if not subreddits:
        print("[-] Žiadne subreddity v config.json!")
        sys.exit(1)

    delay = config.get("rate_limit_delay", 2)
    backup_dir = config.get("backup_dir", BACKUP_DIR)

    print(f"\n[*] Zálohujem {len(subreddits)} subredditov")
    print(f"[*] Cieľový adresár: {backup_dir}")
    print(f"[*] Delay medzi požiadavkami: {delay}s")

    Path(backup_dir).mkdir(parents=True, exist_ok=True)

    total_success = 0
    for subreddit in subreddits:
        count = backup_subreddit(subreddit, config, backup_dir, delay)
        total_success += count
        time.sleep(delay)

    print("\n" + "=" * 50)
    print(f"[*] HOTOVO! Zálohovaných stránok: {total_success}")
    print(f"[*] Zálohy sú v: {backup_dir}/")
    print("=" * 50)


if __name__ == "__main__":
    main()
