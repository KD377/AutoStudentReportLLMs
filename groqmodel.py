from groq import Groq
import json
import re


class GROQModel:

    def __init__(self, api_key, prompt_directory, repository):
        self.api_key = api_key
        self.prompt_directory = prompt_directory
        self.generating_directory = prompt_directory + "/generating"
        self.repository = repository
        self.client = Groq(api_key=api_key)

    def create_completion(self, context, user_prompt):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": user_prompt}
            ],
            model="mixtral-8x7b-32768",
        )
        return chat_completion

    def generate_grading_criteria(self, documents, metadata, title, number_of_tasks):
        with open(self.prompt_directory + "/requirements", "r") as file:
            context = file.read()
        with open(self.prompt_directory + "/requirements_instruction", "r") as file:
            user_prompt = file.read()

        tasks = self.extract_tasks(number_of_tasks)

        for i in range(number_of_tasks):
            chat_completion = self.create_completion(context.format(title, tasks["Exercise_" + str(i + 1)]), user_prompt)
            criteria = chat_completion.choices[0].message.content
            self.save_criteria(criteria, str(i + 1))

    def save_criteria(self, criteria, exercise_number):
        file_path = self.generating_directory + "/criteria_ex" + str(exercise_number)
        with open(file_path, "w") as file:
            file.write(criteria)

    def extract_tasks(self, number_of_tasks):
        tasks = {}

        for i in range(number_of_tasks):
            tasks["Exercise_" + str(i + 1)] = self.repository.get_task_description(i + 1)

        return tasks

    def read_criteria(self, number):
        with open(self.generating_directory + "/criteria_ex" + str(number), "r") as file:
            context = file.read()
        return context

    def get_task_answers(self, number_of_tasks):
        tasks = {}

        for i in range(number_of_tasks):
            tasks["Exercise_" + str(i + 1)] = self.repository.get_task_answer(i + 1)

        return tasks

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

    def grade_tasks(self, number_of_tasks):
        with open("./prompting/grading", "r") as file:
            context = file.read()
        completions = []
        tasks = self.extract_tasks(number_of_tasks)
        i = 0
        for task in tasks:
            criteria = self.read_criteria(i+1)
            answer = self.repository.get_task_answer(i+1)
            prompt = context.format(task, criteria, answer)
            chat_completion = self.create_completion(prompt,"Based on the criteria above, "
                                                            "evaluate the answer and provide a final grading"
                                                            " in JSON format as follows: "
                                                            "{\"points\": \"X\", \"description\": \"Y\"},"
                                                            "where X is the total points awarded and Y is a "
                                                            "maximum 2 sentence rationale. Let your answer be "
                                                            "only JSON without any other text")

            response = chat_completion.choices[0].message.content
            json_data = self.extract_json_from_response(response)

            if json_data:
                final_grade = {"points": int(json_data.get("points", 0)),
                               "description": json_data.get("description", "")}
            else:
                print("No valid JSON found in the AI response:", response)
                final_grade = {"points": 0,
                               "description": "The AI response did not contain valid JSON grading rationale."}

            completions.append(final_grade)
            i += 1

        return completions

    def generate_report(self, grades, number_of_tasks):
        report = {}

        for i in range(number_of_tasks):
            report[f"Exercise_{i + 1}"] = {
                "Grades": grades[i],
            }

        with open(f"{self.generating_directory}/report.json", "w") as file:
            json.dump(report, file, indent=4)

        return report

    def generate_aim_criteria(self, documents, metadata, title):
        with open(self.prompt_directory + "/aim_requirements", "r") as file:
            context = file.read()

        aim = self.extract_aim(documents, metadata)

        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": context.format(title, aim)},
                {"role": "user",
                 "content": "Generate grading requirements. Whole exercise must be graded within range of 0 to 5 "
                            "points. For each "
                            "requirement, the maximum number of points is 1, so the total number of points for "
                            "whole exercise is 5. Each requirement fulfillment can be only graded with 0 or 1 "
                            "point. Non integer points like 0.5 etc. are forbidden."}
            ],
            model="mixtral-8x7b-32768",
        )
        criteria = chat_completion.choices[0].message.content
        file_path = self.generating_directory + "/criteria_aim"
        with open(file_path, "w") as file:
            file.write(criteria)

