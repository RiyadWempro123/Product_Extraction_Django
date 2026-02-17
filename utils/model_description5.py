import pdfplumber
import re
import json
from pathlib import Path

# --------------------------------------------------
# SECTION DEFINITIONS (CANONICAL + SYNONYMS)
# --------------------------------------------------

SECTION_SYNONYMS = {
    "Model Series": [
        "model series"
    ],
    "Center Body Material": [
        "center body material"
    ],
    "Air Motor / Air Cap Material": [
        "air motor air cap material",
        "air motor material",
        "air cap material"
    ],
    "Connection": [
        "connection",
        "fluid connection"
    ],
    "Fluid Caps / Manifold Material": [
        "fluid caps manifold material",
        "fluid cap manifold material",
        "fluid caps and manifold material"
    ],
    "Hardware Material": [
        "hardware material"
    ],
    "Seat / Spacer Material": [
        "seat spacer material",
        "seat material"
    ],
    "Check Material": [
        "check material",
        "ball material"
    ],
    "Diaphragm / O-Ring Material": [
        "diaphragm oring material",
        "diaphragm material"
    ],
    "Revision": [
        "revision"
    ],
    "Specialty Code 1": [
        "specialty code 1"
    ],
    "Specialty Code 2": [
        "specialty code 2"
    ]
}

VALID_SECTIONS = list(SECTION_SYNONYMS.keys())

# --------------------------------------------------
# REGEX FOR CODE - DESCRIPTION LINES
# --------------------------------------------------

INLINE_CODE_DESC = re.compile(
    r"^\s*([A-Z0-9]{1,6})\s*[-–]\s*(.+)$"
)

# --------------------------------------------------
# TEXT HELPERS
# --------------------------------------------------

def clean_line(text):
    if not text:
        return ""
    text = re.sub(r"\(cid:\d+\)", "", text)
    text = text.replace("\u2013", "-").replace("\u00ae", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize(text):
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def is_layout_noise(line):
    lower = line.lower()
    if lower.startswith(("page ", "notice", "special testing")):
        return True
    if re.fullmatch(r"[X\- ]+", line):
        return True
    return False

# --------------------------------------------------
# SECTION DETECTION (FIXED & FUTURE-PROOF)
# --------------------------------------------------

def detect_section(line):
    norm = normalize(line)
    for canonical, variants in SECTION_SYNONYMS.items():
        for v in variants:
            if normalize(v) in norm:
                return canonical
    return None

# --------------------------------------------------
# MAIN EXTRACTION FUNCTION
# --------------------------------------------------

def extract_model_description_chart(pdf_path, page_number):
    chart = {section: [] for section in VALID_SECTIONS}
    current_section = None
    parsing_started = False

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number - 1]
        text = page.extract_text()

        if not text:
            return {}

        for raw_line in text.splitlines():
            line = clean_line(raw_line)

            if not line or is_layout_noise(line):
                continue

            lower = line.lower()

            # Start parsing only after heading
            if "model description chart" in lower:
                parsing_started = True
                continue

            if not parsing_started:
                continue

            # SECTION HEADER
            section = detect_section(line)
            if section:
                current_section = section
                continue

            if not current_section:
                continue

            # CODE - DESCRIPTION LINE
            match = INLINE_CODE_DESC.match(line)
            if match:
                code, desc = match.groups()
                chart[current_section].append({
                    "code": code.strip(),
                    "description": desc.strip()
                })

    # Remove empty sections
    return {k: v for k, v in chart.items() if v}

# --------------------------------------------------
# EXAMPLE USAGE
# --------------------------------------------------
# PDF_FILE = Path("PX30R.pdf")
# PAGE_NUMBER = 2
# result = extract_model_description_chart(PDF_FILE, PAGE_NUMBER)
# print(json.dumps(result, indent=2, ensure_ascii=False))
