import sqlite3

def create_table_students(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Students (
                    student_id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL
                    )''')
    conn.commit()


def create_table_grades(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Grades (
                    id INTEGER PRIMARY KEY,
                    title_id INTEGER,
                    total_points INTEGER,
                    max_total_points INTEGER,
                    final_grade INTEGER,
                    student_id INTEGER,
                    report BLOB, 
                    final_report BLOB, 
                    document BLOB,
                    FOREIGN KEY (title_id) REFERENCES Titles(id),
                    FOREIGN KEY (student_id) REFERENCES Students(student_id)
                    )''')
    conn.commit()


def create_table_titles(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Titles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT
                    )''')
    conn.commit()


def create_database():
    conn = sqlite3.connect('database.db')
    create_table_students(conn)
    create_table_grades(conn)
    create_table_titles(conn)
    conn.close()


def select_reports_by_title(title_name):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id
                          FROM Grades
                          WHERE title_id = (SELECT id FROM Titles WHERE title = ?)''', (title_name,))
        reports = cursor.fetchall()
        conn.close()
        return reports
    except sqlite3.Error as e:
        print("Error selecting reports by title:", e)
        return []


def select_grades_by_student_id(student_id):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id
                          FROM Grades
                          WHERE student_id = ?''', (student_id,))
        grades = cursor.fetchall()
        conn.close()
        return grades
    except sqlite3.Error as e:
        print("Error selecting grades by student ID:", e)
        return []


def add_student(student_id, first_name, last_name):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''SELECT * FROM Students WHERE student_id = ?''', (student_id,))
        existing_student = cursor.fetchone()
        
        if existing_student:
            print("Student with ID", student_id, "already exists.")
        else:
            cursor.execute('''INSERT INTO Students (student_id, first_name, last_name)
                              VALUES (?, ?, ?)''', (student_id, first_name, last_name))
            conn.commit()
            print("Student", first_name, last_name, "with ID", student_id, "has been added to the database.")
        conn.close()
    except sqlite3.Error as e:
        print("Error adding student:", e)


def get_title_id(title):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id FROM Titles WHERE title = ?''', (title,))
        title_id = cursor.fetchone()
        if title_id:
            return title_id[0]
        else:
            cursor.execute('''INSERT INTO Titles (title) VALUES (?)''', (title,))
            conn.commit()
            return cursor.lastrowid
        
    except sqlite3.Error as e:
        print("Error getting title ID:", e)
        return None

def add_grade(title_id, total_points, max_total_points, final_grade, student_id, report, final_report, document):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT id FROM Titles WHERE id = ?''', (title_id,))
        title_row = cursor.fetchone()
        if not title_row:
            print("Title with the given ID does not exist.")
            return
        
        cursor.execute('''SELECT student_id FROM Students WHERE student_id = ?''', (student_id,))
        student_row = cursor.fetchone()
        if not student_row:
            print("Student with ID", student_id, "does not exist.")
            return

        if final_grade < 2 or final_grade > 5:
            print("Final grade must be a value between 2 and 5.")
            return

        cursor.execute('''SELECT id FROM Grades WHERE title_id = ? AND student_id = ?''', (title_id, student_id))
        existing_grade = cursor.fetchone()

        if existing_grade:
            cursor.execute('''UPDATE Grades SET 
                              total_points = ?, max_total_points = ?, final_grade = ?, 
                              report = ?, final_report = ?, document = ?
                              WHERE title_id = ? AND student_id = ?''',
                           (total_points, max_total_points, final_grade, report, final_report, document, title_id, student_id))
            print("Grade has been updated successfully.")
        else:
            cursor.execute('''INSERT INTO Grades (title_id, total_points, max_total_points, final_grade,
                                                  student_id, report, final_report, document)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                           (title_id, total_points, max_total_points, final_grade, student_id, report, final_report, document))
            print("Grade has been added successfully.")

        conn.commit()

    except sqlite3.Error as e:
        print("Error adding grade:", e)

    finally:
        conn.close()


def get_grades_by_report(report_title):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('''SELECT student_id, first_name, last_name FROM Students''')
        students = cursor.fetchall()
        
        cursor.execute('''SELECT Students.student_id, Grades.final_grade
                          FROM Students
                          LEFT JOIN Grades ON Students.student_id = Grades.student_id
                          LEFT JOIN Titles ON Grades.title_id = Titles.id
                          WHERE Titles.title = ?
                          ''', (report_title,))
        grades = dict(cursor.fetchall())
        conn.close()
        result = []
        for student_id, first_name, last_name in students:
            if student_id in grades:
                result.append((first_name, last_name, student_id, grades[student_id]))
            else:
                result.append((first_name, last_name, student_id, -1))
        return result
    except sqlite3.Error as e:
        print("Error retrieving grades:", e)
        return []

