from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import uuid
import os
import fitz
from datetime import datetime

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    # 1. Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # 2. Create unique file id
    file_id = str(uuid.uuid4())

    # 3. Save file
    file_path = f"{UPLOAD_DIR}/{file_id}.pdf"
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error saving PDF file")
    
    # 4. Extract PDF metadata
    try:
        pdf = fitz.open(file_path)
        num_pages = pdf.page_count
        pdf.close()
    except Exception:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Invalid PDF or corrupted file")
    
    # 5. Create metadata object
    metadata = {
        "file_id": file_id,
        "file_name": file.filename,
        "file_size": os.path.getsize(file_path),
        "num_pages": num_pages,
        "uploaded_at": datetime.utcnow().isoformat()
    }

    # TODO: Save metadata to your DB (Mongo/MySQL/Postgres)

    # 6. Return response
    return JSONResponse(
        content={
            "message": "PDF uploaded successfully",
            "file_id": file_id,
            "metadata": metadata
        }
    )
