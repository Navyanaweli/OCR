# IOPP Classifier

A tool for classifying and extracting data from maritime PDF documents — specifically IOPP (International Oil Pollution Prevention) Certificate Supplements and Tank Diagram / Capacity Plans.

## Project structure

- **`app.py`, `iopp_classifier.py`, `iopp_extractor.py`** — FastAPI backend. Accepts PDF uploads, classifies document type via text/filename pattern matching (`pdfplumber`), and extracts structured sections. Keeps upload/record state in `uploads/` and `records.json`.
- **`index.html`** — Standalone frontend for the FastAPI backend.
- **`iopp-classifier/`** — Angular frontend (upload, storage, and extract-panel components) that talks to the same API.
- **`IoppClassifier/`** — ASP.NET Core (.NET 8) API alternative, mirroring the classify/records functionality (`ClassifyController`, `PythonClassifierService`, `RecordsService`).
- **`Prototype.png`** — UI prototype/mockup.

## Running the Python backend

```bash
pip install fastapi uvicorn pdfplumber python-multipart
uvicorn app:app --reload
```

Then open `http://localhost:8000/app` (serves `index.html`) or point the Angular app at `http://localhost:8000`.

## Running the Angular frontend

```bash
cd iopp-classifier
npm install
ng serve
```

Navigate to `http://localhost:4200/`. See [iopp-classifier/README.md](iopp-classifier/README.md) for Angular CLI details.

## Running the .NET API

```bash
cd IoppClassifier
dotnet run
```
