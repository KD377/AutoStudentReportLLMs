from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from docx import Document
from FileReader import extract_title
from database import get_title_id, add_title
import os
import time

from grading import grade, delete_collection

router = APIRouter()


def read_docx(file: UploadFile) -> list:
    file.file.seek(0)
    document = Document(file.file)
    return document.paragraphs


@router.get("/")
def read_root():
    return {"message": "Hello, World!"}


UPLOAD_FOLDER = "reports/reportsC/"


@router.post("/reports/upload")
async def upload_reports(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    invalid_files = [file.filename for file in files if not file.filename.lower().endswith('.docx')]
    if invalid_files:
        raise HTTPException(status_code=400,
                            detail=f"Invalid file extension for: {', '.join(invalid_files)}. Only .docx files are "
                                   f"allowed.")

    title, contents = await extract_title(files)
    if get_title_id(title.strip()) is None:
        add_title(title.strip())

    i = 0
    title_id = get_title_id(title.strip())
    for content in contents:
        file_name = f"report_{title_id}_{i}.docx"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(file_path, "wb") as f:
            f.write(content)
        i += 1

    return {"message": f"Successfully uploaded {len(files)} files"}


@router.post("/reports/topic/{topic_id}/rate")
async def report_topic_rate(topic_id):
    delete_collection()
    time.sleep(0.3)
    grade()
    return {"message": f"All files graded"}