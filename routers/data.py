from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from database import get_collection

import csv
import io

router = APIRouter()

# --- EXISTING ---
@router.get("/sources")
def list_sources(collection: str = "DataPage"):
    col = get_collection(collection)
    sources = col.distinct("Source")
    return {"sources": sources}

@router.get("/data/{source}", operation_id="get_source_data")
def get_data(source: str, collection: str = "DataPage", limit: int = 100):
    col = get_collection(collection)
    docs = list(col.find({"Source": source}).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
    return docs

@router.get("/data/{source}/download", operation_id="download_source_data")
def download_csv(source: str, collection: str = "DataPage"):
    col = get_collection(collection)
    docs = list(col.find({"Source": source}).limit(100))
    if not docs:
        raise HTTPException(status_code=404, detail="No data found.")

    for d in docs:
        d["_id"] = str(d["_id"])

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=docs[0].keys())
    writer.writeheader()
    writer.writerows(docs)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={source}.csv"}
    )

# --- ✅ NEW: Support for /data/preview?key=xxx ---
@router.get("/data/{source}")
def get_data(source: str, collection: str = "DataPage", limit: int = 100):
    col = get_collection(collection)
    docs = list(col.find({"Source": source}).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])

    if not docs:
        raise HTTPException(status_code=404, detail="No data found.")

    # Infer column names/types from the first row
    first = docs[0]
    columns = [
        {"name": k, "type": type(v).__name__}
        for k, v in first.items()
        if k not in ("_id", "Source")
    ]

    # Prepare rows as flat dicts (strip out _id and Source)
    rows = [
        {k: v for k, v in doc.items() if k not in ("_id", "Source")}
        for doc in docs
    ]

    return {
        "view": source,
        "columns": columns,
        "rows": rows,
    }
