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
                     "content": "Generate grading requirements. Whole exercise must be graded within range of 0 to 5 "
                                "points. You must generate exactly 5 requirements for 1 exercise. For each "
                                "requirement, the maximum number of points is 1, so the total number of points for "
                                "whole exercise is 5. Each requirement fulfillment can be only graded with 0 or 1 "
                                "point. Non integer points like 0.5 etc. are forbidden."}
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
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned_response = re.sub(r'^.*?{', '{', response, flags=re.DOTALL)
            try:
                potential_json = json.loads(cleaned_response)
                return potential_json
            except json.JSONDecodeError:
                json_pattern = r'\{(?:[^{}]|(?R))*\}'
                matches = re.findall(json_pattern, response, re.DOTALL)
                if matches:
                    longest_match = max(matches, key=len)
                    if isinstance(longest_match, str):
                        try:
                            return json.loads(longest_match)
                        except json.JSONDecodeError:
                            pass
        return None

    # def create_completion(self, context, task, criteria, answers):
    #     prompt = context.format(task, criteria, answers)
    #     chat_completion = self.client.chat.completions.create(
    #         messages=[
    #             {"role": "system", "content": prompt},
    #             {"role": "user",
    #              "content": "Based on the criteria above, evaluate the answer and provide a final grading in JSON format as follows: {\"points\": \"X\", \"description\": \"Y\"}, where X is the total points awarded and Y is a maximum 2 sentence rationale. Let your answer be only JSON without any other text"}
    #         ],
    #         model="mixtral-8x7b-32768",
    #     )

    #     response = chat_completion.choices[0].message.content
    #     json_data = self.extract_json_from_response(response)

    #     if json_data:
    #         # Zakładamy, że json_data to słownik
    #         final_grade = [{"points": int(json_data.get("points", 0)), "description": json_data.get("description", "")}]
    #     else:
    #         print("No valid JSON found in the AI response:", response)
    #         final_grade = [
    #             {"points": 0, "description": "The AI response did not contain valid JSON grading rationale."}]

    #     with open(f"{self.prompt_directory}/completion.json", 'w') as file:
    #         json.dump(final_grade, file, indent=4)

    #     return final_grade

    def create_completion(self, context, tasks, criteria, answers):
        completions = []

        for task in tasks:
            prompt = context.format(task, criteria, answers)
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user",
                    "content": "Based on the criteria above, evaluate the answer and provide a final grading in JSON format as follows: {\"points\": \"X\", \"description\": \"Y\"}, where X is the total points awarded and Y is a maximum 2 sentence rationale. Let your answer be only JSON without any other text"}
                ],
                model="mixtral-8x7b-32768",
            )

            response = chat_completion.choices[0].message.content
            json_data = self.extract_json_from_response(response)

            if json_data:
                final_grade = {"points": int(json_data.get("points", 0)), "description": json_data.get("description", "")}
            else:
                print("No valid JSON found in the AI response:", response)
                final_grade = {"points": 0, "description": "The AI response did not contain valid JSON grading rationale."}

            completions.append(final_grade)

        return completions
    
    def generate_report(self,  grades, number_of_tasks):
        report = {}

        for i in range(number_of_tasks):
            report[f"Exercise_{i + 1}"] = {
                "Grades": grades[i],
            }

        with open(f"{self.prompt_directory}/report.json", "w") as file:
            json.dump(report, file, indent=4)

        return report
    