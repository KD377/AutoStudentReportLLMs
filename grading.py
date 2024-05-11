import os
import shutil

import DocumentsRepository as repository
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
import FileReader as fr
from groqmodel import GROQModel


def grade():
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
        report = model.generate_report(file_id, aim_tb_completion, tasks_completion, number_of_tasks,
                                       repo.get_author(file_id))
        file_id += 1


def delete_collection():
    directory_path = "./chroma_data"
    try:
        shutil.rmtree(directory_path)
        print("Directory removed successfully")
    except OSError as e:
        print(f"Error: {directory_path} : {e.strerror}")
