from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import uuid, os, logging, fitz
from datetime import datetime

from backend.database import SessionLocal
from backend.models import FileInfo

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = logging.getLogger("UploadRouter")

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload_file")
async def upload_pdf(file: UploadFile = File(...)):
    db = SessionLocal()

    file_name = file.filename  # <---- SEARCH BASED ON THIS

    # ✅ 1. Check if file already exists by file_name
    existing_file = db.query(FileInfo).filter(FileInfo.file_name == file_name).first()

    if existing_file:
        return {
            "message": "File already exists",
            "file_id": existing_file.file_id,
            "file_name": existing_file.file_name,
            "embedding_status": existing_file.embedding_status,
            "redirect_to": (
                "query"
                if existing_file.embedding_status
                else "extract"
            )
        }

    # ---------- File does NOT exist → upload normally ---------- #

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # Save file
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(400, "Empty PDF uploaded")

    with open(file_path, "wb") as f:
        f.write(contents)

    # Extract metadata safely
    pdf = fitz.open(file_path)
    num_pages = pdf.page_count
    pdf.close()

    # Save record into DB
    new_entry = FileInfo(
        file_id=file_id,
        file_name=file_name,
        embedding_status=False  # default
    )
    db.add(new_entry)
    db.commit()

    return {
        "message": "PDF uploaded successfully",
        "file_id": file_id,
        "file_name": file_name,
        "embedding_status": False,
        "redirect_to": "extract"
    }

# from fastapi import UploadFile, File, HTTPException, APIRouter
# from fastapi.responses import JSONResponse
# import uuid
# import os
# import logging
# import fitz  # PyMuPDF
# from fitz import FileDataError
# from datetime import datetime

# router = APIRouter(prefix="/upload", tags=["Upload"])
# logger = logging.getLogger("UploadRouter")
# UPLOAD_DIR = "uploaded_pdfs"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# @router.post("/upload_file")
# async def upload_pdf(file: UploadFile = File(...)):
#     logger.info(f"📥 Upload request received: filename={file.filename}, type={file.content_type}")
#     # 1️⃣ Optional: warn if content_type is not PDF
#     if file.content_type != "application/pdf":
#         logger.warning(f"⚠️ Non-PDF uploaded: {file.filename}")
#         # print(f"Warning: uploaded file content_type={file.content_type}")

#     # 2️⃣ Create unique file ID
#     file_id = str(uuid.uuid4())
#     file_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

#     # 3️⃣ Save file
#     try:
#         contents = await file.read()
#         if len(contents) == 0:
#             logger.error("❌ Empty PDF uploaded")
#             raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

#         with open(file_path, "wb") as f:
#             f.write(contents)
#         logger.info(f"📄 PDF saved: {file_path}")
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.exception("❌ Failed to save uploaded PDF")
#         raise HTTPException(status_code=500, detail=f"Error saving PDF file: {e}")

#     # 4️⃣ Extract PDF metadata safely
#     try:
#         pdf = fitz.open(file_path)  # ✅ correct usage
#         num_pages = pdf.page_count
#         pdf.close()
#         logger.info(f"📚 PDF metadata extracted: pages={num_pages}")
#     except fitz.FileDataError:
#         os.remove(file_path)
#         raise HTTPException(status_code=400, detail="PDF file is corrupted or empty")
#     except RuntimeError:
#         os.remove(file_path)
#         raise HTTPException(status_code=400, detail="Unable to process PDF (may be encrypted)")
#     except Exception as e:
#         logger.error(f"❌ Invalid PDF uploaded, deleting file. Reason: {e}")
#         os.remove(file_path)
#         raise HTTPException(status_code=400, detail=f"Invalid PDF file: {e}")

#     # 5️⃣ Create metadata object
#     metadata = {
#         "file_id": file_id,
#         "file_name": file.filename,
#         "file_size": os.path.getsize(file_path),
#         "num_pages": num_pages,
#         "uploaded_at": datetime.utcnow().isoformat()
#     }

#     logger.info(f"✅ Upload success: file_id={file_id}")

   
#     # TODO: Save metadata to your DB (Mongo/MySQL/Postgres)

#     # 6️⃣ Return response
#     return JSONResponse(
#         content={
#             "message": "PDF uploaded successfully",
#             "file_id": file_id,
#             "metadata": metadata
#         }
#     )





