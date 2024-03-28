import chromaManager as db
import FileReader as fr
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from llmmodel import LLMModel

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

path = "./reports/reportsC/expC_no2.docx"

#UNCOMMENT THIS SECTION IF RUNNING FOR THE FIRST TIME
documents, metadatas = fr.read_file(path, section_start_pattern,3)

for i in range(len(documents)):
    if metadatas[i]["Section_name"] == "Title:":
        title = documents[i]

model = LLMModel("http://localhost:1234/v1", "lm-studio","./prompting")
# model.generate_grading_requirements(documents, metadatas,title,3)
#model.generate_queries(documents, metadatas, 3) to nie dziala
# model.generate_grading_requirements(docs, meta, title)
# db.build_chroma_collection(
#     CHROMA_DATA_PATH,
#     COLLECTION_NAME,
#     EMBED_MODEL,
#     documents,
#     metadatas
# )

tasks = model.extract_tasks(documents, metadatas, 3)
task = tasks["Exercise_1"]

client = chromadb.PersistentClient(CHROMA_DATA_PATH)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
collection = client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_func)

query = collection.query(
    query_texts=["Which chmod command was used to set read, write, and execute permissions for the owner and others on 'file1.txt'?"],
    n_results=8,
    where={"$and": [
        {"Exercise_number": {"$eq": 1}},
        {"Type": {"$eq": "answer"}}
    ]},
    include=["documents", "metadatas"]
)

print(query["documents"])
answers = ",".join(query["documents"][0])

with open("./prompting/grading","r") as file:
    context = file.read()

with open("./prompting/criteria_ex1","r") as file:
    criteria = file.read()

# context = """
# You are a lecturer on a University of technology and you need to grade the students' report.
# I will send you the question the students had to answer and you will have to grade if the answer is correct
# on the scale from 1-3. I will also provide you with the student's answer to the question.
# Task: {}
# Student's answer: {}
# """
#
# question = "Task: What chmod commands did you use to set the specified permissions?"
#
#
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
#
completion = client.chat.completions.create(
  model="local-model",
  messages=[
    {"role": "system", "content": context.format(task, criteria, answers)},
    {"role": "user", "content": "Please verify the answers accroding to the given criteria"}
  ],
  temperature=0.7,
)

print(completion.choices[0].message)

