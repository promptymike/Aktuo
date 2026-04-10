"""
AKTUO — FB Posts Tagger & Batcher
=================================
Krok 1: Taguje posty (NIE usuwa niczego), tworzy batche do ChatGPT.

Input:  posts_output.json (surowy scrape)
Output:
  - posts_tagged.json        — pełna kopia z tagami (BACKUP + metadane)
  - batches/batch_001.txt    — batche do wklejania w ChatGPT
  - stats.txt                — statystyki

Uruchomienie:
  python 01_tag_and_batch.py
"""

import json
import re
import os
from pathlib import Path

# === CONFIG ===
INPUT_FILE = "posts_output.json"
OUTPUT_DIR = "batches"
TAGGED_FILE = "posts_tagged.json"
STATS_FILE = "stats.txt"
BATCH_SIZE = 200  # postów na batch — optymalnie dla ChatGPT

# === NOISE PATTERNS (tylko oczywisty śmieć) ===
NOISE_PATTERNS = [
    # Szukanie pracy / ogłoszenia
    r"szukam\s+(pracy|księgow|kadrowej|zatrudnienia)",
    r"poszukuj[eę]\s+(pracy|księgow|kadrowej)",
    r"zatrudni[eę]|przyjm[eę]\s+do\s+pracy",
    r"dam\s+prac[eę]",
    r"CV\s+w\s+(wiadomo|priv|komentarz)",
    r"oferta\s+pracy",
    # Reklamy kursów / szkoleń (nie pytania O kursach — te zostawiamy)
    r"zapraszam\s+na\s+(szkolenie|kurs|webinar)",
    r"link\s+do\s+zapisu",
    r"kod\s+rabatowy",
    r"promocja\s+na\s+(kurs|szkolenie)",
    # Życzenia / small talk
    r"wesołych\s+świąt",
    r"dobranoc\s+wszystkim",
    r"miłego\s+(dnia|weekendu|wieczoru)",
    r"wszystkiego\s+najlepszego",
    # Ankiety bez treści
    r"^(tak|nie|a|b|c|1|2|3)\s*$",
]

NOISE_COMPILED = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]


def load_posts(path: str) -> list:
    """Load posts, handle both list and dict formats."""
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, dict) and "posts" in data:
        return data["posts"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unexpected JSON structure: {type(data)}")


def classify_post(post: dict) -> str:
    """
    Classify post as:
      'noise'       — oczywisty śmieć (reklama, szukanie pracy, życzenia)
      'short'       — <15 znaków (prawdopodobnie bezwartościowy, ale zachowany)
      'content'     — merytoryczny post do analizy
    """
    text = post.get("text", "").strip()

    # Brak tekstu
    if not text:
        return "empty"

    # Bardzo krótkie
    if len(text) < 15:
        return "short"

    # Pattern matching na szum
    for pattern in NOISE_COMPILED:
        if pattern.search(text):
            return "noise"

    return "content"


def tag_posts(posts: list) -> list:
    """Tag every post, preserve all data."""
    tagged = []
    for i, post in enumerate(posts):
        tagged_post = {
            **post,
            "original_index": i,
            "tag": classify_post(post),
            "char_count": len(post.get("text", "")),
            "has_comments": bool(post.get("comments")),
            "comment_count": len(post.get("comments", [])),
        }
        tagged.append(tagged_post)
    return tagged


def create_batches(tagged_posts: list, output_dir: str, batch_size: int):
    """Create text batches from content posts for ChatGPT processing."""
    os.makedirs(output_dir, exist_ok=True)

    # Bierzemy CONTENT posts do batchy (ale noise/short też idą do tagged backup)
    content_posts = [p for p in tagged_posts if p["tag"] == "content"]

    batch_num = 0
    for i in range(0, len(content_posts), batch_size):
        batch_num += 1
        batch = content_posts[i : i + batch_size]
        filename = f"batch_{batch_num:03d}.txt"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            for post in batch:
                f.write(f"--- POST #{post['original_index']} ---\n")
                f.write(post.get("text", "").strip() + "\n")
                # Komentarze też — często zawierają odpowiedzi i dodatkowy kontekst
                comments = post.get("comments", [])
                if comments:
                    f.write(f"[KOMENTARZE: {len(comments)}]\n")
                    for c in comments[:5]:  # Max 5 komentarzy na post (oszczędność tokenów)
                        f.write(f"  > {c.strip()}\n")
                f.write("\n")

        print(f"  {filename}: {len(batch)} postów")

    return batch_num, len(content_posts)


def generate_stats(tagged_posts: list) -> str:
    """Generate stats report."""
    total = len(tagged_posts)
    tags = {}
    for p in tagged_posts:
        tag = p["tag"]
        tags[tag] = tags.get(tag, 0) + 1

    with_comments = sum(1 for p in tagged_posts if p["has_comments"])
    total_comments = sum(p["comment_count"] for p in tagged_posts)

    lines = [
        "=" * 50,
        "AKTUO — FB Posts Analysis Stats",
        "=" * 50,
        f"Total posts:          {total}",
        f"",
        "--- By tag ---",
    ]
    for tag in ["content", "noise", "short", "empty"]:
        count = tags.get(tag, 0)
        pct = (count / total * 100) if total > 0 else 0
        lines.append(f"  {tag:10s}: {count:6d} ({pct:.1f}%)")

    lines += [
        f"",
        f"Posts with comments:   {with_comments}",
        f"Total comments:        {total_comments}",
        f"",
        f"Content posts go to ChatGPT batches.",
        f"ALL posts preserved in {TAGGED_FILE}.",
        "=" * 50,
    ]
    return "\n".join(lines)


def main():
    print("Loading posts...")
    posts = load_posts(INPUT_FILE)
    print(f"Loaded {len(posts)} posts.")

    print("Tagging posts...")
    tagged = tag_posts(posts)

    # Save full tagged backup
    print(f"Saving tagged backup → {TAGGED_FILE}")
    with open(TAGGED_FILE, "w", encoding="utf-8") as f:
        json.dump(tagged, f, ensure_ascii=False, indent=2)

    # Create batches
    print(f"Creating batches (size={BATCH_SIZE})...")
    num_batches, num_content = create_batches(tagged, OUTPUT_DIR, BATCH_SIZE)
    print(f"Created {num_batches} batches with {num_content} content posts.")

    # Stats
    stats = generate_stats(tagged)
    print(stats)
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        f.write(stats)

    print(f"\nDone! Next steps:")
    print(f"  1. Open ChatGPT")
    print(f"  2. Paste SYSTEM PROMPT from 02_chatgpt_prompts.md")
    print(f"  3. Paste each batch file from {OUTPUT_DIR}/")
    print(f"  4. Collect JSON outputs → save as batch_001_output.json etc.")
    print(f"  5. Run 03_merge_and_deduplicate.py")


if __name__ == "__main__":
    main()
