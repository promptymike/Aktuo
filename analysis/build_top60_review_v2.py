"""Generate ``analysis/top60_clusters_for_review_v2.md`` — revision of
the review doc after Paweł's first-pass decisions:

* **Filter** (v2 — "wynagrodz" keyword removed, it was eating the core of
  kadry ops): exclude ``topic_area == "inne"`` OR label hits one of the
  narrow social/off-topic keywords listed in ``EXCLUDE_PATTERNS``.
* **Force overrides** apply Paweł's explicit decisions:
  - ``FORCE_INCLUDE_IDS`` — 16 clusters previously filtered out by the
    too-aggressive "wynagrodz" rule, restored now.
  - ``FORCE_EXCLUDE_IDS`` — 10 clusters to keep out regardless of filter
    (compliance/social/niche).
* **Merges** — three groups of clusters that are semantically one
  workflow. Merged into synthetic clusters with weighted avg_comments,
  summed size, concatenated keywords/centroids, custom label.
* Scoring + top 60 + markdown identical to v1.

Not committed — still a review artifact.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLUSTERS = REPO / "data" / "corpus" / "fb_groups" / "clusters.jsonl"
CORPUS = REPO / "data" / "corpus" / "fb_groups" / "fb_corpus.jsonl"
OUT = REPO / "analysis" / "top60_clusters_for_review_v2.md"

CORE_TOPICS = {"KSeF", "KPiR", "VAT", "ZUS", "PIT", "CIT", "JPK", "kadry", "rachunkowość"}

# v2 filter: narrow social/off-topic keywords. "wynagrodz" removed per
# Paweł — it was catching the bulk of legitimate payroll workflows.
EXCLUDE_PATTERNS = [
    ("wypalenie", "temat zawodowy/emocjonalny"),
    ("kariera", "kariera — zawodowy"),
    ("szukanie pracy", "szukanie pracy — zawodowy"),
    ("poszukiwanie księgowych", "poszukiwanie księgowych/biur — zawodowy"),
    ("rekrut", "rekrutacja — zawodowy"),
    ("zmiana pracy", "zmiana pracy — zawodowy"),
    ("odejście", "odejście z pracy — zawodowy"),
    ("toksyczn", "relacje toksyczne — społeczny"),
    ("relacje z klientami", "relacje z klientami — społeczny"),
    ("widełki", "widełki wynagrodzeń — społeczny/dyskursywny"),
    ("wycena usług", "wycena usług księgowych — biznes, nie workflow"),
    ("kursy księgowości na start", "nauka zawodu, nie workflow"),
]

# Paweł's manual overrides after v1 review.
FORCE_INCLUDE_IDS: set[int] = {10, 71, 135, 127, 134, 3, 130, 1, 74, 68, 9, 119, 54, 105, 131, 22}
FORCE_EXCLUDE_IDS: set[int] = {133, 137, 116, 136, 115, 0, 28, 11, 129, 72}

# Merges: list of (set of cluster_ids, merged_label, merged_topic_area).
MERGES: list[tuple[set[int], str, str]] = [
    (
        {121, 120},
        "KSeF: moment podatkowy, data wystawienia, korekty",
        "KSeF",
    ),
    (
        {102, 101},
        "Macierzyństwo: wnioski urlopowe, zasiłki, składki ZUS",
        "kadry",
    ),
    (
        {33, 95, 86},
        "Roczne rozliczenia PIT: PIT-4R, PIT-11, korekty i przekazanie",
        "PIT",
    ),
]


def load_corpus_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    with CORPUS.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            index[row["id"]] = {
                "text": row.get("text", ""),
                "group_name": row.get("group_name", ""),
                "comments_count": int(row.get("comments_count", 0)),
            }
    return index


def score_cluster(c: dict) -> float:
    size = c["size"]
    avg = c["avg_comments_count"]
    bonus = 100.0 if c["topic_area"] in CORE_TOPICS else 0.0
    return size * 0.4 + avg * 50 * 0.4 + bonus * 0.2


def classify_exclusion_v2(cluster: dict) -> str | None:
    if cluster["topic_area"] == "inne":
        return "topic_area=inne (nie pasuje do żadnego głównego obszaru księgowego)"
    label_lc = cluster["label"].lower()
    for pattern, reason in EXCLUDE_PATTERNS:
        if pattern in label_lc:
            return f"label zawiera '{pattern}' — {reason}"
    return None


def recommend(cluster: dict) -> str:
    size = cluster["size"]
    avg = cluster["avg_comments_count"]
    core = cluster["topic_area"] in CORE_TOPICS
    if size >= 30 and avg >= 1.5 and core:
        return "RECOMMENDED WORKFLOW"
    if size >= 20 and (avg >= 1.2 or core):
        return "CONSIDER"
    return "LOW PRIORITY"


def truncate(text: str, limit: int = 200) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


def dedupe_preserve_order(seq: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def merge_clusters(members: list[dict], new_label: str, new_topic: str) -> dict:
    """Build a synthetic merged cluster from ``members``."""

    total_size = sum(m["size"] for m in members)
    # Weighted averages by size.
    avg_comments = (
        sum(m["avg_comments_count"] * m["size"] for m in members) / total_size
        if total_size
        else 0.0
    )
    many_ratio = (
        sum(m.get("has_many_comments_ratio", 0.0) * m["size"] for m in members)
        / total_size
        if total_size
        else 0.0
    )

    keywords: list[str] = []
    bigrams: list[str] = []
    centroids: list[str] = []
    samples: list[str] = []
    descriptions: list[str] = []
    member_ids = sorted(m["cluster_id"] for m in members)

    for m in members:
        keywords.extend(m.get("top_keywords") or [])
        bigrams.extend(m.get("top_bigrams") or [])
        centroids.extend(m.get("centroid_post_ids") or [])
        samples.extend(m.get("sample_post_ids") or [])
        desc = (m.get("description") or "").strip()
        if desc:
            descriptions.append(f"({m['cluster_id']}) {desc}")

    return {
        "cluster_id": f"merge[{'+'.join(str(i) for i in member_ids)}]",
        "label": new_label,
        "description": " \n\n".join(descriptions),
        "topic_area": new_topic,
        "size": total_size,
        "avg_comments_count": avg_comments,
        "has_many_comments_ratio": many_ratio,
        "top_keywords": dedupe_preserve_order(keywords)[:15],
        "top_bigrams": dedupe_preserve_order(bigrams)[:10],
        "centroid_post_ids": dedupe_preserve_order(centroids)[:10],
        "sample_post_ids": dedupe_preserve_order(samples)[:20],
        "_merged_from": member_ids,
    }


def format_cluster_section(rank: int, c: dict, corpus_idx: dict[str, dict]) -> str:
    lines: list[str] = []
    score = score_cluster(c)
    rec = recommend(c)
    merged_tag = ""
    if "_merged_from" in c:
        merged_tag = f" · MERGED ({', '.join(str(i) for i in c['_merged_from'])})"
    lines.append(f"## {rank}. {c['label']}{merged_tag}")
    lines.append("")
    lines.append(
        f"- **rank**: {rank}  **score**: {score:.1f}  **cluster_id**: `{c['cluster_id']}`"
    )
    lines.append(f"- **topic_area**: `{c['topic_area']}`")
    lines.append(f"- **size**: {c['size']} postów")
    lines.append(f"- **avg_comments**: {c['avg_comments_count']:.2f}")
    lines.append(f"- **has_many_comments_ratio**: {c.get('has_many_comments_ratio', 0.0):.2f}")
    lines.append(f"- **rekomendacja heurystyczna**: **{rec}**")
    lines.append("- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`")
    lines.append("")
    desc = (c.get("description") or "").strip()
    if desc:
        lines.append(f"> {desc}")
        lines.append("")
    kws = c.get("top_keywords") or []
    bgs = c.get("top_bigrams") or []
    if kws or bgs:
        lines.append(
            f"**Keywords**: {', '.join(kws[:10]) if kws else '(brak)'}  "
            f"**Bigramy**: {', '.join(bgs[:5]) if bgs else '(brak)'}"
        )
        lines.append("")
    lines.append("**Przykładowe posty (z centroidu):**")
    lines.append("")
    for i, pid in enumerate(c.get("centroid_post_ids", [])[:3], start=1):
        info = corpus_idx.get(pid)
        if not info:
            lines.append(f"{i}. `{pid}` — (post nie znaleziony w korpusie)")
            lines.append("")
            continue
        group = info.get("group_name", "")
        lines.append(
            f"{i}. `{pid}` · {group} · {info.get('comments_count', 0)} komentarzy"
        )
        excerpt = truncate(info["text"])
        lines.append(f"   > {excerpt}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    with CLUSTERS.open("r", encoding="utf-8") as handle:
        clusters = [json.loads(line) for line in handle if line.strip()]

    corpus_idx = load_corpus_index()

    # Step 1: partition via v2 filter + force overrides.
    kept: list[dict] = []
    excluded: list[tuple[dict, str]] = []
    for c in clusters:
        cid = c["cluster_id"]
        if cid in FORCE_EXCLUDE_IDS:
            excluded.append((c, "decyzja Pawła: out (przegląd v1)"))
            continue
        if cid in FORCE_INCLUDE_IDS:
            kept.append(c)
            continue
        reason = classify_exclusion_v2(c)
        if reason is None:
            kept.append(c)
        else:
            excluded.append((c, reason))

    # Step 2: apply merges. Remove merge members from kept, add merged synths.
    all_merge_ids: set[int] = set()
    for ids, _, _ in MERGES:
        all_merge_ids.update(ids)

    kept_by_id: dict[int, dict] = {c["cluster_id"]: c for c in kept}
    kept_after_merge: list[dict] = [
        c for c in kept if c["cluster_id"] not in all_merge_ids
    ]
    merged_records: list[dict] = []
    for ids, label, topic in MERGES:
        members = [kept_by_id[i] for i in ids if i in kept_by_id]
        if len(members) != len(ids):
            missing = ids - {m["cluster_id"] for m in members}
            raise RuntimeError(
                f"merge target(s) not in kept set: {missing} "
                f"(jeśli były FORCE_EXCLUDE to popraw konfigurację)"
            )
        merged_records.append(merge_clusters(members, label, topic))

    final_clusters = kept_after_merge + merged_records
    final_clusters.sort(key=score_cluster, reverse=True)
    top = final_clusters[:60]

    rec_counts: dict[str, int] = {"RECOMMENDED WORKFLOW": 0, "CONSIDER": 0, "LOW PRIORITY": 0}
    for c in top:
        rec_counts[recommend(c)] += 1

    md: list[str] = []
    md.append("# Top klastrów do review — v2 (po decyzjach Pawła)")
    md.append("")
    md.append(
        f"**Zmiany względem v1:** przywrócono **{len(FORCE_INCLUDE_IDS)}** klastrów "
        f"(operacyjne kadrowo-płacowe, v1 wycięła je zbyt agresywnym keywordem 'wynagrodz'), "
        f"utrzymano wykluczenie **{len(FORCE_EXCLUDE_IDS)}** (faktycznie społeczne/niszowe), "
        f"oraz zmergowano **{len(MERGES)}** grupy klastrów w jeden workflow każda."
    )
    md.append("")
    md.append(
        f"Z **{len(clusters)}** oryginalnych klastrów: **{len(excluded)}** wykluczono "
        f"(filtr + decyzje), **{sum(len(ids) for ids, _, _ in MERGES)}** połączono w "
        f"**{len(MERGES)}** merge'y, finalnie **{len(final_clusters)}** klastrów "
        f"w rankingu — pokazano top **{len(top)}**:"
    )
    md.append("")
    md.append(
        "```\n"
        "score = size * 0.4 + avg_comments * 50 * 0.4 + bonus * 0.2\n"
        "bonus = 100 dla topic_area ∈ {KSeF, KPiR, VAT, ZUS, PIT, CIT, JPK, kadry, rachunkowość}\n"
        "dla merge'ów: size = suma; avg_comments = średnia ważona size\n"
        "```"
    )
    md.append("")
    md.append("**Rekomendacje heurystyczne (do weryfikacji przez Pawła):**")
    md.append(f"- RECOMMENDED WORKFLOW: **{rec_counts['RECOMMENDED WORKFLOW']}** klastrów")
    md.append(f"- CONSIDER: **{rec_counts['CONSIDER']}** klastrów")
    md.append(f"- LOW PRIORITY: **{rec_counts['LOW PRIORITY']}** klastrów")
    md.append("")
    md.append(
        "**Jak używać:** przejrzyj każdą sekcję, przeczytaj 3 przykładowe posty, "
        "i wypełnij `decyzja Pawła` jedną z:"
    )
    md.append("- `WORKFLOW` — klaster wchodzi jako kandydat workflow rekordu w Zadaniu 3")
    md.append("- `SKIP` — odpada")
    md.append("- `MERGE_WITH_#X` — powinien być połączony z klastrem #X")
    md.append("")

    md.append("## Zastosowane merge'y")
    md.append("")
    md.append("| Merge | Cluster_ids | Nowy label | Topic | Size (suma) | AvgComm (ważona) |")
    md.append("|---|---|---|---|---:|---:|")
    for i, rec in enumerate(merged_records, start=1):
        ids_str = " + ".join(str(x) for x in rec["_merged_from"])
        md.append(
            f"| M{i} | `{ids_str}` | {rec['label']} | {rec['topic_area']} | "
            f"{rec['size']} | {rec['avg_comments_count']:.2f} |"
        )
    md.append("")

    md.append("## Tabela zbiorcza (top 60)")
    md.append("")
    md.append("| # | Score | Size | AvgComm | Topic | Rekomendacja | Label | cluster_id | Decyzja |")
    md.append("|---:|---:|---:|---:|---|---|---|---|---|")
    for rank, c in enumerate(top, start=1):
        rec = recommend(c)
        score = score_cluster(c)
        label = c["label"].replace("|", "/")
        merged_marker = " ⟵M" if "_merged_from" in c else ""
        md.append(
            f"| {rank}{merged_marker} | {score:.1f} | {c['size']} | "
            f"{c['avg_comments_count']:.2f} | {c['topic_area']} | {rec} | "
            f"{label} | `{c['cluster_id']}` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |"
        )
    md.append("")

    md.append("---")
    md.append("")
    md.append("## Szczegółowe karty klastrów (top 60)")
    md.append("")
    for rank, c in enumerate(top, start=1):
        md.append(format_cluster_section(rank, c, corpus_idx))
        md.append("---")
        md.append("")

    md.append("## Klastry wykluczone (v2)")
    md.append("")
    md.append(
        f"Pełna lista **{len(excluded)}** klastrów odrzuconych — dla audytu."
    )
    md.append("")
    md.append("| cluster_id | Topic | Size | AvgComm | Label | Powód wykluczenia |")
    md.append("|---:|---|---:|---:|---|---|")
    excluded.sort(key=lambda x: x[0]["size"], reverse=True)
    for cluster, reason in excluded:
        label = cluster["label"].replace("|", "/")
        md.append(
            f"| `{cluster['cluster_id']}` | {cluster['topic_area']} | "
            f"{cluster['size']} | {cluster['avg_comments_count']:.2f} | "
            f"{label} | {reason} |"
        )
    md.append("")

    OUT.write_text("\n".join(md), encoding="utf-8")
    print(
        f"Wrote {OUT} ({len(top)} top, {len(final_clusters)} total in ranking, "
        f"{len(excluded)} excluded, {len(merged_records)} merges)"
    )
    print(
        f"Recommendations: WORKFLOW={rec_counts['RECOMMENDED WORKFLOW']}  "
        f"CONSIDER={rec_counts['CONSIDER']}  LOW={rec_counts['LOW PRIORITY']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
