from groq import Groq


class GROQModel:

    def __init__(self, api_key, prompt_directory):
        self.api_key = api_key
        self.prompt_directory = prompt_directory
        self.client = Groq(api_key=api_key)

    def generate_grading_requirements(self, documents, metadata, title, number_of_tasks):
        with open(self.prompt_directory+"/requirements", "r") as file:
            context = file.read()

        tasks = self.extract_tasks(documents, metadata, number_of_tasks)

        for i in range(number_of_tasks):
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": context.format(title, tasks["Exercise_" + str(i + 1)])},
                    {"role": "user", "content": "Generate a grading requirement along with the specified schema"}
                ],
                model="mixtral-8x7b-32768",
            )

            criteria = chat_completion.choices[0].message.content
            self.save_criteria(criteria, str(i + 1))

    def save_criteria(self, criteria, exercise_number):
        file_path = self.prompt_directory + "/criteria_ex" + str(exercise_number)
        with open(file_path, "w") as file:
            file.write(criteria)

    def extract_tasks(self, documents, metadata, number_of_tasks):
        tasks = {}
        for i in range(number_of_tasks):
            task = []
            for sentence, data in zip(documents, metadata):
                if (data["Section_name"] == "3. Research:" and data["Exercise_number"] == i + 1 and
                        data["Type"] == "description"):
                    task.append(sentence)
            tasks["Exercise_" + str(i + 1)] = ",".join(task)
        return tasks

    def read_criteria(self, number):
        with open(self.prompt_directory + "/criteria_ex" + str(number + 1), "r") as file:
            context = file.read()
        return context

    def save_query(self, query, number):
        file_path = self.prompt_directory + "/query_ex" + number
        with open(file_path, "w") as file:
            file.write(query)

    def generate_queries(self, documents, metadata, number_of_tasks):
        tasks = self.extract_tasks(documents, metadata, number_of_tasks)

        for i in range(number_of_tasks):
            criteria = self.read_criteria(i)
            task_description = tasks[f"Exercise_{i + 1}"]

            prompt = f"Generate a query to find documents satisfying the following criteria for the task: '{task_description}' based on the criteria: '{criteria}'"

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Please provide a query based on the criteria."}
                ],
                model="mixtral-8x7b-32768",  # Dostosuj do modelu dostępnego w Groq
            )

            query = chat_completion.choices[0].message.content
            self.save_query(query, str(i + 1))

    def create_completion(self, context, task, criteria, answers):
        prompt = context.format(task, criteria, answers)
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please evaluate the answer based on the criteria above."}
            ],
            model="mixtral-8x7b-32768",
        )
        return chat_completion.choices[0].message.content

