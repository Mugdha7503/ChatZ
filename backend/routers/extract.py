from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import PyPDF2

router = APIRouter(prefix="/extract", tags=["Extract"])

UPLOAD_DIR = "uploaded_pdfs"
EXTRACT_DIR = "extracted_text"
os.makedirs(EXTRACT_DIR, exist_ok=True)

@router.get("/{file_id}")
async def extract_pdf_text(file_id: str):
    pdf_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")

    # 1️⃣ Validate file exists
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="File not found")

    extracted_path = os.path.join(EXTRACT_DIR, f"{file_id}.txt")

    # 2️⃣ Extract text using PyPDF2
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            if len(reader.pages) == 0:
                raise HTTPException(status_code=400, detail="PDF has no pages")

            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() or ""

    except PyPDF2.errors.PdfReadError:
        raise HTTPException(status_code=400, detail="PDF is encrypted or unreadable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

    # 3️⃣ Save the extracted text
    with open(extracted_path, "w", encoding="utf-8") as out:
        out.write(extracted_text)

    # 4️⃣ Return success response
    return JSONResponse(
        content={
            "message": "Text extracted successfully",
            "file_id": file_id,
            "text_file": f"{file_id}.txt",
            "text_length": len(extracted_text),
        }
    )
