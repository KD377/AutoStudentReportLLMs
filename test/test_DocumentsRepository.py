import pytest
from unittest.mock import MagicMock
from DocumentsRepository import DocumentsRepository


@pytest.fixture
def mock_collection():
    return MagicMock()


@pytest.fixture
def documents_repo(mock_collection):
    return DocumentsRepository(mock_collection)


def test_get_title(mock_collection, documents_repo):
    mock_collection.get.return_value = {"documents": ["Title: Sample Document"]}
    title = documents_repo.get_title(1)
    assert title == "Sample Document"


def test_get_author(mock_collection, documents_repo):
    mock_collection.get.return_value = {"documents": ["Author: John Doe"]}
    author = documents_repo.get_author(1)
    assert author == "John Doe"


def test_get_task_answer(mock_collection, documents_repo):
    mock_collection.get.return_value = {"documents": ["Correct Answer"]}
    answer = documents_repo.get_task_answer(1, 1)
    assert answer == "Correct Answer"


def test_get_task_description(mock_collection, documents_repo):
    mock_collection.get.return_value = {"documents": ["Task description goes here"]}
    description = documents_repo.get_task_description(1, 1)
    assert description == "Task description goes here"


def test_get_experiment_aim(mock_collection, documents_repo):
    mock_collection.get.return_value = {"documents": ["Aim of the experiment"]}
    aim = documents_repo.get_experiment_aim(1)
    assert aim == "Aim of the experiment"


def test_get_theoretical_background(mock_collection, documents_repo):
    mock_collection.get.return_value = {"documents": ["Background information"]}
    background = documents_repo.get_theoretical_background(1)
    assert background == "Background information"


def test_get_conclusions(mock_collection, documents_repo):
    mock_collection.get.return_value = {"documents": ["Conclusive remarks"]}
    conclusions = documents_repo.get_conclusions(1)
    assert conclusions == "Conclusive remarks"


def test_title_and_author_integration(mock_collection, documents_repo):
    mock_collection.get.side_effect = [
        {"documents": ["Title: Example Document"]},
        {"documents": ["Author: John Doe"]}
    ]
    title = documents_repo.get_title(1)
    author = documents_repo.get_author(1)
    assert title == "Example Document"
    assert author == "John Doe"
    assert mock_collection.get.call_count == 2


def test_task_description_and_answer_integration(mock_collection, documents_repo):
    mock_collection.get.side_effect = [
        {"documents": ["Describe the procedure"]},
        {"documents": ["Completed procedure steps"]}
    ]
    description = documents_repo.get_task_description(1, 1)
    answer = documents_repo.get_task_answer(1, 1)
    assert description == "Describe the procedure"
    assert answer == "Completed procedure steps"
    assert mock_collection.get.call_count == 2


def test_full_document_retrieval_integration(mock_collection, documents_repo):
    mock_collection.get.side_effect = [
        {"documents": ["Title: Complete Document Analysis"]},
        {"documents": ["Author: Jane Smith"]},
        {"documents": ["Task 1 Description"]},
        {"documents": ["Answer to Task 1"]},
        {"documents": ["Aim is to analyze..."]},
        {"documents": ["Background information..."]},
        {"documents": ["Conclusions are..."]}
    ]
    title = documents_repo.get_title(1)
    author = documents_repo.get_author(1)
    task1_desc = documents_repo.get_task_description(1, 1)
    task1_ans = documents_repo.get_task_answer(1, 1)
    aim = documents_repo.get_experiment_aim(1)
    background = documents_repo.get_theoretical_background(1)
    conclusions = documents_repo.get_conclusions(1)
    assert title == "Complete Document Analysis"
    assert author == "Jane Smith"
    assert task1_desc == "Task 1 Description"
    assert task1_ans == "Answer to Task 1"
    assert aim == "Aim is to analyze..."
    assert background == "Background information..."
    assert conclusions == "Conclusions are..."
    assert mock_collection.get.call_count == 7


def test_performance(mock_collection, documents_repo):
    import time
    start_time = time.time()
    for _ in range(1000):
        documents_repo.get_title(1)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Time taken for 1000 get_title calls: {duration}s")
    assert duration < 10
