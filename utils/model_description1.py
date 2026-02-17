import pdfplumber
import re

SECTION_MAP = {
    "model series": "Model Series",
    "center body material": "Center Body Material",
    "connection": "Connection",
    "fluid caps / manifold material": "Fluid Caps / Manifold Material",
    "fluid caps and manifold material": "Fluid Caps / Manifold Material",
    "fluid cap / manifold material": "Fluid Caps / Manifold Material",
    "hardware material": "Hardware Material",
    "seat / spacer material": "Seat / Spacer Material",
    "seat material": "Seat / Spacer Material",
    "check material": "Check Material",
    "ball material": "Check Material",
    "diaphragm / o-ring material": "Diaphragm / O-Ring Material",
    "diaphragm material": "Diaphragm / O-Ring Material",

    "revision": "Revision",
    "specialty code 1 (blank if no speciality code)": "Specialty Code 1",
    "specialty code 2 (blank if no speciality code)": "Specialty Code 2",
}

SECTIONS = list(set(SECTION_MAP.values()))
CODE_DESC_REGEX = re.compile(r"^([A-Z0-9]{1,5})\s*-\s*(.+)$")

def clean_line(text):
    return (
        text.replace("((cid:31))", "")
            .replace("(cid:31)", "")
            .replace("\u201d", '"')
            .replace('"', '"')
            .strip()
    )

def is_valid_code_desc(code, desc):
    if not code or not desc:
        return False
    if len(code) > 5:
        return False
    if not re.match(r'^[A-Z0-9]{1,5}$', code):
        return False
    if "page" in desc.lower():
        return False
    if re.search(r'[A-Z0-9]{2,5}-[A-Z0-9]{2,5}', desc):
        return False
    return True  # allow "Revision" as valid

def extract_model_chart(pdf_path):
    chart = {s: [] for s in SECTIONS}
    seen = {s: set() for s in SECTIONS}
    current_section = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[1:5]:
            text = page.extract_text()
            if not text:
                continue

            for line in text.splitlines():
                line = clean_line(line)
                key = line.lower().strip()

                # Detect section changes
                for k, v in SECTION_MAP.items():
                    if k in key:  # partial match for robust detection
                        current_section = v
                        break

                # Special handling inside Revision
                if current_section == "Revision":
                    if "specialty code 1" in key:
                        current_section = "Specialty Code 1"
                        continue
                    elif "specialty code 2" in key:
                        current_section = "Specialty Code 2"
                        continue

                if not current_section:
                    continue

                # Extract code-description pairs
                m = CODE_DESC_REGEX.match(line)
                if m:
                    code, desc = m.groups()
                    if is_valid_code_desc(code, desc):
                        if code not in seen[current_section]:
                            chart[current_section].append({
                                "code": code.strip(),
                                "description": desc.strip()
                            })
                            seen[current_section].add(code)

    return chart

