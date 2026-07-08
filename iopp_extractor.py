import re
import pdfplumber
from pathlib import Path


def extract_sections(pdf_path: str | Path) -> dict:
    pdf_path = Path(pdf_path)
    full_text_lines: list[str] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            full_text_lines.extend(text.splitlines())

    full_text = "\n".join(full_text_lines)

    def get_between(start_pat, end_pat):
        m_start = re.search(start_pat, full_text, re.IGNORECASE)
        m_end   = re.search(end_pat,   full_text, re.IGNORECASE)
        if not m_start:
            return ""
        end_pos = m_end.start() if m_end and m_end.start() > m_start.start() else len(full_text)
        return full_text[m_start.start():end_pos]

    # Use full sentence anchors to avoid matching 2.3.1, 2.3.2, 2.3.3
    sec31 = get_between(
        r'3\.1\. The ship is provided with oil residue',
        r'3\.2\. Means for the disposal'
    )
    sec32 = get_between(
        r'3\.2\. Means for the disposal',
        r'3\.3\. The ship is provided with holding'
    )
    sec33 = get_between(
        r'3\.3\. The ship is provided with holding',
        r'4\. STANDARD DISCHARGE'
    )

    def parse_tanks(section_text):
        tanks = []
        lines = [l.strip() for l in section_text.splitlines()]
        data_re = re.compile(r'^(.*?)([\d.]+)\s*[-–]\s*([\d.]+)\s+([PCSpcs])\s+([\d.]+)\s*$')
        skip_words = {'tank identification', 'frames', 'lateral position',
                      'tank location', 'total volume', 'volume (m'}

        i = 0
        while i < len(lines):
            line = lines[i]
            if not line:
                i += 1
                continue
            if any(s in line.lower() for s in skip_words):
                i += 1
                continue
            if re.match(r'^3\.\d', line):
                i += 1
                continue

            m = data_re.match(line)
            if m:
                name = m.group(1).strip()
                if not name:
                    for j in range(i - 1, -1, -1):
                        prev = lines[j].strip()
                        if prev and not re.search(r'\d', prev) and not any(s in prev.lower() for s in skip_words):
                            name = prev
                            break
                # Check next line for suffix like "Ser"
                if i + 1 < len(lines):
                    nxt = lines[i + 1].strip()
                    if (nxt and not re.search(r'[\d\[\]]', nxt)
                            and not any(s in nxt.lower() for s in skip_words)
                            and not re.match(r'^3\.\d', nxt)
                            and len(nxt) < 20):
                        name = (name + " " + nxt).strip()
                        i += 1

                if name:
                    tanks.append({
                        "tank_identification": name,
                        "frames_from":        m.group(2),
                        "frames_to":          m.group(3),
                        "lateral_position":   m.group(4).upper(),
                        "volume_m3":          float(m.group(5)),
                    })
            i += 1
        return tanks

    def get_total(section_text):
        m = re.search(r'total volume[^:]*:\s*([\d.]+)', section_text, re.IGNORECASE)
        return float(m.group(1)) if m else None

    # Section 3.2 disposal means
    incinerator = bool(re.search(r'\[X\]\s*3\.2\.1', sec32))
    aux_boiler  = bool(re.search(r'\[X\]\s*3\.2\.2', sec32))
    other_means = bool(re.search(r'\[X\]\s*3\.2\.3', sec32))

    other_desc = ""
    lines32 = sec32.splitlines()
    for i, line in enumerate(lines32):
        if re.search(r'3\.2\.3|other acceptable', line, re.IGNORECASE):
            for l in lines32[i + 1:]:
                l = l.strip()
                if l and not re.match(r'\[', l) and not re.match(r'3\.\d', l):
                    other_desc = l
                    break
            break

    return {
        "section_3_1_sludge_tanks": {
            "description": "Oil residue (sludge) tanks for retention of oil residues on board",
            "tanks":           parse_tanks(sec31),
            "total_volume_m3": get_total(sec31),
        },
        "section_3_2_disposal_means": {
            "description":             "Means for disposal of oil residues (sludge)",
            "incinerator_for_sludge":  incinerator,
            "auxiliary_boiler":        aux_boiler,
            "other_acceptable_means":  other_means,
            "other_means_description": other_desc,
        },
        "section_3_3_bilge_water_holding_tanks": {
            "description": "Holding tanks for the retention on board of oily bilge water",
            "tanks":           parse_tanks(sec33),
            "total_volume_m3": get_total(sec33),
        },
    }