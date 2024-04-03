from groq import Groq
import json
import re


class GROQModel:

    def __init__(self, api_key, prompt_directory):
        self.api_key = api_key
        self.prompt_directory = prompt_directory
        self.client = Groq(api_key=api_key)

    def generate_grading_requirements(self, documents, metadata, title, number_of_tasks):
        with open(self.prompt_directory + "/requirements", "r") as file:
            context = file.read()

        tasks = self.extract_tasks(documents, metadata, number_of_tasks)

        for i in range(number_of_tasks):
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": context.format(title, tasks["Exercise_" + str(i + 1)])},
                    {"role": "user",
                     "content": "Generate a grading requirement along with the specified schema. Each exercise must be graded within range of 0 to 5 points and must be an enteger. For each genereted requirement, the maximum number of points is 1. Each requirement fullfilment can be only graded with 0 or 1 point."}
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

    # def generate_queries(self, documents, metadata, number_of_tasks):
    #     tasks = self.extract_tasks(documents, metadata, number_of_tasks)
    #
    #     for i in range(number_of_tasks):
    #         criteria = self.read_criteria(i)
    #         task_description = tasks[f"Exercise_{i + 1}"]
    #
    #         prompt = f"Generate a query to find documents satisfying the following criteria for the task: '{task_description}' based on the criteria: '{criteria}'"
    #
    #         chat_completion = self.client.chat.completions.create(
    #             messages=[
    #                 {"role": "system", "content": prompt},
    #                 {"role": "user", "content": "Please provide a query based on the criteria."}
    #             ],
    #             model="mixtral-8x7b-32768",
    #         )
    #
    #         query = chat_completion.choices[0].message.content
    #         self.save_query(query, str(i + 1))

    def generate_queries(self, documents, metadata, number_of_tasks):
        tasks = self.extract_tasks(documents, metadata, number_of_tasks)

        criteria_questions = {}

        for i in range(number_of_tasks):
            criteria = self.read_criteria(i)
            task_description = tasks[f"Exercise_{i + 1}"]

            prompt = f"""
            Please generate questions for querying a vector database, based on the following criteria associated with a given task. The goal is to assess whether the task's criteria have been met.
        
            Each question should correspond to one of the criteria listed below, and should be used to check the completion and understanding of the task. The questions should be formatted as a JSON object with criteria as keys and the questions as a list of strings.
            The number of criterias in output should be equal to the number of criterias in the input.
        
            Output format:
        
            One question in one line for each criteria. Use json format. 
        
            ###
        
            Task Description: 
        
            {task_description}
        
            ###
        
            Grading Criteria:
        
            {criteria}
            
            ###
        
            Expected Output Format:
            {{"NAME OF CRITERION": ["QUESTION 1", "QUESTION 2", ...]}}
            """

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt.strip()},
                    {"role": "user", "content": "Please generate questions in JSON format based on the criteria."}
                ],
                model="mixtral-8x7b-32768",
            )

            generated_questions = chat_completion.choices[0].message.content

            try:
                questions_json = json.loads(generated_questions)
                criteria_questions[i] = questions_json
            except json.JSONDecodeError:
                print(f"Error decoding JSON from response: {generated_questions}")

        with open(f"{self.prompt_directory}/generated_queries.json", "w") as file:
            json.dump(criteria_questions, file, indent=4)

        return criteria_questions

    def extract_json_from_response(self, response):
        json_pattern = r"```json\n([\s\S]*?)\n```"
        match = re.search(json_pattern, response)
        if match:
            return match.group(1)
        return None

    def create_completion(self, context, task, criteria, answers):
        prompt = context.format(task, criteria, answers)
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",
                 "content": "Based on the criteria above, evaluate the answer and provide a final grading in JSON format as follows: {\"points\": \"X\", \"description\": \"Y\"}, where X is the total points awarded and Y is a maximum 2 sentence rationale."}
            ],
            model="mixtral-8x7b-32768",
        )

        response = chat_completion.choices[0].message.content
        json_string = self.extract_json_from_response(response)

        if json_string:
            try:
                response_data = json.loads(json_string)
                final_grade = [response_data]
            except json.JSONDecodeError as e:
                print(f"Error processing the extracted JSON: {e}")
                final_grade = [{"points": 0, "description": "Unable to parse grading rationale from the AI response."}]
        else:
            print(f"No valid JSON found in the AI response: {response}")
            final_grade = [
                {"points": 0, "description": "The AI response did not contain valid JSON grading rationale."}]

        with open(f"{self.prompt_directory}/completion.json", 'w') as file:
            json.dump(final_grade, file, indent=4)

        return final_grade
