from docx import Document
import re

def read_docx_file(file_path):
    doc = Document(file_path)
    content = []
    for paragraph in doc.paragraphs:
        content.append(paragraph.text)
    return content


def split_document_into_sections(content, patterns):
    sections = {}
    current_section = None

    for line in content:
        for pattern in patterns:
            if line.strip().startswith(pattern):
                current_section = pattern
                sections[current_section] = []
                if current_section == "Title:":
                    sections[current_section].append(line[len("Title:"):].strip())
                break
        else:
            if current_section is not None and line.strip():
                sections[current_section].append(line.strip())

    return sections


def remove_non_ascii(input_string):
    cleaned_string = ''.join(char for char in input_string if ord(char) < 128)
    return cleaned_string


def extract_exercises(sections, exercise_number):
    exercises = {}
    current_section = None

    patterns = [f"Ex. {i}." for i in range(1, exercise_number + 1)]
    for line in sections["3. Research:"]:
        for pattern in patterns:
            if line.strip().startswith(pattern):
                current_section = pattern
                exercises[current_section] = []
        else:
            if current_section is not None:
                exercises[current_section].append(line.strip())
    return exercises


def read_file(file_path, patterns, number_of_exercises):
    sections = split_document_into_sections(read_docx_file(file_path), patterns)

    exercises = extract_exercises(sections, number_of_exercises)

    del sections["3. Research:"]
    sections.update(exercises)
    # metadatass = {
    #     "Section_name": [],
    #     "Global_sentence_number": [],
    #     "Local_sentence_number": [],
    #     "Type": [],
    #     "Exercise_number": [] # 0 if not exercise ssection
    # }

    metadatas = []
    pattern = r'Ex\. (?:[1-9]|[1-9][0-9])\.'

    documents = []
    i, j = 0, 0
    for section_name, sentences in sections.items():
        j = 0
        for sentence in sentences:
            cleaned_sentence = remove_non_ascii(sentence)
            documents.append(cleaned_sentence)
            meta = {}
            #Check if it is Ex. num. section and atach proper meta
            if re.findall(pattern, section_name):
                meta["Section_name"] = "3. Research:"

                # Extraction of the number from the section_name
                parts = section_name.split(".")
                if len(parts) == 3 and parts[0] == "Ex" and parts[1].strip().isdigit():
                    number = int(parts[1].strip())
                    meta["Exercise_number"] = number
                meta["Type"] = "Exercise"
            else:
                meta["Exercise_number"] = 0
                meta["Section_name"] = section_name
                meta["Type"] = "Description"

            meta["Global_sentence_number"] = i
            meta["Local_sentence_number"] = j

            metadatas.append(meta)

            j += 1
            i += 1
    return documents, metadatas
