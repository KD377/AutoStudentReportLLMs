import chromaManager as db
import FileReader as fr
import chromadb
from chromadb.utils import embedding_functions
import openai

CHROMA_DATA_PATH = "chroma_data"
EMBED_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2"
COLLECTION_NAME = "demo_docs"


section_start_pattern = (
    "Title:",
    "1. Experiment aim:",
    "2. Theoretical background:",
    "3. Research:",
    "4. Conclusions:"
)

path = "./reports/reportsC/expC_no2.docx"


#documents, metadatas = fr.read_file(path, section_start_pattern,3)


# db.build_chroma_collection(
#     CHROMA_DATA_PATH,
#     COLLECTION_NAME,
#     EMBED_MODEL,
#     documents,
#     metadatas
# )

client = chromadb.PersistentClient(CHROMA_DATA_PATH)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_func)

great_reviews = collection.query(
    query_texts=["Find me something how file permissions works on Linux"],
    n_results=5,
    include=["documents", "distances", "metadatas"]
)

print(great_reviews["documents"])

