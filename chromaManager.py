import chromadb
from chromadb.utils import embedding_functions


def build_chroma_collection(
    chroma_path: str,
    collection_name: str,
    embedding_func_name: str,
    documents: list[str],
    metadatas: list[dict],
    distance_func_name: str = "cosine",
):

    chroma_client = chromadb.PersistentClient(chroma_path)

    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=embedding_func_name
    )

    collection = chroma_client.create_collection(
        name=collection_name,
        embedding_function=embedding_func,
        metadata={"hnsw:space": distance_func_name},
    )

    collection.add(
        ids=[f"id{i}" for i in range(len(documents))],
        documents=documents,
        metadatas=metadatas,
    )