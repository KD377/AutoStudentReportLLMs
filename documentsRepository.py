import chromadb


class DocumentsRepository:
    def __init__(self, collection):
        self.collection = collection

    def get_title(self, report_id):
        title = self.collection.query(
            query_texts=["What is the title?"],
            n_results=1,
            where={"$and": [
                {"Section_name": {"$eq": "Title:"}},
                {"Global_sentence_number": {"$eq": report_id}}
            ]},
            include=["documents"]
        )
        return title["documents"][0][0][len("Title: "):]

    def get_author(self, report_id):
        author = self.collection.query(
            query_texts=["Who is the author?"],
            n_results=1,
            where={"Global_sentence_number": {"$eq": report_id}},
            include=["documents"]
        )
        return author["documents"][0][0][len("Author "):].strip()

    def get_task_answer(self, report_id, task_number):
        task = self.collection.get(
            where={"$and": [
                {"Exercise_number": {"$eq": task_number}},
                {"Type": {"$eq": "answer"}},
                {"Global_sentence_number": {"$eq": report_id}}
            ]}
        )

        return ",".join(task["documents"])

    def get_task_description(self, report_id, task_number):
        task = self.collection.get(
            where={"$and": [
                {"Exercise_number": {"$eq": task_number}},
                {"Type": {"$eq": "description"}},
                {"Global_sentence_number": {"$eq": report_id}}
            ]}
        )

        return ",".join(task["documents"])

    def get_experiment_aim(self, report_id):
        aim = self.collection.get(
            where={"$and": [
                {"Section_name": {"$eq": "1. Experiment aim:"}},
                {"Type": {"$eq": "answer"}},
                {"Global_sentence_number": {"$eq": report_id}}
            ]}
        )

        return ",".join(aim["documents"])

    def get_theoretical_background(self, report_id):
        background = self.collection.get(
            where={"$and": [
                {"Section_name": {"$eq": "2. Theoretical background:"}},
                {"Type": {"$eq": "answer"}},
                {"Global_sentence_number": {"$eq": report_id}}
            ]}
        )

        return ",".join(background["documents"])

    def get_conclusions(self, report_id):
        conclusions = self.collection.get(
            where={"$and": [
                {"Section_name": {"$eq": "4. Conclusions:"}},
                {"Type": {"$eq": "answer"}},
                {"Global_sentence_number": {"$eq": report_id}}
            ]}
        )

        return ",".join(conclusions["documents"])
