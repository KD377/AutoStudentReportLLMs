import json
import os
import shutil
import re

import DocumentsRepository as repository
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import FileReader as fr
from database import add_grade
from groqmodel import GROQModel


def grade(title_id):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    CHROMA_DATA_PATH = "chroma_data"
    EMBED_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    COLLECTION_NAME = "collection_reports"
    folder_path = "./reports/reportsC/"
    section_start_pattern = (
        "Author:",
        "Title:",
        "1. Experiment aim:",
        "2. Theoretical background:",
        "3. Research:",
        "4. Conclusions:"
    )
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    all_documents, all_metadatas = fr.read_all_files(folder_path, section_start_pattern, 3)
    client = chromadb.PersistentClient(CHROMA_DATA_PATH)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_func)
    try:
        for i, (document, metadata) in enumerate(zip(all_documents, all_metadatas)):
            collection.add(
                ids=[f"file{i}_doc{j}" for j in range(len(document))],
                documents=document,
                metadatas=metadata,
            )
        print("All documents and their metadata added successfully.")
    except Exception as e:
        print("Error adding documents and metadata:", e)

    repo = repository.DocumentsRepository(collection)
    model = GROQModel(api_key, "./prompting", repo)

    for file_id in range(len(all_documents)):
        number_of_tasks = 3
        tasks_completion = model.grade_tasks(file_id)
        aim_tb_completion = model.grade_aim_and_tb(file_id)
        report, author_id = model.generate_report(file_id, aim_tb_completion, tasks_completion, number_of_tasks,
                                                  repo.get_author(file_id))
        summary = model.generate_summary(report, author_id)
        total_points, max_total_points, final_grade = count_points("./prompting/reports/", author_id)
        doc = fr.read_docx_file(f"{folder_path}report_{title_id}_{author_id}.docx")
        add_grade(title_id, total_points, max_total_points, final_grade, author_id, report, summary, doc)
        file_id += 1


def delete_collection():
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    directory_path = "./chroma_data"
    try:
        shutil.rmtree(directory_path)
        print("Directory removed successfully")
    except OSError as e:
        print(f"Error: {directory_path} : {e.strerror}")


def generate_grading_criteria(title_id):
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    CHROMA_DATA_PATH = "chroma_data"
    EMBED_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2"
    COLLECTION_NAME = "collection_reports"
    folder_path = "./reports/reportsC/"
    section_start_pattern = (
        "Author:",
        "Title:",
        "1. Experiment aim:",
        "2. Theoretical background:",
        "3. Research:",
        "4. Conclusions:"
    )
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

    all_documents, all_metadatas = fr.read_all_files(folder_path, section_start_pattern, 3)
    client = chromadb.PersistentClient(CHROMA_DATA_PATH)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_func)
    try:
        for i, (document, metadata) in enumerate(zip(all_documents, all_metadatas)):
            collection.add(
                ids=[f"file{i}_doc{j}" for j in range(len(document))],
                documents=document,
                metadatas=metadata,
            )
        print("All documents and their metadata added successfully.")
    except Exception as e:
        print("Error adding documents and metadata:", e)

    repo = repository.DocumentsRepository(collection)
    model = GROQModel(api_key, "./prompting", repo)
    title = repo.get_title(0)
    ex1 = repo.get_task_description(0, 1)
    ex2 = repo.get_task_description(0, 2)
    ex3 = repo.get_task_description(0, 3)

    aim_criteria = model.generate_criteria(title, "Experiment aim", ex1, ex2, ex3)
    background_criteria = model.generate_criteria(title, "Theoretical background", ex1, ex2, ex3)
    exercise1_criteria = model.generate_grading_criteria(title, 1, 0)["Exercise_1"]
    exercise2_criteria = model.generate_grading_criteria(title, 2, 0)["Exercise_2"]
    exercise3_criteria = model.generate_grading_criteria(title, 3, 0)["Exercise_3"]
    conclusions_criteria = model.generate_criteria(title, "Conclusions", ex1, ex2, ex3)

    return {
        "aim": aim_criteria,
        "background": background_criteria,
        "exercise1": exercise1_criteria,
        "exercise2": exercise2_criteria,
        "exercise3": exercise3_criteria,
        "conclusions": conclusions_criteria
    }


def count_points(folder_path, author_id):
    files = os.listdir(folder_path)
    target_file = None
    for file in files:
        if file.endswith('.json') and author_id in file:
            target_file = file
            break

    if target_file is None:
        print(f"File with author id: {author_id} do not exist in {folder_path}")
        return

    file_path = os.path.join(folder_path, target_file)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    points = []
    for section in data.values():
        points.append(section["Grades"]['points'])

    points = [max(0, min(point, 5)) for point in points]
    total_points = sum(points)
    final_grade = round(total_points / len(points), 1)
    max_total_points = len(points) * 5
    return total_points, max_total_points, final_grade



def Find_First_In_File(title_id, katalog):
    wzorzec = f"report_{title_id}_\d+\.docx"

    # Przejście przez wszystkie pliki w katalogu
    for plik in os.listdir(katalog):
        if re.match(wzorzec, plik):
            return os.path.join(katalog, plik)

    return None