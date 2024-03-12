import chromadb
from chromadb.utils import embedding_functions
import FileReader as fr
# import nltk
# from nltk import sent_tokenize
#
# nltk.download("punkt")

CHROMA_DATA_PATH = "chroma_data/"
EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "demo_docs"

# Only for tests in the future we want
# PersistentClient() to write data to DATA_PATH :)
client = chromadb.Client()

embedding_func = embedding_functions.DefaultEmbeddingFunction()

collection = client.create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"},
)


section_start_pattern = (
    "Title:",
    "1. Experiment aim:",
    "2. Theoretical background:",
    "3. Research:",
    "4. Conclusions:"
)

path = "./reports/reportsC/expC_no2.docx"


documents, section_names = fr.read_file(path, section_start_pattern)


collection.add(
    documents=documents,
    ids=[f"id{i}" for i in range(len(documents))],
    metadatas=[{"section": s} for s in section_names]
)

query_results = collection.query(
    query_texts=["what is the aim of the report"],
    n_results=2,
)

print(query_results)
