from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
import shutil
import uuid
import json
from datetime import datetime

from iopp_classifier import classify
from iopp_extractor import extract_sections

app = FastAPI(title="Document Classifier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

RECORDS_FILE = Path("records.json")
if not RECORDS_FILE.exists():
    RECORDS_FILE.write_text("[]")


def load_records() -> list:
    return json.loads(RECORDS_FILE.read_text())


def save_records(records: list):
    RECORDS_FILE.write_text(json.dumps(records, indent=2))


@app.get("/")
def home():
    return {"message": "Document Classifier API is running"}


@app.get("/app")
def serve_frontend():
    return FileResponse("index.html")


@app.get("/records")
def get_records():
    return load_records()


@app.delete("/records/{record_id}")
def delete_record(record_id: str):
    records = load_records()
    record = next((r for r in records if r["id"] == record_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    file_path = UPLOAD_DIR / record_id
    if file_path.exists():
        file_path.unlink()
    records = [r for r in records if r["id"] != record_id]
    save_records(records)
    return {"deleted": record_id}


@app.post("/classify")
async def classify_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / unique_name

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = classify(file_path, file.filename)

        record = {
            "id":            unique_name,
            "filename":      file.filename,
            "document_type": result["document_type"],
            "reason":        result["reason"],
            "tier":          result["tier"],
            "uploaded_at":   datetime.now().strftime("%Y-%m-%d %H:%M"),
            "size_bytes":    file_path.stat().st_size,
            "extracted":     None,  # will be filled on first view
        }

        records = load_records()
        records.insert(0, record)
        save_records(records)
        return record

    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
    finally:
        file.file.close()


@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    unique_name = f"{uuid.uuid4()}.pdf"
    file_path = UPLOAD_DIR / unique_name

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        result = extract_sections(file_path)
        return result
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        file_path.unlink(missing_ok=True)
        file.file.close()


@app.get("/extract-saved/{record_id}")
def extract_saved(record_id: str):
    """
    Returns saved extraction data for a record.
    If not yet extracted, extracts from the stored PDF, saves it, and returns it.
    """
    records = load_records()
    record = next((r for r in records if r["id"] == record_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")

    # Return cached extraction if already done
    if record.get("extracted"):
        return record["extracted"]

    # Extract from stored PDF
    file_path = UPLOAD_DIR / record_id
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found.")

    try:
        result = extract_sections(file_path)
        # Save back to records
        for r in records:
            if r["id"] == record_id:
                r["extracted"] = result
                break
        save_records(records)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")