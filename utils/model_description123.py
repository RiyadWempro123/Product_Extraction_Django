"""
ARO Pumps – Model Description Chart Extractor (Advanced)
=========================================================
Improvements over v1:
  • Uses pdfplumber table extraction first, falls back to text parsing
  • modelDescriptionChartPage hint narrows search (skips irrelevant pages)
  • Multi-page state preserved across page boundaries
  • Fuzzy section-header matching (handles extra words / partial headers)
  • Orphan-code buffer survives noise lines (configurable tolerance)
  • Deduplication with conflict logging
  • Debug mode with per-line trace output
  • Returns structured result + extraction metadata
"""

import pdfplumber
import re
import json
import logging
from pathlib import Path
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(message)s")
log = logging.getLogger("aro_extractor")



# ---------------------------------------------------------------------------
# SECTION SYNONYMS
# ---------------------------------------------------------------------------

SECTION_SYNONYMS = {
    "Model Series":                 ["model series"],
    "Center Body Material":         ["center body material"],
    "Connection":                   ["connection", "fluid connection"],
    "Fluid Caps / Manifold Material": [
        "fluid caps manifold material",
        "fluid caps & manifold material",
        "fluid caps and manifold material",
        "fluid caps material",
    ],
    "Hardware Material":            ["hardware material"],
    "Seat / Spacer Material":       ["seat material", "seat spacer material", "seat and spacer material"],
    "Check Material":               ["check material", "ball material", "check ball material"],
    "Diaphragm / O-Ring Material":  [
        "diaphragm oring material",
        "diaphragm o ring material",
        "diaphragm material",
        "diaphragm and oring material",
    ],
    "Revision":                     ["revision"],
    "Specialty Code 1":             ["specialty code 1"],
    "Specialty Code 2":             ["specialty code 2"],
}

VALID_SECTIONS = list(SECTION_SYNONYMS.keys())

# Minimum fuzzy-match ratio to accept a section header (0.0–1.0)
FUZZY_THRESHOLD = 0.82

# How many non-matching lines a pending code survives before being discarded
ORPHAN_TOLERANCE = 3


# ---------------------------------------------------------------------------
# REGEX
# ---------------------------------------------------------------------------

# "AB - Some description"  or  "A1 - desc"
INLINE_CODE_DESC = re.compile(r"^\s*([A-Z0-9]{1,5})\s*[-–]\s*(.+)$")

# "D -"  (code with no description on the same line)
CODE_ONLY = re.compile(r"^\s*([A-Z0-9]{1,5})\s*[-–]\s*$")

# Lines that are purely a code with no dash at all (rare but seen in some ARO PDFs)
BARE_CODE = re.compile(r"^\s*([A-Z0-9]{1,5})\s*$")


# ---------------------------------------------------------------------------
# HELPERS – clean & normalize
# ---------------------------------------------------------------------------

def clean_line(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\(cid:\d+\)", "", text)          # PDF encoding artefacts
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u00ae", "").replace("\u2122", "")  # ® ™
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)   # strip parenthetical remarks
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_description(desc: str) -> str:
    desc = re.sub(r"\(cid:\d+\)", "", desc)
    desc = re.sub(r"^\W+", "", desc)     # leading non-word chars
    desc = desc.strip(" -–/\\")
    return desc.strip()


# ---------------------------------------------------------------------------
# NOISE FILTER
# ---------------------------------------------------------------------------

_NOISE_EXACT = {"X", "-", "--", "PX01", "PX03", "PX20", "N/A", "NA"}
_NOISE_PATTERNS = [
    re.compile(r"^[X\-\s]+$"),          # rows of X or dashes
    re.compile(r"^\(\*\)"),             # footnote markers
    re.compile(r"^page\s+\d+", re.I),  # page numbers
    re.compile(r"^\d{1,3}$"),           # bare page/row numbers
]

def is_noise(line: str) -> bool:
    if line in _NOISE_EXACT:
        return True
    for pat in _NOISE_PATTERNS:
        if pat.match(line):
            return True
    return False


# ---------------------------------------------------------------------------
# SECTION DETECTION  (exact → fuzzy fallback)
# ---------------------------------------------------------------------------

def _fuzzy_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def detect_section(line: str) -> str | None:
    norm = normalize(line)
    # 1. Exact match
    for canonical, variants in SECTION_SYNONYMS.items():
        if norm in variants:
            return canonical
    # 2. Fuzzy match – the normalized line must be "close enough" to a variant
    best_score, best_section = 0.0, None
    for canonical, variants in SECTION_SYNONYMS.items():
        for v in variants:
            score = _fuzzy_ratio(norm, v)
            if score > best_score:
                best_score, best_section = score, canonical
    if best_score >= FUZZY_THRESHOLD:
        log.debug("Fuzzy match '%.2f': '%s' → %s", best_score, line, best_section)
        return best_section
    return None


# ---------------------------------------------------------------------------
# TABLE-BASED EXTRACTION  (preferred when PDF has real tables)
# ---------------------------------------------------------------------------

def _extract_from_table(table: list[list]) -> list[dict]:
    """
    Given a pdfplumber table (list of rows), return [{code, description}, …].
    Handles two common layouts:
      • Two-column:  | CODE | Description |
      • Three-column: | CODE | - | Description |
    """
    entries = []
    for row in table:
        row = [clean_line(c or "") for c in row]
        row = [c for c in row if c and not is_noise(c)]
        if len(row) == 2:
            code, desc = row
        elif len(row) >= 3:
            code, *rest = row
            desc = " ".join(rest)
        else:
            continue
        code = code.strip()
        desc = clean_description(desc)
        # code must look like a real model code
        if re.fullmatch(r"[A-Z0-9]{1,5}", code) and desc:
            entries.append({"code": code, "description": desc})
    return entries


# ---------------------------------------------------------------------------
# MAIN EXTRACTOR
# ---------------------------------------------------------------------------

def extract_model_description_chart(
    pdf_path: str | Path,
    model_description_chart_page: int | None = None,
    debug: bool = False,
) -> dict:
    """
    Extract the Model Description Chart from an ARO pump PDF.

    Parameters
    ----------
    pdf_path : path to the PDF file
    model_description_chart_page : 1-based page hint (optional).
        If provided, extraction starts from that page and also searches
        a small window before it in case the title appears one page early.
    debug : emit per-line trace to stderr

    Returns
    -------
    dict  {section_name: [{code, description}, …], "_meta": {…}}
    """
    if debug:
        log.setLevel(logging.DEBUG)

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    chart   = {s: [] for s in VALID_SECTIONS}
    seen    = {s: set() for s in VALID_SECTIONS}

    current_section  = None
    parsing_started  = False
    pending_codes    = []          # [(code, ttl_remaining)]
    pages_parsed     = 0
    source_pages     = []

    # Page window: if hint given, start one page before (0-based)
    if model_description_chart_page is not None:
        start_page = max(0, model_description_chart_page - 2)   # -2 for 0-based + 1 early
    else:
        start_page = 0

    def _add_entry(section, code, desc):
        """Add entry, warn on duplicate with different description."""
        if code in seen[section]:
            existing = next(e for e in chart[section] if e["code"] == code)
            if existing["description"].lower() != desc.lower():
                log.warning(
                    "Duplicate code '%s' in [%s]: keeping '%s', ignoring '%s'",
                    code, section, existing["description"], desc,
                )
            return
        chart[section].append({"code": code, "description": desc})
        seen[section].add(code)
        log.debug("  [%s] %s → %s", section, code, desc)

    def _flush_pending(desc_line: str) -> bool:
        """Assign desc_line to the oldest pending code. Returns True if consumed."""
        nonlocal pending_codes
        if not pending_codes:
            return False
        code, _ = pending_codes.pop(0)
        desc = clean_description(desc_line)
        if desc:
            _add_entry(current_section, code, desc)
        return True

    def _age_pending():
        """Decrement TTL on pending codes; discard expired ones."""
        nonlocal pending_codes
        pending_codes = [(c, ttl - 1) for c, ttl in pending_codes if ttl - 1 > 0]

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            if page_idx < start_page:
                continue

            pages_parsed += 1

            # ----------------------------------------------------------
            # 1. Try table extraction first
            # ----------------------------------------------------------
            tables = page.extract_tables()
            table_codes_this_page: set[str] = set()

            for table in tables:
                if not table or len(table) < 2:
                    continue
                entries = _extract_from_table(table)
                if entries and current_section:
                    for e in entries:
                        table_codes_this_page.add(e["code"])
                        _add_entry(current_section, e["code"], e["description"])

            # ----------------------------------------------------------
            # 2. Text-line parsing (fills gaps / handles non-table PDFs)
            # ----------------------------------------------------------
            text = page.extract_text()
            if not text:
                continue

            source_pages.append(page_idx + 1)

            for raw in text.splitlines():
                line = clean_line(raw)
                if not line:
                    continue

                log.debug("LINE: %r", line)

                if is_noise(line):
                    _age_pending()
                    continue

                lower = line.lower()

                # ── Start trigger ──────────────────────────────────────
                if not parsing_started:
                    if "model code explanation" in lower or "model description chart" in lower:
                        parsing_started = True
                        log.debug("Parsing started on page %d", page_idx + 1)
                    continue

                # ── Stop trigger ───────────────────────────────────────
                stop_phrases = ("special testing", "notes:", "note:", "warranty")
                if any(lower.startswith(p) for p in stop_phrases):
                    log.debug("Stop trigger hit: %r", line)
                    goto_finish = True
                    break

                # ── Section header ─────────────────────────────────────
                section = detect_section(line)
                if section:
                    current_section = section
                    pending_codes.clear()
                    log.debug("Section → %s", section)
                    continue

                if not current_section:
                    continue

                # ── Code-only line (description follows) ──────────────
                m = CODE_ONLY.match(line)
                if m:
                    pending_codes.append((m.group(1), ORPHAN_TOLERANCE))
                    continue

                # ── Inline code + description ──────────────────────────
                m = INLINE_CODE_DESC.match(line)
                if m:
                    code, desc = m.groups()
                    # Skip if already captured from table
                    if code not in table_codes_this_page:
                        _add_entry(current_section, code, clean_description(desc))
                    continue

                # ── Bare code (no dash) ────────────────────────────────
                m = BARE_CODE.match(line)
                if m and len(line) <= 5:
                    pending_codes.append((m.group(1), ORPHAN_TOLERANCE))
                    continue

                # ── Description-only → assign to pending code ──────────
                if pending_codes:
                    _flush_pending(line)
                    continue

                # ── Unknown line ────────────────────────────────────────
                _age_pending()
                log.debug("  (unmatched) %r", line)

            else:
                # inner for-loop completed normally (no break); continue to next page
                continue
            # break out of page loop when stop trigger fires
            break

    result = {k: v for k, v in chart.items() if v}
    result["_meta"] = {
        "source_file":    pdf_path.name,
        "pages_scanned":  pages_parsed,
        "source_pages":   source_pages,
        "sections_found": list(result.keys()),
        "total_codes":    sum(len(v) for k, v in result.items() if k != "_meta"),
    }
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Extract ARO pump Model Description Chart")
    parser.add_argument("pdf",  help="Path to the ARO pump PDF")
    parser.add_argument("--page", type=int, default=None,
                        help="1-based page number hint for the chart")
    parser.add_argument("--output", default=None,
                        help="Output JSON file (default: <pdf_name>_chart.json)")
    parser.add_argument("--debug", action="store_true", help="Verbose trace output")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    out_path = Path(args.output) if args.output else pdf_path.with_name(
        pdf_path.stem + "_chart.json"
    )

    try:
        result = extract_model_description_chart(pdf_path, args.page, debug=args.debug)
    except FileNotFoundError as e:
        print(f"❌  {e}", file=sys.stderr)
        sys.exit(1)

    meta = result.pop("_meta", {})

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


    print(f"✅  Extracted {meta.get('total_codes', '?')} codes across "
          f"{len(meta.get('sections_found', []))} sections → {out_path}")
    print(f"   Pages scanned : {meta.get('pages_scanned')}")
    print(f"   Sections found: {', '.join(meta.get('sections_found', []))}")