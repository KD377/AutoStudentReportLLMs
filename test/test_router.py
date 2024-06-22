import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from router import router, read_docx, extract_index_number


client = TestClient(router)




@pytest.fixture
def mock_upload_file():
    file_mock = Mock(spec=UploadFile)
    file_mock.filename = "test.docx"
    file_mock.content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    file_mock.file = Mock()
    file_mock.file.read = Mock(return_value=b"dummy content")
    file_mock.file.seek = Mock()
    return file_mock


# Unit tests

def test_read_docx(mock_upload_file):
    with patch("router.Document") as mock_document:
        mock_document.return_value.paragraphs = ["Paragraph 1", "Paragraph 2"]
        paragraphs = read_docx(mock_upload_file)
        assert paragraphs == ["Paragraph 1", "Paragraph 2"]


def test_extract_index_number():
    file_name = "report_1234_report.json"
    index_number = extract_index_number(file_name)
    assert index_number == "1234"

    invalid_file_name = "report_1234.txt"
    index_number = extract_index_number(invalid_file_name)
    assert index_number is None


# Integration tests

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

@patch('router.extract_title')
@patch('router.extract_author')
@patch('router.get_title_id')
@patch('router.add_title')
def test_upload_reports(mock_add_title, mock_get_title_id, mock_extract_author, mock_extract_title):
    mock_extract_title.return_value = ("Test Title", [b"Test content"])
    mock_extract_author.return_value = ["123"]
    mock_get_title_id.return_value = None
    mock_add_title.return_value = None

    files = [('files', ('test.docx', b"dummy content", 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))]
    response = client.post("/reports/upload", files=files)

    assert response.status_code == 200
    assert response.json() == {"message": "Successfully uploaded 1 files", "title": "Test Title"}


@patch('router.generate_grading_criteria')
def test_generate_criteria(mock_generate_grading_criteria):
    mock_generate_grading_criteria.return_value = ("aim criteria", "background criteria", "research criteria", "conclusions criteria")

    response = client.post("/criteria/topic/1/generate")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Created grading",
        "criteria": {
            "aim": "aim criteria",
            "background": "background criteria",
            "research": "research criteria",
            "conclusions": "conclusions criteria"
        }
    }


# Performance tests
def test_performance_generate_criteria():
    with patch("router.generate_grading_criteria",
               return_value=("Aim criteria", "Background criteria", "Research criteria", "Conclusions criteria")):
        import time
        start_time = time.time()
        response = client.post("/criteria/topic/1/generate")
        end_time = time.time()
        duration = end_time - start_time
        assert response.status_code == 200
        assert duration < 1