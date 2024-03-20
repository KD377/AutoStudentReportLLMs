import chromaManager as db
import FileReader as fr
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

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

#UNCOMMENT THIS SECTION IF RUNNING FOR THE FIRST TIME
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

query = collection.query(
    query_texts=["What chmod commands did you use to set the specified permissions?"],
    n_results=8,
    where={"Exercise_number":{"$eq": 1}},
    include=["documents", "metadatas"]
)

answers = ",".join(query["documents"][0])

context = """
You are a lecturer on a University of technology and you need to grade the students' report.
I will send you the question the students had to answer and you will have to grade if the answer is correct
on the scale from 1-3. I will also provide you with the student's answer to the question.
Task: {}
Student's answer: {}
"""

question = "Task: What chmod commands did you use to set the specified permissions?"


client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

completion = client.chat.completions.create(
  model="local-model",
  messages=[
    {"role": "system", "content": context.format(question, answers)},
    {"role": "user", "content": "How would you grade that?"}
  ],
  temperature=0.7,
)

print(completion.choices[0].message)

