from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

KB_FILES = [
    Path("data/seeds/law_knowledge.json"),
    Path("data/seeds/law_knowledge_additions.json"),
    Path("data/seeds/law_knowledge_curated_additions.json"),
]
FIELDS = ["law_name", "category", "content", "question_intent", "source"]
REPORT_PATH = Path("analysis/utf8_fix_report.json")
BACKUP_SUFFIX = ".backup_pre_utf8_fix"
CORRUPTION_PATTERN = r"\w+\?\w+"
OUTER_PUNCT = '.,;:!()[]{}"„”«»'

# Regex-reported corruption fragments that we verify and track in the report.
CORRUPTION_MAP = {
    "Dow?d": "Dow\u00f3d",
    "Je?eli": "Je\u017celi",
    "Jednocze?nie": "Jednocze\u015bnie",
    "Odpis?w": "Odpis\u00f3w",
    "Op?aty": "Op\u0142aty",
    "Pe?ne": "Pe\u0142ne",
    "Pe?nomocnictwo": "Pe\u0142nomocnictwo",
    "Us?uga": "Us\u0142uga",
    "Wyj?tek": "Wyj\u0105tek",
    "adunk?w": "\u0142adunk\u00f3w",
    "aktyw?w": "aktyw\u00f3w",
    "b??d?w": "b\u0142\u0119d\u00f3w",
    "b??du": "b\u0142\u0119du",
    "b??dy": "b\u0142\u0119dy",
    "b?d": "b\u0119d",
    "bezpo?rednia": "bezpo\u015brednia",
    "bezpo?redniej": "bezpo\u015bredniej",
    "bezpo?rednio": "bezpo\u015brednio",
    "bie??cy": "bie\u017c\u0105cy",
    "by?o": "by\u0142o",
    "cel?w": "cel\u00f3w",
    "cz??ci": "cz\u0119\u015bci",
    "cz??ciowego": "cz\u0119\u015bciowego",
    "d?u?ej": "d\u0142u\u017cej",
    "d?u": "d\u0142u",
    "d?ugo?ci": "d\u0142ugo\u015bci",
    "d?ugo": "d\u0142ugo",
    "d?w": "d\u00f3w",
    "dor?cze": "dor\u0119cze",
    "dor?czeniu": "dor\u0119czeniu",
    "dotycz?ca": "dotycz\u0105ca",
    "dotycz?ce": "dotycz\u0105ce",
    "dzia?a": "dzia\u0142a",
    "dzia?alno": "dzia\u0142alno",
    "dzia?alno?ci": "dzia\u0142alno\u015bci",
    "dzia?ania": "dzia\u0142ania",
    "finans?w": "finans\u00f3w",
    "je?eli": "je\u017celi",
    "ka?de": "ka\u017cde",
    "koryguj?cej": "koryguj\u0105cej",
    "korzystaj?cego": "korzystaj\u0105cego",
    "koszt?w": "koszt\u00f3w",
    "ksi?g": "ksi\u0105g",
    "ksi?ga": "ksi\u0119ga",
    "ksi?gach": "ksi\u0119gach",
    "ksi?gi": "ksi\u0119gi",
    "ksi?gowa": "ksi\u0119gowa",
    "ksi?gowego": "ksi\u0119gowego",
    "kt?ra": "kt\u00f3ra",
    "kt?re": "kt\u00f3re",
    "kt?rego": "kt\u00f3rego",
    "kt?ry": "kt\u00f3ry",
    "kt?rym": "kt\u00f3rym",
    "limit?w": "limit\u00f3w",
    "maj?tku": "maj\u0105tku",
    "mi?dzy": "mi\u0119dzy",
    "mi?dzyokresowe": "mi\u0119dzyokresowe",
    "mi?dzyokresowych": "mi\u0119dzyokresowych",
    "mierno?ci": "mierno\u015bci",
    "miesi?ca": "miesi\u0105ca",
    "miesi?cu": "miesi\u0105cu",
    "miesi?cy": "miesi\u0119cy",
    "mo?e": "mo\u017ce",
    "mo?liwo": "mo\u017cliwo",
    "mo?na": "mo\u017cna",
    "nale?n": "nale\u017cn",
    "nast?pi": "nast\u0105pi",
    "nast?pi?o": "nast\u0105pi\u0142o",
    "nast?puj": "nast\u0119puj",
    "nast?puj?cego": "nast\u0119puj\u0105cego",
    "nieczysto?ci": "nieczysto\u015bci",
    "niekt?re": "niekt\u00f3re",
    "nieprowadz?cych": "nieprowadz\u0105cych",
    "niew?a": "niew\u0142a",
    "niew?a?ciwego": "niew\u0142a\u015bciwego",
    "niezale?nie": "niezale\u017cnie",
    "obci??a": "obci\u0105\u017ca",
    "obejmuj?ca": "obejmuj\u0105ca",
    "obejmuj?cej": "obejmuj\u0105cej",
    "obj?ty": "obj\u0119ty",
    "obj?tym": "obj\u0119tym",
    "obowi?zek": "obowi\u0105zek",
    "obowi?zku": "obowi\u0105zku",
    "obowi?zuje": "obowi\u0105zuje",
    "odpis?w": "odpis\u00f3w",
    "odr?bnie": "odr\u0119bnie",
    "odr?bnym": "odr\u0119bnym",
    "og?lne": "og\u00f3lne",
    "og?lnego": "og\u00f3lnego",
    "og?lnym": "og\u00f3lnym",
    "okre?laj": "okre\u015blaj",
    "okres?w": "okres\u00f3w",
    "op?aca": "op\u0142aca",
    "op?at": "op\u0142at",
    "op?aty": "op\u0142aty",
    "os?b": "os\u00f3b",
    "p??niej": "p\u00f3\u017aniej",
    "p?atnik": "p\u0142atnik",
    "pe?ne": "pe\u0142ne",
    "pe?nego": "pe\u0142nego",
    "pe?nomocnictwa": "pe\u0142nomocnictwa",
    "pe?nomocnictwo": "pe\u0142nomocnictwo",
    "pi?mie": "pi\u015bmie",
    "po?redni": "po\u015bredni",
    "po?rednie": "po\u015brednie",
    "podatnik?w": "podatnik\u00f3w",
    "podlegaj?cym": "podlegaj\u0105cym",
    "podzia?u": "podzia\u0142u",
    "poje?dzie": "poje\u017adzie",
    "post?powania": "post\u0119powania",
    "post?powaniem": "post\u0119powaniem",
    "poszczeg?lnych": "poszczeg\u00f3lnych",
    "potr?calne": "potr\u0105calne",
    "prawid?owe": "prawid\u0142owe",
    "prawid?owego": "prawid\u0142owego",
    "protoko?u": "protoko\u0142u",
    "prowadz?cego": "prowadz\u0105cego",
    "prowadz?cych": "prowadz\u0105cych",
    "prze?om": "prze\u0142om",
    "przekraczaj?c": "przekraczaj\u0105c",
    "przekraczaj?cego": "przekraczaj\u0105cego",
    "przekraczaj?cej": "przekraczaj\u0105cej",
    "przeksi?gowanie": "przeksi\u0119gowanie",
    "przes?a": "przes\u0142a",
    "przes?ana": "przes\u0142ana",
    "przes?anek": "przes\u0142anek",
    "przes?anie": "przes\u0142anie",
    "przesy?ania": "przesy\u0142ania",
    "przych?d": "przych\u00f3d",
    "przychod?w": "przychod\u00f3w",
    "przypadaj?ce": "przypadaj\u0105ce",
    "przypadaj?cych": "przypadaj\u0105cych",
    "przys?uguje": "przys\u0142uguje",
    "przysz?ych": "przysz\u0142ych",
    "r??ne": "r\u00f3\u017cne",
    "r?wnie": "r\u00f3wnie",
    "rachunkowo?ci": "rachunkowo\u015bci",
    "rejestruj?cej": "rejestruj\u0105cej",
    "rob?t": "rob\u00f3t",
    "rolnik?w": "rolnik\u00f3w",
    "rozporz?dzenia": "rozporz\u0105dzenia",
    "rozporz?dzeniu": "rozporz\u0105dzeniu",
    "rycza?towych": "rycza\u0142towych",
    "rycza?tu": "rycza\u0142tu",
    "samoch?d": "samoch\u00f3d",
    "sk?ada": "sk\u0142ada",
    "sk?adek": "sk\u0142adek",
    "sk?adki": "sk\u0142adki",
    "sk?adnik": "sk\u0142adnik",
    "sk?adnika": "sk\u0142adnika",
    "sk?adnikiem": "sk\u0142adnikiem",
    "sk?adowanie": "sk\u0142adowanie",
    "sk?d": "sk\u0105d",
    "skutk?w": "skutk\u00f3w",
    "sp??ki": "sp\u00f3\u0142ki",
    "sp??nienie": "sp\u00f3\u017anienie",
    "sp?aty": "sp\u0142aty",
    "spe?nia": "spe\u0142nia",
    "spe?nione": "spe\u0142nione",
    "spos?b": "spos\u00f3b",
    "sprzeda?y": "sprzeda\u017cy",
    "sprzedaj?cemu": "sprzedaj\u0105cemu",
    "szczeg?lne": "szczeg\u00f3lne",
    "szczeg?lnego": "szczeg\u00f3lnego",
    "tak?e": "tak\u017ce",
    "towar?w": "towar\u00f3w",
    "tre?ci": "tre\u015bci",
    "trwa?ego": "trwa\u0142ego",
    "trwa?ym": "trwa\u0142ym",
    "tytu?u": "tytu\u0142u",
    "u?ytek": "u\u017cytek",
    "u?ytku": "u\u017cytku",
    "u?ywanego": "u\u017cywanego",
    "u?ywania": "u\u017cywania",
    "u?ywanie": "u\u017cywanie",
    "u?ywany": "u\u017cywany",
    "u?ywanym": "u\u017cywanym",
    "uj?cia": "uj\u0119cia",
    "uniemo?liwiaj": "uniemo\u017cliwiaj",
    "uniemo?liwiaj?ce": "uniemo\u017cliwiaj\u0105ce",
    "up?ywu": "up\u0142ywu",
    "upowa?nia": "upowa\u017cnia",
    "urz?du": "urz\u0119du",
    "us?ug": "us\u0142ug",
    "us?uga": "us\u0142uga",
    "us?ugi": "us\u0142ugi",
    "ustali?y": "ustali\u0142y",
    "w?a?ciwa": "w\u0142a\u015bciwa",
    "w?a?ciwego": "w\u0142a\u015bciwego",
    "w?a?ciwym": "w\u0142a\u015bciwym",
    "w?a?nie": "w\u0142a\u015bnie",
    "w?a": "w\u0142a",
    "w?asno": "w\u0142asno",
    "warto?ci": "warto\u015bci",
    "wcze?niej": "wcze\u015bniej",
    "wcze?niejsze": "wcze\u015bniejsze",
    "wed?ug": "wed\u0142ug",
    "wej?ciu": "wej\u015bciu",
    "wi?c": "wi\u0119c",
    "wielko?ci": "wielko\u015bci",
    "wnosz?cego": "wnosz\u0105cego",
    "wskazuj?cego": "wskazuj\u0105cego",
    "wsp??mierno?ci": "wsp\u00f3\u0142mierno\u015bci",
    "wy??cznie": "wy\u0142\u0105cznie",
    "wy?adunek": "wy\u0142adunek",
    "wy?szy": "wy\u017cszy",
    "wydatk?w": "wydatk\u00f3w",
    "wyja?nienia": "wyja\u015bnienia",
    "wynikaj?c": "wynikaj\u0105c",
    "wyodr?bni": "wyodr\u0119bni",
    "wytw?rcz": "wytw\u00f3rcz",
    "wyw?z": "wyw\u00f3z",
    "wywo?uje": "wywo\u0142uje",
    "z?o?enia": "z\u0142o\u017cenia",
    "z?o?enie": "z\u0142o\u017cenie",
    "z?o?eniu": "z\u0142o\u017ceniu",
    "z?o?on": "z\u0142o\u017con",
    "z?o?ona": "z\u0142o\u017cona",
    "z?o": "z\u0142o",
    "z?o?y": "z\u0142o\u017cy",
    "za?adunek": "za\u0142adunek",
    "za?o": "za\u0142o",
    "za?o?ono": "za\u0142o\u017cono",
    "zako?czeniu": "zako\u0144czeniu",
    "zaksi?gowa": "zaksi\u0119gowa",
    "zap?aty": "zap\u0142aty",
    "zar?wno": "zar\u00f3wno",
    "zast?puje": "zast\u0119puje",
    "zg?asza": "zg\u0142asza",
    "zg?osi": "zg\u0142osi",
    "zobowi?za": "zobowi\u0105za",
    "zosta?a": "zosta\u0142a",
    "zosta?y": "zosta\u0142y",
    "zrycza?towanym": "zrycza\u0142towanym",
    "zwi?kszaj": "zwi\u0119kszaj",
    "zwi?zane": "zwi\u0105zane",
    "zwi?zanych": "zwi\u0105zanych",
}

# Exact token repairs used during apply; this safely covers cases that the regex
# report does not see, such as leading/trailing corrupted letters.
EXACT_TOKEN_MAP = {
    "?e": "\u017ce",
    "si?": "si\u0119",
    "s?": "s\u0105",
    "by?": "by\u0107",
    "ni?": "ni\u017c",
    "dat?": "dat\u0119",
    "korekt?": "korekt\u0119",
    "dzie?": "dzie\u0144",
    "b?d?": "b\u0119d\u0119",
    "mog?": "mog\u0119",
    "stanowi?": "stanowi\u0105",
    "z?o?y?": "z\u0142o\u017cy\u0107",
    "z?o?on?": "z\u0142o\u017con\u0105",
    "sk?ada?": "sk\u0142ada\u0107",
    "zg?osi?": "zg\u0142osi\u0107",
    "przes?a?": "przes\u0142a\u0107",
    "zrobi??": "zrobi\u0107?",
    "zrobi?": "zrobi\u0107",
    "skorygowa?": "skorygowa\u0107",
    "zaksi?gowa?": "zaksi\u0119gowa\u0107",
    "ksi?gowa?": "ksi\u0119gowa\u0107",
    "odliczy?": "odliczy\u0107",
    "odlicz?": "odlicz\u0119",
    "decyduj?": "decyduj\u0105",
    "Zasad?": "Zasad\u0105",
    "uj??": "uj\u0105\u0107",
    "powsta?": "powsta\u0142",
    "nast?pi?": "nast\u0105pi\u0107",
    "mo?liwo??": "mo\u017cliwo\u015b\u0107",
    "dzia?alno??": "dzia\u0142alno\u015b\u0107",
    "dzia?alno?ci?": "dzia\u0142alno\u015bci\u0105",
    "gospodarcz?": "gospodarcz\u0105",
    "r?wnie?": "r\u00f3wnie\u017c",
    "w?asno??": "w\u0142asno\u015b\u0107",
    "?rodka": "\u015brodka",
    "?rodkiem": "\u015brodkiem",
    "?wiadcze?": "\u015bwiadcze\u0144",
    "dor?cze?": "dor\u0119cze\u0144",
    "rozlicze?": "rozlicze\u0144",
    "dekretacj?": "dekretacj\u0119",
    "zobowi?za?": "zobowi\u0105za\u0144",
    "obci??a?": "obci\u0105\u017ca\u0107",
    "nale?n?": "nale\u017cn\u0105",
    "przekraczaj?c?": "przekraczaj\u0105c\u0105",
    "wynikaj?c?": "wynikaj\u0105c\u0105",
    "us?ug?": "us\u0142ug\u0119",
    "sprzeda?": "sprzeda\u017c",
    "Sprzeda?": "Sprzeda\u017c",
    "cz???": "cz\u0119\u015b\u0107",
    "?przych?d": '"przych\u00f3d',
    "us?uga?": 'us\u0142uga"',
    "okre?laj?": "okre\u015blaj\u0105",
    "zwi?kszaj?": "zwi\u0119kszaj\u0105",
    "wprowadzi?": "wprowadzi\u0107",
    "wskazywa?": "wskazywa\u0107",
    "dostosowa?": "dostosowa\u0107",
    "przypisa?": "przypisa\u0107",
    "wyodr?bni?": "wyodr\u0119bni\u0107",
    "wystawion?": "wystawion\u0105",
    "wybran?": "wybran\u0105",
    "wytwórcz?": "wytw\u00f3rcz\u0105",
    "metod?": "metod\u0119",
    "amortyzacj?": "amortyzacj\u0119",
    "informacj?": "informacj\u0119",
    "poda?": "poda\u0144",
    "bior?": "bior\u0105",
    "?alu": "\u017calu",
    "piecz??": "piecz\u0119\u0107",
    "podlegaj?": "podlegaj\u0105",
    "deklaracj?": "deklaracj\u0119",
    "konkretn?": "konkretn\u0105",
    "ocenia?": "ocenia\u0107",
    "ujmowa?": "ujmowa\u0107",
    "poniewa?": "poniewa\u017c",
    "?wietle": "\u015bwietle",
    "?ładunków": "\u0142adunk\u00f3w",
    "maj?": "maj\u0105",
    "zaliczk?": "zaliczk\u0119",
    "zmieni?": "zmieni\u0107",
    "kwot?": "kwot\u0119",
    "cen?": "cen\u0119",
    "dotycz?": "dotycz\u0105",
    "ustali?": "ustali\u0107",
    "stosowa?": "stosowa\u0107",
    "faktur?": "faktur\u0119",
    "pyta?": "pyta\u0144",
    "proporcj?": "proporcj\u0119",
    "wykluczaj?": "wykluczaj\u0105",
    "odlicza?": "odlicza\u0107",
    "przelicza?": "przelicza\u0107",
    "rozlicza?": "rozlicza\u0107",
    "zawiera?": "zawiera\u0107",
    "kontrol?": "kontrol\u0105",
    "zosta?": "zosta\u0107",
    "decyzj?": "decyzj\u0105",
    "podatkow?": "podatkow\u0105",
    "weryfikacj?": "weryfikacj\u0119",
    "reguluj?": "reguluj\u0105",
    "rozstrzygaj?": "rozstrzygaj\u0105",
}

PHRASE_FIX_MAP = {
    "Je\u017celi przepisy szczeg\u00f3lne nie stanowi\u0107 inaczej": "Je\u017celi przepisy szczeg\u00f3lne nie stanowi\u0105 inaczej",
    "Op\u0142aty ustalone w umowie leasingu stanowi\u0107 koszt uzyskania przychod\u00f3w korzystaj\u0105cego": "Op\u0142aty ustalone w umowie leasingu stanowi\u0105 koszt uzyskania przychod\u00f3w korzystaj\u0105cego",
    "Op\u0142aty leasingowe za samoch\u00f3d osobowy mog\u0119 by\u0107 kosztem uzyskania przychod\u00f3w": "Op\u0142aty leasingowe za samoch\u00f3d osobowy mog\u0105 by\u0107 kosztem uzyskania przychod\u00f3w",
    "kt\u00f3ry nie zosta\u0107 obj\u0119ty decyzj\u0105": "kt\u00f3ry nie zosta\u0142 obj\u0119ty decyzj\u0105",
}

FALSE_POSITIVES = {"APPLE?Czy"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repair UTF-8 corruption in KB seeds.")
    parser.add_argument("--apply", action="store_true", help="Modify files in place after a clean dry-run scan.")
    return parser.parse_args()


def read_json(path: Path) -> tuple[dict | list, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload["records"] if isinstance(payload, dict) else payload
    return payload, records


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def split_outer_punctuation(token: str) -> tuple[str, str, str]:
    start = 0
    end = len(token)
    while start < end and token[start] in OUTER_PUNCT:
        start += 1
    while end > start and token[end - 1] in OUTER_PUNCT:
        end -= 1
    return token[:start], token[start:end], token[end:]


def scan_patterns(records: list[dict]) -> tuple[Counter[str], dict[str, Counter[str]]]:
    pattern_counts: Counter[str] = Counter()
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        for field in FIELDS:
            value = record.get(field)
            if not isinstance(value, str):
                continue
            for match in defaultdict_re_find(value):
                if match not in FALSE_POSITIVES:
                    pattern_counts[match] += 1
                    grouped[field][match] += 1
    return pattern_counts, grouped


def defaultdict_re_find(value: str) -> list[str]:
    import re

    return re.findall(CORRUPTION_PATTERN, value)


def repair_text(value: str) -> str:
    parts = []
    for chunk in value.split():
        prefix, core, suffix = split_outer_punctuation(chunk)
        core = EXACT_TOKEN_MAP.get(core, core)
        parts.append(prefix + core + suffix)
    repaired = " ".join(parts)
    for corrupted, clean in sorted(CORRUPTION_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        repaired = repaired.replace(corrupted, clean)
    for corrupted, clean in PHRASE_FIX_MAP.items():
        repaired = repaired.replace(corrupted, clean)
    return repaired


def collect_unrelated_issues(records: list[dict], file_path: Path) -> list[str]:
    issues: list[str] = []
    for index, record in enumerate(records):
        for field in FIELDS:
            value = record.get(field)
            if isinstance(value, str) and "APPLE?Czy" in value:
                issues.append(
                    f"{file_path} record {index} field '{field}' contains 'APPLE?Czy' "
                    "which looks like duplicated prompt text rather than UTF-8 corruption and was left unchanged."
                )
    return issues


def find_potential_duplicates(records: list[dict], file_path: Path) -> list[dict]:
    grouped: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, record in enumerate(records):
        law_name = record.get("law_name")
        article_number = record.get("article_number")
        if isinstance(law_name, str) and isinstance(article_number, str):
            grouped[(law_name, article_number)].append(index)
    duplicates = []
    for (law_name, article_number), indexes in sorted(grouped.items()):
        if len(indexes) > 1:
            duplicates.append(
                {
                    "file": str(file_path),
                    "law_name": law_name,
                    "article_number": article_number,
                    "count": len(indexes),
                    "record_indexes": indexes,
                }
            )
    return duplicates


def build_report(mode: str, scan_results: list[dict], records_fixed: int, records_per_file: dict[str, int]) -> dict:
    pattern_counter: Counter[str] = Counter()
    grouped_patterns: dict[str, dict[str, Counter[str]]] = {}
    unrelated_issues: list[str] = []
    potential_duplicates: list[dict] = []
    for item in scan_results:
        pattern_counter.update(item["patterns"])
        grouped_patterns[item["file"]] = {
            field: Counter(counts) for field, counts in item["grouped_patterns"].items()
        }
        unrelated_issues.extend(item["unrelated"])
        potential_duplicates.extend(item["duplicates"])
    unmapped = sorted(pattern for pattern in pattern_counter if pattern not in CORRUPTION_MAP)
    corrections_applied = {pattern: CORRUPTION_MAP[pattern] for pattern in sorted(pattern_counter) if pattern in CORRUPTION_MAP}
    return {
        "scan_date": date.today().isoformat(),
        "mode": mode,
        "files_scanned": [item["file"] for item in scan_results],
        "corrupted_patterns_found": dict(sorted(pattern_counter.items())),
        "corrupted_patterns_by_file_and_field": {
            file_path: {field: dict(sorted(counter.items())) for field, counter in fields.items()}
            for file_path, fields in grouped_patterns.items()
        },
        "corrections_applied": corrections_applied,
        "records_fixed": records_fixed,
        "records_per_file": records_per_file,
        "unmapped_corruptions": unmapped,
        "potential_duplicates_after_fix": potential_duplicates,
        "unrelated_issues_observed": sorted(set(unrelated_issues)),
    }


def print_grouped_patterns(scan_results: list[dict]) -> None:
    print("UTF-8 corruption scan by file and field")
    for item in scan_results:
        print(f"\n[{item['file']}]")
        if not item["grouped_patterns"]:
            print("  no regex-corrupted patterns found")
            continue
        for field, counts in sorted(item["grouped_patterns"].items()):
            print(f"  {field}:")
            for pattern, count in sorted(counts.items()):
                print(f"    {pattern}: {count}")


def ensure_backup(path: Path) -> None:
    backup_path = path.with_name(path.name + BACKUP_SUFFIX)
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def main() -> int:
    args = parse_args()
    scan_results: list[dict] = []

    for file_path in KB_FILES:
        payload, records = read_json(file_path)
        pattern_counts, grouped_patterns = scan_patterns(records)
        fixed_records = []
        for record in records:
            fixed = {}
            for key, value in record.items():
                if key in FIELDS and isinstance(value, str):
                    fixed[key] = repair_text(value)
                else:
                    fixed[key] = value
            fixed_records.append(fixed)
        if isinstance(payload, dict):
            fixed_payload = dict(payload)
            fixed_payload["records"] = fixed_records
        else:
            fixed_payload = fixed_records
        scan_results.append(
            {
                "file": str(file_path),
                "payload": payload,
                "fixed_payload": fixed_payload,
                "patterns": pattern_counts,
                "grouped_patterns": grouped_patterns,
                "unrelated": collect_unrelated_issues(records, file_path),
                "duplicates": find_potential_duplicates(fixed_records, file_path),
            }
        )

    print_grouped_patterns(scan_results)

    dry_report = build_report(
        mode="dry_run" if not args.apply else "applied",
        scan_results=scan_results,
        records_fixed=0,
        records_per_file={item["file"]: 0 for item in scan_results},
    )

    if dry_report["unmapped_corruptions"]:
        REPORT_PATH.write_text(json.dumps(dry_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("\nUnmapped corruptions detected; refusing to modify files:")
        for pattern in dry_report["unmapped_corruptions"]:
            print(f"  - {pattern}")
        return 1

    if not args.apply:
        REPORT_PATH.write_text(json.dumps(dry_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return 0

    records_fixed = 0
    records_per_file: dict[str, int] = {}
    for item in scan_results:
        path = Path(item["file"])
        ensure_backup(path)
        original_payload = item["payload"]
        fixed_payload = item["fixed_payload"]
        original_records = original_payload["records"] if isinstance(original_payload, dict) else original_payload
        fixed_records = fixed_payload["records"] if isinstance(fixed_payload, dict) else fixed_payload
        changed_records = sum(1 for before, after in zip(original_records, fixed_records) if before != after)
        records_fixed += changed_records
        records_per_file[item["file"]] = changed_records
        if changed_records:
            write_json(path, fixed_payload)

    applied_scan_results = []
    for file_path in KB_FILES:
        payload, records = read_json(file_path)
        pattern_counts, grouped_patterns = scan_patterns(records)
        applied_scan_results.append(
            {
                "file": str(file_path),
                "payload": payload,
                "fixed_payload": payload,
                "patterns": pattern_counts,
                "grouped_patterns": grouped_patterns,
                "unrelated": collect_unrelated_issues(records, file_path),
                "duplicates": find_potential_duplicates(records, file_path),
            }
        )

    report = build_report(
        mode="applied",
        scan_results=applied_scan_results,
        records_fixed=records_fixed,
        records_per_file=records_per_file,
    )
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
