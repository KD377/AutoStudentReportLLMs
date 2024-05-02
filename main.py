import chromaManager as db
import FileReader as fr
import documentsRepository as repository
import chromadb
from dotenv import load_dotenv
import os
from chromadb.utils import embedding_functions
from groqmodel import GROQModel
from database import *

os.environ["TOKENIZERS_PARALLELISM"] = "false"
CHROMA_DATA_PATH = "chroma_data"
EMBED_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2"
COLLECTION_NAME = "reportsC"

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
            ids=[f"file{i}_doc{j}" for j in range(len(document))],  # Adjusted IDs to include file identifier
            documents=document,
            metadatas=metadata,
        )
    print("All documents and their metadata added successfully.")
except Exception as e:
    print("Error adding documents and metadata:", e)


# print("Number of documents read:", len(all_documents))
# print("Number of metadata entries:", len(all_metadatas))
#
# print("Sample document:", all_documents[0])
# print("Sample metadata:", all_metadatas[0])


# repository class contains different queries
repository = repository.DocumentsRepository(collection)
model = GROQModel(api_key, "./prompting", repository)

# title = repository.get_title()
# number_of_tasks = 3
# ex1 = repository.get_task_description(1)
# ex2 = repository.get_task_description(2)
# ex3 = repository.get_task_description(3)
# print(repository.get_task_answer(1))
# # model.generate_grading_criteria(documents, metadatas, title, 3)
# tasks_completion = model.grade_tasks(3)
# aim_tb_completion = model.grade_aim_and_tb()
# # model.generate_criteria(title, "Experiment aim", ex1, ex2, ex3)
# # model.generate_criteria(title, "Theoretical background", ex1, ex2, ex3)
# # model.generate_criteria(title, "Conclusions", ex1, ex2, ex3)
# report = model.generate_report(aim_tb_completion, tasks_completion, 3)


for doc_id in range(len(all_documents)):
    number_of_tasks = 3
    # print(repository.get_author(doc_id))
    # print('BGGGGGGGGGGG', doc_id, repository.get_theoretical_background(doc_id))
    #
    # print('Author:', repository.get_author(doc_id))
    # print("Aim:", repository.get_experiment_aim(doc_id))
    # print("Background:", repository.get_theoretical_background(doc_id))
    # print("Background:", repository.get_conclusions(doc_id))
    tasks_completion = model.grade_tasks(doc_id)
    aim_tb_completion = model.grade_aim_and_tb(doc_id)
    report = model.generate_report(doc_id, aim_tb_completion, tasks_completion, number_of_tasks, repository.get_author(doc_id))

# create_database()
