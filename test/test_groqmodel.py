import json
import os
import time

import pytest
from unittest.mock import Mock, patch, mock_open
from groqmodel import GROQModel


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def groq_model(mock_repository):
    return GROQModel(api_key="fake_api_key", prompt_directory="/fake/path", repository=mock_repository)


# unit tests
@patch("groqmodel.Groq")
def test_create_completion(mock_groq_class, mock_repository):
    mock_groq = mock_groq_class.return_value
    mock_chat = mock_groq.chat
    mock_completions = mock_chat.completions
    mock_create = mock_completions.create
    mock_create.return_value = Mock(choices=[Mock(message=Mock(content="mocked response"))])

    groq_model = GROQModel(api_key="fake_api_key", prompt_directory="/fake/path", repository=mock_repository)

    context = "Test context"
    user_prompt = "Test user prompt"

    result = groq_model.create_completion(context, user_prompt)

    assert result.choices[0].message.content == "mocked response"
    mock_create.assert_called_once_with(
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": user_prompt}
        ],
        model="mixtral-8x7b-32768"
    )


def test_generate_grading_criteria(groq_model, mock_repository):
    mock_repository.get_task_description.return_value = "task description"
    with patch("builtins.open", mock_open(read_data="file content")):
        with patch.object(groq_model, 'create_completion',
                          return_value=Mock(choices=[Mock(message=Mock(content="criteria"))])):
            criteria = groq_model.generate_grading_criteria(["doc1"], {"meta": "data"}, "title", 1, "doc1")
            assert criteria == "criteria"


def test_save_criteria(groq_model):
    with patch("builtins.open", mock_open()) as mocked_file:
        groq_model.save_criteria("criteria content", "1")
        mocked_file.assert_called_once_with("/fake/path/generating/criteria_ex1", "w")
        mocked_file().write.assert_called_once_with("criteria content")


def test_extract_tasks(groq_model, mock_repository):
    mock_repository.get_task_description.side_effect = lambda doc_id, i: f"Task {i} description"
    tasks = groq_model.extract_tasks("doc1", 2)
    assert tasks == {"Exercise_1": "Task 1 description", "Exercise_2": "Task 2 description"}


def test_extract_json_from_response(groq_model):
    valid_json_response = '{"points": "5", "description": "Good work"}'
    invalid_json_response = "Invalid JSON {points: 5, description: 'Good work'}"

    assert groq_model.extract_json_from_response(valid_json_response) == {"points": "5", "description": "Good work"}
    assert groq_model.extract_json_from_response(invalid_json_response) is None


# integration tests
def test_create_and_save_criteria(groq_model, mock_repository):
    mock_repository.get_task_description.return_value = "task description"
    with patch("builtins.open", mock_open(read_data="file content")):
        with patch.object(groq_model, 'create_completion',
                          return_value=Mock(choices=[Mock(message=Mock(content="criteria"))])):
            criteria = groq_model.generate_grading_criteria(["doc1"], {"meta": "data"}, "title", 1, "doc1")
            assert criteria == "criteria"

    with patch("builtins.open", mock_open()) as mocked_file:
        groq_model.save_criteria("criteria", "1")
        mocked_file.assert_called_once_with("/fake/path/generating/criteria_ex1", "w")
        mocked_file().write.assert_called_once_with("criteria")


def test_extract_and_save_tasks(groq_model, mock_repository):
    mock_repository.get_task_description.side_effect = lambda doc_id, i: f"Task {i} description"
    tasks = groq_model.extract_tasks("doc1", 2)
    assert tasks == {"Exercise_1": "Task 1 description", "Exercise_2": "Task 2 description"}

    with patch("builtins.open", mock_open()) as mocked_file:
        for i in range(1, 3):
            groq_model.save_criteria(tasks[f"Exercise_{i}"], str(i))
            mocked_file.assert_any_call(f"/fake/path/generating/criteria_ex{i}", "w")
            mocked_file().write.assert_any_call(f"Task {i} description")


def test_read_criteria_and_generate_summary(groq_model, mock_repository):
    mock_repository.get_conclusions.return_value = "Conclusion content"
    final_grade = {"points": 10, "description": "Excellent work"}

    with patch("builtins.open", mock_open(read_data="criteria content")):
        criteria = groq_model.read_criteria(1)
        assert criteria == "criteria content"

    with patch("os.makedirs") as mock_makedirs, \
            patch("builtins.open", mock_open(read_data="criteria content")), \
            patch.object(groq_model, 'create_completion',
                         return_value=Mock(choices=[Mock(message=Mock(content="summary"))])):
        mock_makedirs.side_effect = lambda path, exist_ok: os.makedirs(path, exist_ok=exist_ok) if not os.path.exists(
            path) else None

        report, author_id = groq_model.generate_report("doc1", [final_grade, final_grade], [final_grade] * 3, 2,
                                                       "John Doe 123")
        assert "Experiment aim" in report
        assert "Theoretical background" in report
        assert "Exercise_1" in report
        assert "Exercise_2" in report
        assert "Conclusions" in report
        assert author_id == "123"

        summary = groq_model.generate_summary(report, author_id)
        assert summary == "summary"


def test_full_workflow(groq_model, mock_repository):
    mock_repository.get_task_description.side_effect = lambda doc_id, i: f"Task {i} description"
    mock_repository.get_conclusions.return_value = "Conclusion content"
    mock_repository.get_task_answer.side_effect = lambda doc_id, i: f"Answer {i}"

    with patch("builtins.open", mock_open(read_data="file content")):
        with patch.object(groq_model, 'create_completion',
                          return_value=Mock(choices=[Mock(message=Mock(content="criteria"))])):
            criteria = groq_model.generate_grading_criteria(["doc1"], {"meta": "data"}, "title", 2, "doc1")
            assert criteria == "criteria"

    final_grade = {"points": 10, "description": "Excellent work"}
    with patch("builtins.open", mock_open(read_data="criteria content")) as mocked_file:
        with patch.object(groq_model, 'create_completion',
                          return_value=Mock(choices=[Mock(message=Mock(content="summary"))])):
            report, author_id = groq_model.generate_report("doc1", [final_grade, final_grade], [final_grade] * 3, 2,
                                                           "John Doe 123")
            assert "Experiment aim" in report
            assert "Theoretical background" in report
            assert "Exercise_1" in report
            assert "Exercise_2" in report
            assert "Conclusions" in report
            assert author_id == "123"

            summary = groq_model.generate_summary(report, author_id)
            assert summary == "summary"


# performance tests
def test_performance_grade_tasks(groq_model, mock_repository):
    mock_repository.get_task_description.side_effect = lambda doc_id, i: f"Task {i} description"
    mock_repository.get_task_answer.side_effect = lambda doc_id, i: f"Answer {i}"

    with patch("builtins.open", mock_open(read_data="file content")):
        with patch.object(groq_model, 'create_completion',
                          return_value=Mock(choices=[Mock(message=Mock(content=json.dumps({"points": 10, "description": "Good work"})))])):
            start_time = time.time()
            grades = groq_model.grade_tasks(doc_id="doc1")
            end_time = time.time()
            duration = end_time - start_time
            print(f"grade_tasks duration: {duration:.4f} seconds")
            assert grades is not None
            assert duration < 3


def test_performance_generate_report(groq_model, mock_repository):
    aim_tb_grades = [{"points": 10, "description": "Good aim"}, {"points": 8, "description": "Good background"}]
    task_grades = [{"points": 9, "description": "Good exercise 1"}, {"points": 7, "description": "Good exercise 2"}, {"points": 6, "description": "Good exercise 3"}, {"points": 9, "description": "Good conclusion"}]

    with patch("builtins.open", mock_open(read_data="file content")):
        start_time = time.time()
        report, author_id = groq_model.generate_report(doc_id="doc1", aim_tb_grades=aim_tb_grades, task_grades=task_grades, number_of_tasks=3, name="John Doe 123")
        end_time = time.time()
        duration = end_time - start_time
        print(f"generate_report duration: {duration:.4f} seconds")
        assert report is not None
        assert duration < 2


def test_performance_generate_summary(groq_model, mock_repository):
    report = {"Experiment aim": {"Grades": {"points": 10, "description": "Good aim"}},
              "Theoretical background": {"Grades": {"points": 8, "description": "Good background"}},
              "Exercise_1": {"Grades": {"points": 9, "description": "Good exercise 1"}},
              "Exercise_2": {"Grades": {"points": 7, "description": "Good exercise 2"}},
              "Exercise_3": {"Grades": {"points": 6, "description": "Good exercise 3"}},
              "Conclusions": {"Grades": {"points": 9, "description": "Good conclusion"}}}
    author_id = "123"

    with patch("builtins.open", mock_open(read_data="file content")):
        with patch.object(groq_model, 'create_completion',
                          return_value=Mock(choices=[Mock(message=Mock(content="summary"))])):
            start_time = time.time()
            summary = groq_model.generate_summary(report, author_id)
            end_time = time.time()
            duration = end_time - start_time
            print(f"generate_summary duration: {duration:.4f} seconds")
            assert summary == "summary"
            assert duration < 1
