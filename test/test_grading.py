import json
import os
import time
from unittest.mock import patch, MagicMock, mock_open
import pytest
import grading

@pytest.fixture
def mock_files(monkeypatch):
    # Mock os.listdir to control what files are seen
    monkeypatch.setattr(os, "listdir", MagicMock(return_value=["file_author_id.json"]))

    # Mock open to prevent any actual file I/O
    mock_open_patch = patch("builtins.open", mock_open(read_data=json.dumps(
        {"section1": {"Grades": {"points": 3}}, "section2": {"Grades": {"points": 4}}})))
    file_mock = mock_open_patch.start()
    yield file_mock
    mock_open_patch.stop()


@pytest.fixture
def setup_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "dummy_api_key")
    monkeypatch.setenv("TOKENIZERS_PARALLELISM", "false")

# Unit Tests

def test_delete_collection():
    with patch("shutil.rmtree") as mock_rmtree:
        grading.delete_collection()
        mock_rmtree.assert_called_once_with("./chroma_data")



def test_find_first_in_file():
    with patch("os.listdir", return_value=["report_1_123.docx", "report_1_124.docx"]):
        result = grading.Find_First_In_File(1, "./reports/")
        assert "report_1_123.docx" in result

# Integration Tests:
def test_count_points(mock_files):
    total_points, max_points, final_grade = grading.count_points("./path/", "author_id")
    assert total_points == 7
    assert max_points == 10
    assert final_grade == 3.5

# Performance Tests
def test_delete_collection_performance():
    with patch("shutil.rmtree") as mock_rmtree:
        start_time = time.perf_counter()
        grading.delete_collection()
        end_time = time.perf_counter()

        duration = end_time - start_time
        print(f"Execution time: {duration:.4f} seconds")

        assert duration < 0.5, "The delete_collection function is too slow."

        mock_rmtree.assert_called_once_with("./chroma_data")
