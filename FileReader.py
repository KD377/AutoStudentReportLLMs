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
                sections[current_section].append(current_section)
                if current_section == "Title:":
                    sections[current_section].append(line[len("Title:"):].strip())
                elif current_section == "Author:":
                    sections[current_section].append(line[len("Author:"):].strip())
                break
        else:
            if current_section is not None and line.strip():
                sections[current_section].append(line.strip())

    return sections


def remove_non_ascii(input_string):
    cleaned_string = ''.join(char for char in input_string if ord(char) < 128)
    return cleaned_string


# def extract_exercises(sections, exercise_number):
#     exercises = {}
#     current_section = None
#
#     patterns = [f"Ex. {i}." for i in range(1, exercise_number + 1)]
#     for line in sections["3. Research:"]:
#         for pattern in patterns:
#             if line.strip().startswith(pattern):
#                 current_section = pattern
#                 exercises[current_section] = []
#         else:
#             if current_section is not None:
#                 exercises[current_section].append(line.strip())
#     return exercises


def read_file(file_path, patterns):
    sections = split_document_into_sections(read_docx_file(file_path), patterns)
    documents = []
    metadatas = []
    i, j = 0, 0

    for section_name, sentences in sections.items():
        j = 0
        for sentence in sentences:
            cleaned_sentence = remove_non_ascii(sentence)
            documents.append(cleaned_sentence)
            meta = {"Section_name": section_name, "Global_sentence_number": i, "Local_sentence_number": j}
            j += 1
            i += 1

            if "Ex." in section_name:
                match = re.match(r"Ex\. (\d+)\.", section_name)
                if match:
                    meta["Exercise_number"] = int(match.group(1))
                    meta["Type"] = "description" if j == 1 else "answer"
            else:
                meta["Exercise_number"] = 0
                meta["Type"] = "description"

            metadatas.append(meta)

    return documents, metadatas
