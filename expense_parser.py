"""Turns "10 ta paypoq oldim 13k" into ("10 ta paypoq oldim", 13000)."""
import re

NUM = r"(?:\d{1,3}(?:[ ,]\d{3})+|\d+(?:[.,]\d+)?)"
SUF = (r"(?:k|к|ming|тыс|mln|million|млн|m|thousand|so['ʻʼ’`]?m|som|sum|сум|сумов)")
PRICE_RE = re.compile(rf"(?<![\w.,])({NUM})(?:\s*({SUF}))?(?!\w)", re.I)
# "10 ta", "2 kg", "3 dona", "5 пар" -> quantity, NOT a price (unless it has k/ming/mln)
QTY_RE = re.compile(
    r"\s*(ta|dona|kg|gr|g|l|litr|ml|sht|pcs|pair|pairs|kishi|nafar|metr|шт|штук|кг|гр|г|л|литр|пар|пары|человек)(?!\w)",
    re.I)

MULT = {"k": 1_000, "к": 1_000, "ming": 1_000, "тыс": 1_000, "thousand": 1_000,
        "mln": 1_000_000, "million": 1_000_000, "млн": 1_000_000, "m": 1_000_000}


def _to_number(raw: str, has_suffix: bool) -> float:
    s = raw.strip()
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s) and not has_suffix:   # 13.000 -> 13000
        return float(s.replace(".", ""))
    if re.fullmatch(r"\d{1,3}(?:[ ,]\d{3})+", s):                    # 13 000 / 13,000
        return float(re.sub(r"[ ,]", "", s))
    return float(s.replace(",", "."))


def parse_line(line: str):
    """Return (item, amount_int) or None if no price found. item may be '' (caller localizes)."""
    line = line.strip()
    if not line:
        return None
    cands = []
    for m in PRICE_RE.finditer(line):
        suffix = (m.group(2) or "").lower()
        if not suffix and QTY_RE.match(line[m.end():]):
            continue
        cands.append(m)
    if not cands:
        return None
    with_suffix = [m for m in cands if m.group(2) and m.group(2).lower() in MULT]
    m = with_suffix[-1] if with_suffix else cands[-1]
    suffix = (m.group(2) or "").lower()
    amount = _to_number(m.group(1), suffix in MULT) * MULT.get(suffix, 1)
    amount = int(round(amount))
    if amount <= 0 or amount > 10 ** 12:
        return None
    item = (line[:m.start()] + " " + line[m.end():])
    item = re.sub(r"\s+", " ", item).strip(" -–—:,.;")
    return (item, amount)


def parse_message(text: str):
    """Supports several expenses in one message (one per line or separated by ';')."""
    parsed, failed = [], []
    for line in re.split(r"[\n;]+", text):
        if not line.strip():
            continue
        res = parse_line(line)
        if res:
            parsed.append(res)
        else:
            failed.append(line.strip())
    return parsed, failed


def fmt_money(n) -> str:
    return f"{int(n):,}".replace(",", " ")
