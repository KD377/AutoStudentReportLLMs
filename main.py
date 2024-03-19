import chromadb
from chromadb.utils import embedding_functions
import FileReader as fr
# import nltk
# from nltk import sent_tokenize
#
# nltk.download("punkt")

CHROMA_DATA_PATH = "chroma_data/"
EMBED_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2"
COLLECTION_NAME = "demo_docs"

# Only for tests in the future we want
# PersistentClient() to write data to DATA_PATH :)
client = chromadb.Client()

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBED_MODEL
)

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


fr.read_file(path, section_start_pattern)

# collection.add(
#     documents=documents,
#     ids=[f"id{i}" for i in range(len(documents))],
#     metadatas=[{"section": s} for s in section_names]
# )
#
# query_results = collection.query(
#     query_texts=["Tell me about logs"],
#     where={"section": {"$eq": "3. Research:"}},
#     n_results=2,
# )
#
# print(query_results)
