from docx import Document


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


def read_file(file_path, patterns):
    sections = split_document_into_sections(read_docx_file(file_path), patterns)
    print(extract_exercises(sections, 3))
    # documents = []
    # section_names = []
    #
    # for section_name, sentences in sections.items():
    #     for sentence in sentences:
    #         cleaned_sentence = remove_non_ascii(sentence)
    #         documents.append(cleaned_sentence)
    #         section_names.append(section_name)
    # return documents, section_names
