import chromaManager as db
import FileReader as fr
import documentsRepository as repository
import chromadb
from dotenv import load_dotenv
import os
from chromadb.utils import embedding_functions
from groqmodel import GROQModel


CHROMA_DATA_PATH = "chroma_data"
EMBED_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2"
COLLECTION_NAME = "demo_docs"

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

path = "./reports/reportsC/expC_no2.docx"

# Read file and prepare data
documents, metadatas = fr.read_file(path, section_start_pattern,3)
# for i in range(len(documents)):
#     if metadatas[i]["Exercise_number"] == 1:
#         print(documents[i])
# if db does not exist create one
if not os.path.exists(CHROMA_DATA_PATH):
    db.build_chroma_collection(
        CHROMA_DATA_PATH,
        COLLECTION_NAME,
        EMBED_MODEL,
        documents,
        metadatas
    )

client = chromadb.PersistentClient(CHROMA_DATA_PATH)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBED_MODEL
)
collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_func)
# repository class contains different queries
repository = repository.DocumentsRepository(collection)

model = GROQModel(api_key, "./prompting", repository)

# title extraction
title = repository.get_title()
number_of_tasks = 3

# model.generate_grading_criteria(documents, metadatas, title, 3)
# model.generate_aim_criteria(documents, metadatas, title)

completion = model.grade_tasks(3)

report = model.generate_report(completion, 3)

