import re
import sys
import json
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("Missing dependency. Install it using: pip install pdfplumber")

REG12_PATTERN = re.compile(
    r"3\.1\s+the\s+ship\s+is\s+provided\s+with\s+oil\s+residue",
    re.IGNORECASE,
)

TANK_DIAGRAM_TOKENS = {
    "capacity", "tank", "lcg", "vcg", "tcg", "deadweight", "displacement",
    "frame", "compartment", "volume", "tonnes",
}
TANK_DIAGRAM_THRESHOLD = 3

IOPP_FILENAME_TOKENS = {
    "supplement", "international", "oil", "pollution", "prevention", "certificate",
}
IOPP_WEAK_MATCH_THRESHOLD = 3


class DocumentType:
    IOPP         = "IOPP Certificate Supplement"
    TANK_DIAGRAM = "Tank Diagram / Capacity Plan"
    UNKNOWN      = "Unknown Document"


def extract_text(pdf_path: Path) -> str:
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def matches_reg12(text: str) -> bool:
    return bool(REG12_PATTERN.search(text))


def filename_is_iopp(filename: str) -> bool:
    lower = filename.lower()
    if "iopp" in lower:
        return True
    hit_count = sum(1 for token in IOPP_FILENAME_TOKENS if token in lower)
    return hit_count >= IOPP_WEAK_MATCH_THRESHOLD


def looks_like_tank_diagram(text: str, filename: str) -> bool:
    lower_text = text.lower()
    lower_name = filename.lower()
    if any(t in lower_name for t in ["capacity", "tank", "diagram"]):
        return True
    hits = sum(1 for token in TANK_DIAGRAM_TOKENS if token in lower_text)
    return hits >= TANK_DIAGRAM_THRESHOLD


def classify(pdf_path: str | Path, original_filename: str | None = None) -> dict:
    path = Path(pdf_path).resolve()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {path.suffix}")

    text = extract_text(path)
    display_name = original_filename or path.name

    if matches_reg12(text):
        return {
            "document_type": DocumentType.IOPP,
            "reason": "Regulation-12 declaration sentence found in document text.",
            "tier": "Tier 1 — content scan",
            "path": str(path),
        }

    if filename_is_iopp(display_name):
        strong = "iopp" in display_name.lower()
        return {
            "document_type": DocumentType.IOPP,
            "reason": (
                "Original filename contains 'IOPP' strong match."
                if strong
                else "Original filename contains 3 or more IOPP keyword tokens."
            ),
            "tier": "Tier 2 — filename heuristic",
            "path": str(path),
        }

    if looks_like_tank_diagram(text, display_name):
        return {
            "document_type": DocumentType.TANK_DIAGRAM,
            "reason": "Document contains tank diagram keywords or filename match.",
            "tier": "Tier 3 — content keywords",
            "path": str(path),
        }

    return {
        "document_type": DocumentType.UNKNOWN,
        "reason": "Document does not match IOPP or Tank Diagram patterns. Manual review required.",
        "tier": "Default — unclassified",
        "path": str(path),
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python iopp_classifier.py <path/to/document.pdf> [--json]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    json_output = "--json" in sys.argv
    original_filename = None

    if "--original-name" in sys.argv:
        index = sys.argv.index("--original-name")
        if index + 1 < len(sys.argv):
            original_filename = sys.argv[index + 1]

    try:
        result = classify(pdf_path, original_filename)
        if json_output:
            print(json.dumps(result))
        else:
            print("\n=== Document Classification Result ===")
            print(f"File          : {result['path']}")
            print(f"Document Type : {result['document_type']}")
            print(f"Tier          : {result['tier']}")
            print(f"Reason        : {result['reason']}")
            print("======================================\n")
    except Exception as error:
        if json_output:
            print(json.dumps({"error": str(error)}))
        else:
            print(f"Error: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()