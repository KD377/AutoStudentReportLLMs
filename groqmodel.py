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

    def generate_grading_criteria(self, title, number_of_tasks, doc_id):
        with open(self.prompt_directory + "/requirements", "r") as file:
            context = file.read()
        with open(self.prompt_directory + "/requirements_instruction", "r") as file:
            user_prompt = file.read()

        tasks = self.extract_tasks(doc_id, number_of_tasks)
        criteria_results = {}

        for i in range(1, number_of_tasks + 1):
            task_title = f"Exercise_{i}"
            chat_completion = self.create_completion(context.format(title, tasks[task_title]), user_prompt)
            criteria = chat_completion.choices[0].message.content
            self.save_criteria(criteria, str(i))
            criteria_results[task_title] = criteria

        return criteria_results

    def save_criteria(self, criteria, exercise_number):
        file_path = self.generating_directory + "/criteria_ex" + str(exercise_number)
        with open(file_path, "w") as file:
            file.write(criteria)

    def save_aim_tb_criteria(self, criteria, name):
        file_path = self.generating_directory + name
        with open(file_path, "w") as file:
            file.write(criteria)

    def extract_tasks(self, doc_id, number_of_tasks):
        tasks = {}

        for i in range(1, number_of_tasks + 1):
            tasks["Exercise_" + str(i)] = self.repository.get_task_description(doc_id, i)

        return tasks

    def read_criteria(self, number):
        with open(self.generating_directory + "/criteria_ex" + str(number), "r") as file:
            context = file.read()
        return context

    def read_criteria_all(self, file):
        with open(self.generating_directory + file, "r") as file:
            context = file.read()
        return context

    def get_task_answers(self, doc_id, number_of_tasks):
        tasks = {}

        for i in range(1, number_of_tasks + 1):
            tasks["Exercise_" + str(i)] = self.repository.get_task_answer(doc_id, i)

        return tasks

    def extract_json_from_response(self, response):
        try:
            json_data = json.loads(response)
            return json_data
        except json.JSONDecodeError:
            cleaned_response = re.sub(r'^.*?{', '{', response, flags=re.DOTALL)
            try:
                potential_json = json.loads(cleaned_response)
                return potential_json
            except json.JSONDecodeError:
                print("Error: Unable to extract valid JSON from response.")
                return None

    def grade_tasks(self, doc_id):
        global final_grade
        with open("./prompting/grading", "r") as file:
            context = file.read()
        completions = []

        tasks = self.extract_tasks(doc_id, 3)
        for i, task in enumerate(tasks):
            criteria = self.read_criteria(i + 1)
            answer = self.repository.get_task_answer(doc_id, i + 1)
            prompt = context.format(task, criteria, answer)
            json_data = None
            while json_data is None:
                chat_completion = self.create_completion(prompt, "Based on the criteria above, "
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

        criteria_c = self.read_criteria_all("/criteria_conclusion")
        answer_c = self.repository.get_conclusions(doc_id)
        prompt_c = context.format("Conclusions", criteria_c, answer_c, final_grade)
        json_data = None
        while json_data is None:
            chat_completion = self.create_completion(prompt_c, "Based on the criteria above and grades with description"
                                                               "for the excercises performed in the earlier part of the "
                                                               "report, "
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
        return completions

    def grade_aim_and_tb(self, doc_id):
        with open("./prompting/grading", "r") as file:
            context = file.read()
        completions = []

        criteria_aim = self.read_criteria_all("/criteria_aim")
        criteria_tb = self.read_criteria_all("/criteria_tb")

        answer_aim = self.repository.get_experiment_aim(doc_id)
        answer_tb = self.repository.get_theoretical_background(doc_id)

        prompt_aim = context.format("Experiment aim", criteria_aim, answer_aim)
        prompt_tb = context.format("Theoretical background", criteria_tb, answer_tb)
        prompts = [prompt_aim, prompt_tb]

        for prompt in prompts:
            json_data = None
            while json_data is None:
                chat_completion = self.create_completion(prompt, "Based on the criteria above, "
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
        return completions

    def generate_report(self, doc_id, aim_tb_grades, task_grades, number_of_tasks, name):
        report = {"Experiment aim": {
            "Grades": aim_tb_grades[0],
        },
            "Theoretical background": {
                "Grades": aim_tb_grades[1],
            }
        }

        for i in range(number_of_tasks + 1):
            if i < number_of_tasks:
                report[f"Exercise_{i + 1}"] = {
                    "Grades": task_grades[i],
                }
            else:
                report["Conclusions"] = {
                    "Grades": task_grades[i],
                }
        data = name.split()[:3]
        author_name, author_lastname, author_id = data

        with open(f"prompting/reports/{doc_id}_{author_name}_{author_lastname}_{author_id}_report.json",
                  "w") as file:
            json.dump(report, file, indent=4)

        return report, author_id

    def generate_summary(self, report, author_id):
        report_string = json.dumps(report)
        chat_completion = self.create_completion(report_string,
                                                 "based on the report assessing the student report, construct a summary of the report in a few sentences")

        response = chat_completion.choices[0].message.content
        with open(f"prompting/summary/report_{author_id}.txt",
                  "w") as file:
            file.write(response)
        return response

    def generate_criteria(self, title, header, ex1, ex2, ex3):
        if header == "Experiment aim":
            with open(self.prompt_directory + "/aim_requirements", "r") as file:
                content = file.read()
            with open(self.prompt_directory + "/aim_requirements_instruction", "r") as file2:
                user_prompt = file2.read()
            chat_completion = self.create_completion(content.format(title, header, ex1, ex2, ex3), user_prompt)
            criteria = chat_completion.choices[0].message.content
            self.save_aim_tb_criteria(criteria, "/criteria_aim")
            return criteria
        elif header == "Theoretical background":
            with open(self.prompt_directory + "/tb_requirements", "r") as file:
                content = file.read()
            with open(self.prompt_directory + "/tb_requirements_instruction", "r") as file2:
                user_prompt = file2.read()
            chat_completion = self.create_completion(content.format(title, header, ex1, ex2, ex3), user_prompt)
            criteria = chat_completion.choices[0].message.content
            self.save_aim_tb_criteria(criteria, "/criteria_tb")
            return criteria
        elif header == "Conclusions":
            with open(self.prompt_directory + "/conclusion_requirements", "r") as file:
                content = file.read()
            with open(self.prompt_directory + "/conclusion_requirements_instruction", "r") as file2:
                user_prompt = file2.read()
            chat_completion = self.create_completion(content.format(title, header, ex1, ex2, ex3), user_prompt)
            criteria = chat_completion.choices[0].message.content
            self.save_aim_tb_criteria(criteria, "/criteria_conclusion")
            return criteria