import chromadb


class DocumentsRepository:
    def __init__(self, collection):
        self.collection = collection

    def get_title(self):
        title = self.collection.query(
            query_texts=["What is the title?"],
            n_results=1,
            where={"Section_name": {"$eq": "Title:"}},
            include=["documents"]
        )
        return title["documents"][0][0][len("Title: "):]

    def get_author(self):
        author = self.collection.query(
            query_texts=["Who is the author?"],
            n_results=1,
            include=["documents"]
        )
        return author["documents"][0][0][len("Author "):].strip()

    def get_task_answer(self, task_number):
        task = self.collection.get(
            where={"$and": [
                {"Exercise_number": {"$eq": task_number}},
                {"Type": {"$eq": "answer"}}
            ]}
        )

        return ",".join(task["documents"])


    def get_task_description(self, task_number):
        task = self.collection.get(
            where={"$and": [
                {"Exercise_number": {"$eq": task_number}},
                {"Type": {"$eq": "description"}}
            ]}
        )

        return ",".join(task["documents"])

    def get_experiment_aim(self):
        aim = self.collection.get(
            where={"$and": [
                {"Section_name": {"$eq": "1. Experiment aim:"}},
                {"Type": {"$eq": "answer"}}
            ]}
        )

        return ",".join(aim["documents"])

    def get_theoretical_background(self):
        background = self.collection.get(
            where={"$and": [
                {"Section_name": {"$eq": "2. Theoretical background:"}},
                {"Type": {"$eq": "answer"}}
            ]}
        )

        return ",".join(background["documents"])


    def get_conclusions(self):
        conclusions = self.collection.get(
            where={"$and": [
                {"Section_name": {"$eq": "4. Conclusions:"}},
                {"Type": {"$eq": "answer"}}
            ]}
        )

        return ",".join(conclusions["documents"])