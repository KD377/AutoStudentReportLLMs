class DocumentsRepository:
    def __init__(self, collection):
        self.collection = collection

    def get_title(self, file_id):
        title = self.collection.query(
            query_texts=["What is the title?"],
            n_results=1,
            where={"$and": [
                {"File_ID": {"$eq": file_id}},
                {"Section_name": {"$eq": "Title:"}}
            ]},
            include=["documents"]
        )
        if title["documents"]:
            return title["documents"][0][0][len("Title: "):]
        return "Title not found"

    def get_author(self, file_id):
        author = self.collection.query(
            query_texts=["Who is the author?"],
            n_results=1,
            where={"$and": [
                {"File_ID": {"$eq": file_id}},
                {"Section_name": {"$eq": "Author:"}}
            ]},
            include=["documents"]
        )
        if author["documents"]:
            return author["documents"][0][0][len("Author: "):].strip()
        return "Author not found"

    def get_task_answer(self, file_id, task_number):
        task = self.collection.get(
            where={"$and": [
                {"File_ID": {"$eq": file_id}},
                {"Exercise_number": {"$eq": task_number}},
                {"Type": {"$eq": "answer"}}
            ]}
        )
        if task["documents"]:
            return ",".join(task["documents"])
        return "No answer found"

    def get_task_description(self, file_id, task_number):
        task = self.collection.get(
            where={"$and": [
                {"File_ID": {"$eq": file_id}},
                {"Exercise_number": {"$eq": task_number}},
                {"Type": {"$eq": "description"}}
            ]}
        )
        if task["documents"]:
            return ",".join(task["documents"])
        return "No description found"

    def get_experiment_aim(self, file_id):
        aim = self.collection.get(
            where={"$and": [
                {"File_ID": {"$eq": file_id}},
                {"Section_name": {"$eq": "1. Experiment aim:"}},
                {"Type": {"$eq": "answer"}}
            ]}
        )
        if aim["documents"]:
            return ",".join(aim["documents"])
        return "No aim found"

    def get_theoretical_background(self, file_id):
        background = self.collection.get(
            where={"$and": [
                {"File_ID": {"$eq": file_id}},
                {"Section_name": {"$eq": "2. Theoretical background:"}},
                {"Type": {"$eq": "answer"}}
            ]}
        )
        if background["documents"]:
            return ",".join(background["documents"])
        return "No background found"

    def get_conclusions(self, file_id):
        conclusions = self.collection.get(
            where={"$and": [
                {"File_ID": {"$eq": file_id}},
                {"Section_name": {"$eq": "4. Conclusions:"}},
                {"Type": {"$eq": "answer"}}
            ]}
        )
        if conclusions["documents"]:
            return ",".join(conclusions["documents"])
        return "No conclusions found"
