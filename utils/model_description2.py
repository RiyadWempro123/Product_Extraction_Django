
import pdfplumber
import re
import json
from pathlib import Path

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

PDF_FILE = Path("PX03P.pdf")
OUTPUT_FILE = Path("output/model_description_chart_PX03P.json")

# PDF_FILE = Path("PX20P.pdf")
# OUTPUT_FILE = Path("output/model_description_chart_PX20P.json")

# PDF_FILE = Path("PX01X.pdf")
# OUTPUT_FILE = Path("output/model_description_chart_PX01X.json")

OUTPUT_FILE.parent.mkdir(exist_ok=True)

# ---------------------------------------------------
# SECTION SYNONYMS (MATCHES YOUR PDF)
# ---------------------------------------------------

SECTION_SYNONYMS = {
    "Model Series": ["model series"],
    "Center Body Material": ["center body material"],
    "Connection": ["connection", "fluid connection"],
    "Fluid Caps / Manifold Material": [
        "fluid caps manifold material",
        "fluid caps & manifold material",
        "fluid caps and manifold material"
    ],
    "Hardware Material": ["hardware material"],
    "Seat / Spacer Material": ["seat material", "seat spacer material"],
    "Check Material": ["check material", "ball material"],
    "Diaphragm / O-Ring Material": [
        "diaphragm material",
        "diaphragm / o-ring material",
        "diaphragm & o-ring material",
        "diaphragm and o-ring material"
    ],
    "Revision": ["revision"],
    "Specialty Code 1": ["specialty code 1"],
    "Specialty Code 2": ["specialty code 2"]
}

VALID_SECTIONS = list(SECTION_SYNONYMS.keys())

# ---------------------------------------------------
# REGEX
# ---------------------------------------------------

INLINE_CODE_DESC = re.compile(r"^\s*([A-Z0-9]{1,5})\s*[-–]\s*(.+)$")
CODE_ONLY = re.compile(r"^\s*([A-Z0-9]{1,5})\s*[-–]\s*$")

# ---------------------------------------------------
# CLEAN & NORMALIZE
# ---------------------------------------------------

def clean_line(text):
    if not text:
        return ""
    text = re.sub(r"\(cid:\d+\)", "", text)
    text = text.replace("\u2013", "-")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def normalize(text):
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------------------------------------------------
# NOISE FILTER
# ---------------------------------------------------

def is_layout_noise(line):
    if line in {"X", "-", "PX01", "PX03", "PX20"}:
        return True
    if re.fullmatch(r"[X\- ]+", line):
        return True
    if line.startswith("(*)"):
        return True
    return False

# ---------------------------------------------------
# SECTION DETECTION
# ---------------------------------------------------

def detect_section(line):
    norm = normalize(line)
    for canonical, variants in SECTION_SYNONYMS.items():
        for v in variants:
            if v in norm: 
            # if norm == v:
                return canonical
    return None

# ---------------------------------------------------
# MAIN EXTRACTION
# ---------------------------------------------------

def extract_model_description_chart(pdf_path):
    chart = {s: [] for s in VALID_SECTIONS}
    seen = {s: set() for s in VALID_SECTIONS}

    current_section = None
    parsing_started = False
    pending_codes = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for raw in text.splitlines():
                line = clean_line(raw)

                if not line or is_layout_noise(line):
                    continue

                lower = line.lower()

                # Start parsing after chart title
                if lower == "model code explanation":
                    parsing_started = True
                    continue

                if not parsing_started:
                    continue

                # Stop cleanly
                if lower.startswith("special testing"):
                    return {k: v for k, v in chart.items() if v}

                # Section header
                section = detect_section(line)
                if section:
                    current_section = section
                    pending_codes.clear()
                    continue

                if not current_section:
                    continue

                # Case 1: Code only (e.g. "D-")
                m = CODE_ONLY.match(line)
                if m:
                    pending_codes.append(m.group(1))
                    continue

                # Case 2: Inline code-description
                m = INLINE_CODE_DESC.match(line)
                if m:
                    code, desc = m.groups()
                    if code not in seen[current_section]:
                        chart[current_section].append({
                            "code": code,
                            "description": desc.strip()
                        })
                        seen[current_section].add(code)
                    continue

                # Case 3: Description-only line → assign to pending code
                if pending_codes:
                    code = pending_codes.pop(0)
                    desc = line.strip()

                    if code not in seen[current_section]:
                        chart[current_section].append({
                            "code": code,
                            "description": desc
                        })
                        seen[current_section].add(code)
    

    return {k: v for k, v in chart.items() if v}

# ---------------------------------------------------
# RUN
# ---------------------------------------------------

if __name__ == "__main__":
    if not PDF_FILE.exists():
        print(f"❌ PDF not found: {PDF_FILE}")
    else:
        result = extract_model_description_chart(PDF_FILE)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"✅ Model Description Chart extracted → {OUTPUT_FILE}")
