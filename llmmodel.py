from openai import OpenAI


class LLMModel:

    def __init__(self, url, api_key, prompt_directory):
        self.url = url
        self.api_key = api_key
        self.prompt_directory = prompt_directory
        self.client = OpenAI(base_url=self.url, api_key=self.api_key)

    def generate_grading_requirements(self, documents, metadata, title, number_of_tasks):
        with open(self.prompt_directory+"/requirements", "r") as file:
            context = file.read()

        tasks = self.extract_tasks(documents, metadata, number_of_tasks)

        for i in range(number_of_tasks):

            completion = self.client.chat.completions.create(
              model="local-model",
              messages=[
                {"role": "system", "content": context.format(title, tasks["Exercise_"+str(i + 1)])},
                {"role": "user", "content": "Generate a grading requirement along with the specified schema"}
              ],
              temperature=0.7,
            )

            criteria = completion.choices[0].message.content
            self.save_criteria(criteria, str(i + 1))

    def save_criteria(self, criteria, exercise_number):
        file_path = self.prompt_directory+"/criteria_ex"+str(exercise_number)
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
            tasks["Exercise_"+str(i + 1)] = ",".join(task)
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
            completion = self.client.chat.completions.create(
              model="local-model",
              messages=[
                {"role": "system", "content": criteria.format(tasks["Exercise_"+str(i + 1)],criteria)},
                {"role": "user", "content": "Generate queries in the specified format which will be asked to a vector database in order to check if the requirement is satisfied"}
              ],
              temperature=0.7,
            )

            query = completion.choices[0].message.content
            self.save_query(query, str(i + 1))


