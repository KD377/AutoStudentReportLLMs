from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from typing import List
from docx import Document
from FileReader import extract_title, extract_author
from database import get_title_id, add_title
import os
import json
import re
import time
from grading import delete_collection, grade, generate_grading_criteria

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
    author_ids = extract_author(contents)
    if get_title_id(title.strip()) is None:
        add_title(title.strip())

    i = 0
    title_id = get_title_id(title.strip())
    for content in contents:
        file_name = f"report_{title_id}_{author_ids[i]}.docx"
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(file_path, "wb") as f:
            f.write(content)
        i += 1

    return {"message": f"Successfully uploaded {len(files)} files", "title": title}


REPORTS_FOLDER = "prompting/reports/"
SUMMARY_FOLDER = "prompting/summary/"


def extract_index_number(file_name):
    match = re.search(r'_(\d+)_report\.json$', file_name)
    if match:
        return match.group(1)
    return None


@router.post("/reports/topic/{topic_id}/rate")
async def report_topic_rate(topic_id):
    delete_collection()
    time.sleep(3)
    grade(topic_id)

    grades = []
    index_number = None

    for file_name in os.listdir(REPORTS_FOLDER):
        if file_name.endswith('.json'):
            file_path = os.path.join(REPORTS_FOLDER, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                grades.append(data)
                index_number = extract_index_number(file_name)

    if not grades:
        raise HTTPException(status_code=404, detail="No grades found")

    if not index_number:
        raise HTTPException(status_code=404, detail="Index number not found in report filenames")

    summary_file_path = os.path.join(SUMMARY_FOLDER, f"report_{index_number}.txt")
    if not os.path.exists(summary_file_path):
        raise HTTPException(status_code=404, detail="Summary file not found")

    with open(summary_file_path, 'r', encoding='utf-8') as file:
        summary = file.read()

    print(grades)
    return {"grades": grades, "summary": summary}


@router.post("/criteria/topic/{topic_id}/generate")
async def generate_criteria(topic_id):
    aim_criteria, background_criteria, research_criteria,  conclusions_criteria = generate_grading_criteria(topic_id)

    return {
        "message": "Created grading",
        "criteria": {
            "aim": aim_criteria,
            "background": background_criteria,
            "research": research_criteria,
            "conclusions": conclusions_criteria
        }
    }


CRITERIA_FOLDER = "./prompting/generating/"


@router.post("/criteria/update")
async def update_criteria(request: Request):
    data = await request.json()

    try:
        with open(os.path.join(CRITERIA_FOLDER, "criteria_aim"), "w") as file:
            file.write(data.get("aim", ""))

        with open(os.path.join(CRITERIA_FOLDER, "criteria_tb"), "w") as file:
            file.write(data.get("background", ""))

        with open(os.path.join(CRITERIA_FOLDER, "criteria_ex1"), "w") as file:
            file.write(data.get("research", ""))

        with open(os.path.join(CRITERIA_FOLDER, "criteria_conclusion"), "w") as file:
            file.write(data.get("conclusions", ""))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating criteria: {e}")

    return {"message": "Criteria updated successfully"}