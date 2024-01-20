import json
from flask import Flask, jsonify, request
import sqlite3
app = Flask(__name__)
conn = sqlite3.connect(r'C:\Users\Administrator\Desktop\SCHOOL\database\29.12.2023.db')  # duong dan toiws file .db

# TERMINAL -> flask --app api run

@app.route('/students')
def get_all_students():
    # lays du lieu tu table
    cursor = conn.cursor()
    query = """
        SELECT students.student_id, student_name, class_name
        FROM students
        JOIN classes ON students.class_id = classes.class_id
    """
    cursor.execute(query)
    students = cursor.fetchall()
    return jsonify(students)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    full_name = data.get('full_name')
    email = data.get('email')

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO users (username, password, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (username, password, role, full_name, email))
        conn.commit()
        return jsonify({'message': 'User added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400  # Assuming errors indicate invalid input
    finally:
        cursor.close()

@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    student_name = data.get('student_name')
    student_email = data.get('student_email')
    class_id = data.get('class_id')
    user_id = data.get('user_id')  # user phair hop le 
    parents_id = data.get('parents_id')

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO students (student_name, student_email, class_id, user_id, parents_id)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (student_name, student_email, class_id, user_id, parents_id))
        conn.commit()
        return jsonify({'message': 'Student added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/classes', methods=['POST'])
def add_class():
    data = request.get_json()
    class_name = data.get('class_name')
    head_teacher_id = data.get('head_teacher_id')

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO classes (class_name, head_teacher_id)
            VALUES (?, ?)
        """
        cursor.execute(query, (class_name, head_teacher_id))
        conn.commit()
        return jsonify({'message': 'Class added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/enrollments', methods=['POST'])
def add_enrollment():
    data = request.get_json()
    student_id = data.get('student_id')
    subject_id = data.get('subject_id')
    school_year_id = data.get('school_year_id')
    enrollment_date = data.get('enrollment_date')  # data dangj date

    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO student_subject_enrollments (student_id, subject_id, school_year_id, enrollment_date)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (student_id, subject_id, school_year_id, enrollment_date))
        conn.commit()
        return jsonify({'message': 'Enrollment added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/users/<int:user_id>')
def get_user_info(user_id):
    try:
        cursor = conn.cursor()
        query = """
            SELECT user_id, username, full_name, email, role, class_name, student_name, parents_name, teacher_name
            FROM users
            LEFT JOIN students ON users.user_id = students.user_id
            LEFT JOIN parents ON users.user_id = parents.user_id
            LEFT JOIN teachers ON users.user_id = teachers.user_id
            LEFT JOIN classes ON students.class_id = classes.class_id
            WHERE users.user_id = ?
        """
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            return jsonify(user_data)
        else:
            return jsonify({'error': 'User not found'}), 404
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()