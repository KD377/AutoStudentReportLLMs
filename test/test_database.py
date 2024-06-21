from unittest.mock import patch, MagicMock
import sqlite3
import timeit

from database import (create_database, create_table_students, create_table_grades,
                      create_table_titles, select_reports_by_title, select_grades_by_student_id,
                      add_student, get_title_id, add_grade, get_grades_by_report, add_title)


@patch('sqlite3.connect')
def test_create_database(mock_connect):
    create_database()
    mock_connect.assert_called_once_with('database.db')


@patch('sqlite3.connect')
def test_create_table_students(mock_connect):
    conn = MagicMock()
    mock_connect.return_value = conn
    create_table_students(conn)
    conn.cursor().execute.assert_called_once()
    conn.commit.assert_called_once()


@patch('sqlite3.connect')
def test_create_table_grades(mock_connect):
    conn = MagicMock()
    mock_connect.return_value = conn
    create_table_grades(conn)
    conn.cursor().execute.assert_called_once()
    conn.commit.assert_called_once()


@patch('sqlite3.connect')
def test_create_table_titles(mock_connect):
    conn = MagicMock()
    mock_connect.return_value = conn
    create_table_titles(conn)
    conn.cursor().execute.assert_called_once()
    conn.commit.assert_called_once()


@patch('sqlite3.connect')
def test_select_reports_by_title(mock_connect):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.fetchall.return_value = [(1,)]
    result = select_reports_by_title("Dummy Title")
    assert result == [(1,)]
    mock_conn.cursor.return_value.execute.assert_called()


@patch('sqlite3.connect')
def test_select_grades_by_student_id(mock_connect):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value.fetchall.return_value = [(1,)]
    result = select_grades_by_student_id(1)
    assert result == [(1,)]
    mock_conn.cursor.return_value.execute.assert_called()


@patch('sqlite3.connect')
def test_add_student(mock_connect):
    conn = MagicMock()
    mock_connect.return_value = conn
    conn.cursor.return_value.fetchone.return_value = None
    add_student(1, 'John', 'Doe')
    conn.cursor.return_value.execute.assert_called()
    conn.commit.assert_called()


@patch('sqlite3.connect')
def test_get_title_id(mock_connect):
    conn = MagicMock()
    mock_connect.return_value = conn
    conn.cursor.return_value.fetchone.return_value = [1]
    title_id = get_title_id("Sample Title")
    assert title_id == 1
    conn.cursor.return_value.execute.assert_called()


@patch('sqlite3.connect')
def test_add_grade(mock_connect):
    conn = MagicMock()
    mock_connect.return_value = conn
    conn.cursor.return_value.fetchone.side_effect = [[1], [1], None]
    add_grade(1, 95, 100, 5, 1, "{}", "{}", "[]")
    conn.cursor.return_value.execute.assert_called()
    conn.commit.assert_called()


@patch('sqlite3.connect')
def test_add_title(mock_connect):
    conn = MagicMock()
    mock_connect.return_value = conn
    conn.cursor.return_value.fetchone.return_value = None
    add_title("New Title")
    conn.cursor.return_value.execute.assert_called()
    conn.commit.assert_called()


