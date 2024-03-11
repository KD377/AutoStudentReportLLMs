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
        if line.strip() in patterns:
            current_section = line.strip()
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append(line)

    return sections

section_start_pattern = (
    "Title:",
    "1. Experiment aim:",
    "2. Theoretical background: ",
    "3. Research: ",
    "4. Conclusions:"
)

file_path = "./reports/reportsC/expC_no2.docx"
