"""
Krok 1: Parser tekstu ustawy z ISAP PDF.
Czyści nagłówki/stopki, łączy złamane linie, rozbija na artykuły.

Użycie:
    python parse_isap.py ustawa_vat.pdf --output articles.json
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def _decode_pdf_text(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1250", "iso-8859-2"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _extract_with_pdftotext(pdf_path: str) -> str:
    """Ekstrahuje tekst z PDF za pomocą systemowego pdftotext."""
    pdftotext_path = shutil.which("pdftotext")
    if not pdftotext_path:
        raise FileNotFoundError("Nie znaleziono systemowego programu 'pdftotext' w PATH.")

    print(f"      Używam systemowego pdftotext: {pdftotext_path}")
    result = subprocess.run(
        [pdftotext_path, pdf_path, "-"],
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = _decode_pdf_text(result.stderr or b"").strip()
        raise RuntimeError(f"pdftotext error: {stderr or 'unknown error'}")
    return _decode_pdf_text(result.stdout)


def _extract_with_python_parser(pdf_path: str) -> str:
    """Fallback: ekstrakcja tekstu z PDF przez bibliotekę Pythona."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "Brak biblioteki 'pypdf'. Zainstaluj zależności: pip install -r requirements.txt"
        ) from exc

    print("      Używam fallback parsera Python: pypdf")
    reader = PdfReader(pdf_path)
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            raise RuntimeError(f"pypdf error na stronie {index}: {exc}") from exc
        pages.append(page_text)

    text = "\n\n".join(pages).strip()
    if not text:
        raise RuntimeError("pypdf nie zwrócił żadnego tekstu z PDF.")
    return text


def extract_text_from_pdf(pdf_path: str) -> str:
    """Ekstrahuje tekst z PDF z fallbackiem dla Windows bez pdftotext."""
    errors: list[str] = []

    try:
        return _extract_with_pdftotext(pdf_path)
    except Exception as exc:
        errors.append(f"pdftotext: {exc}")
        print(f"      pdftotext niedostępny lub nie zadziałał: {exc}")

    try:
        return _extract_with_python_parser(pdf_path)
    except Exception as exc:
        errors.append(f"pypdf: {exc}")
        print(f"      Fallback parser Python nie zadziałał: {exc}")

    joined_errors = "\n      - ".join(errors)
    raise RuntimeError(
        "Nie udało się wyekstrahować tekstu z PDF.\n"
        f"      - {joined_errors}\n"
        "      Zainstaluj 'pdftotext' i dodaj go do PATH albo zainstaluj zależności Pythona: "
        "pip install -r requirements.txt"
    )


def clean_text(raw: str) -> str:
    """Usuwa nagłówki/stopki ISAP i form feedy."""
    lines = raw.split("\n")
    cleaned = []
    skip_patterns = [
        re.compile(r"^©Kancelaria Sejmu"),
        re.compile(r"^\s*s\.\s*\d+/\d+"),
        re.compile(r"^\s*\d{4}-\d{2}-\d{2}\s*$"),
        re.compile(r"^\x0c"),
    ]
    for line in lines:
        if any(p.match(line) for p in skip_patterns):
            continue
        line = line.lstrip("\x0c")
        cleaned.append(line)
    return "\n".join(cleaned)


def rejoin_broken_lines(text: str) -> str:
    """Łączy linie złamane przez PDF word-wrap."""
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"([^\n])\n\n([a-ząćęłńóśźż])", r"\1 \2", text)

    lines = text.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        while (
            i + 1 < len(lines)
            and line
            and not line.endswith((".", ";", ":", ")", "–", "—"))
            and lines[i + 1].strip()
            and not re.match(
                r"^\s*(Art\.|DZIAŁ|Rozdział|\d+[a-z]?\)|\d+[a-z]?\.\s|[a-z]\))",
                lines[i + 1].strip(),
            )
            and (
                lines[i + 1].strip()[0].islower()
                or lines[i + 1].strip().startswith(("w ", "z ", "o ", "i ", "na ", "do ", "od ", "lub "))
            )
        ):
            i += 1
            line = line + " " + lines[i].strip()
        result.append(line)
        i += 1
    return "\n".join(result)


def extract_metadata(text: str) -> dict:
    """Wyciąga metadane ustawy z początku tekstu."""
    meta = {
        "law_name": "",
        "short_name": "",
        "date": "",
        "isap_id": "",
    }

    def normalize_whitespace(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def clean_title(value: str) -> str:
        cleaned = normalize_whitespace(re.sub(r"\d+\)\s*$", "", value))
        if cleaned.lower().startswith("ustawa "):
            return cleaned
        if cleaned.lower().startswith(("ordynacja", "prawo", "kodeks")):
            return cleaned
        return f"Ustawa {cleaned}"

    month_map = {
        "stycznia": "01",
        "lutego": "02",
        "marca": "03",
        "kwietnia": "04",
        "maja": "05",
        "czerwca": "06",
        "lipca": "07",
        "sierpnia": "08",
        "września": "09",
        "października": "10",
        "listopada": "11",
        "grudnia": "12",
    }

    header_match = re.search(
        r"U\s*S\s*T\s*A\s*W\s*A\s*\n\s*z dnia\s+([^\n]+)\n(.+?)(?:\nDZIAŁ|\nRozdział|\nArt\.)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if header_match:
        date_text = normalize_whitespace(header_match.group(1))
        title_text = clean_title(header_match.group(2))
        meta["law_name"] = title_text
        if "ordynacja podatkowa" in title_text.lower():
            meta["short_name"] = "Ordynacja podatkowa"
        elif "podatku od towarów i usług" in title_text.lower():
            meta["short_name"] = "Ustawa o VAT"
        else:
            meta["short_name"] = title_text

        parsed_date = re.match(r"(\d{1,2})\s+([a-ząćęłńóśźż]+)\s+(\d{4})\s*r\.", date_text, re.IGNORECASE)
        if parsed_date:
            day, month_name, year = parsed_date.groups()
            month = month_map.get(month_name.lower())
            if month:
                meta["date"] = f"{year}-{month}-{int(day):02d}"

    m = re.search(r"Dz\.\s*U\.\s*(?:z\s*)?(\d{4})\s*(?:r\.\s*)?(?:Nr\s*\d+\s*)?poz\.\s*(\d+)", text)
    if m:
        meta["isap_id"] = f"Dz.U.{m.group(1)}.{m.group(2)}"

    m2 = re.search(r"t\.j\.\s*\n?\s*Dz\.\s*U\.\s*z\s*(\d{4})\s*r\.\s*\n?\s*poz\.\s*([\d,\s]+)", text[:500])
    if m2:
        meta["consolidated_id"] = f"Dz.U.{m2.group(1)}.{m2.group(2).split(',')[0].strip()}"

    if not meta["law_name"]:
        meta["law_name"] = "Ustawa"
    if not meta["short_name"]:
        meta["short_name"] = meta["law_name"]
    return meta


def parse_articles(text: str) -> list[dict]:
    """Rozbija tekst na artykuły z zachowaniem struktury."""
    article_pattern = re.compile(r"^(Art\.\s*(\d+[a-z]*)\.\s*)(.*)", re.MULTILINE)
    matches = list(article_pattern.finditer(text))

    if not matches:
        raise ValueError("Nie znaleziono artykułów w tekście")

    articles = []
    for i, match in enumerate(matches):
        art_num = match.group(2)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        raw_text = text[start:end].strip()
        context = find_context(text, start)
        paragraphs = parse_paragraphs(raw_text, art_num)

        article = {
            "article_number": art_num,
            "full_id": f"art. {art_num}",
            "division": context.get("division", ""),
            "chapter": context.get("chapter", ""),
            "raw_text": raw_text,
            "paragraphs": paragraphs,
            "is_repealed": "(uchylony)" in raw_text and len(raw_text) < 100,
            "char_count": len(raw_text),
        }
        articles.append(article)

    return articles


def find_context(text: str, position: int) -> dict:
    """Znajduje dział i rozdział dla danej pozycji w tekście."""
    context = {}
    preceding = text[:position]

    divisions = list(re.finditer(r"DZIAŁ\s+([IVXLC]+)\s*\n\s*(.+)", preceding))
    if divisions:
        last = divisions[-1]
        context["division"] = f"Dział {last.group(1)} – {last.group(2).strip()}"

    chapters = list(re.finditer(r"Rozdział\s+(\d+[a-z]*)\s*\n\s*(.+)", preceding))
    if chapters:
        last = chapters[-1]
        context["chapter"] = f"Rozdział {last.group(1)} – {last.group(2).strip()}"

    return context


def parse_paragraphs(article_text: str, art_num: str) -> list[dict]:
    """Parsuje ustępy w artykule."""
    paragraphs = []

    first_line_match = re.match(
        rf"Art\.\s*{re.escape(art_num)}\.\s*(\d+[a-z]?)\.\s*(.*)",
        article_text,
        re.DOTALL,
    )

    if not first_line_match:
        text = re.sub(rf"^Art\.\s*{re.escape(art_num)}\.\s*", "", article_text).strip()
        if text:
            paragraphs.append({"paragraph_number": None, "text": text})
        return paragraphs

    para_pattern = re.compile(r"(?:^Art\.\s*\d+[a-z]*\.\s*)?(\d+[a-z]?)\.\s+", re.MULTILINE)
    para_matches = list(para_pattern.finditer(article_text))

    for i, pm in enumerate(para_matches):
        para_num = pm.group(1)
        start = pm.end()
        end = para_matches[i + 1].start() if i + 1 < len(para_matches) else len(article_text)
        para_text = article_text[start:end].strip()
        paragraphs.append({"paragraph_number": para_num, "text": para_text})

    return paragraphs


def main() -> None:
    if len(sys.argv) < 2:
        print("Użycie: python parse_isap.py <plik.pdf> [--output articles.json]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = "articles.json"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_path = sys.argv[idx + 1]

    print(f"[1/4] Ekstrakcja tekstu z {pdf_path}...")
    raw = extract_text_from_pdf(pdf_path)

    print("[2/4] Czyszczenie nagłówków/stopek ISAP...")
    cleaned = clean_text(raw)

    print("[3/4] Łączenie złamanych linii...")
    rejoined = rejoin_broken_lines(cleaned)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    clean_txt_path = output_path.replace(".json", "_clean.txt")
    Path(clean_txt_path).write_text(rejoined, encoding="utf-8")
    print(f"      Czysty tekst: {clean_txt_path}")

    print("[4/4] Parsowanie artykułów...")
    metadata = extract_metadata(raw)
    articles = parse_articles(rejoined)

    total = len(articles)
    repealed = sum(1 for a in articles if a["is_repealed"])
    active = total - repealed

    output = {
        "metadata": metadata,
        "stats": {
            "total_articles": total,
            "active_articles": active,
            "repealed_articles": repealed,
        },
        "articles": articles,
    }

    Path(output_path).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nGotowe! {active} aktywnych artykułów (+ {repealed} uchylonych)")
    print(f"Zapisano: {output_path}")


if __name__ == "__main__":
    main()
