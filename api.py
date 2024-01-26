import json
from flask import Flask, jsonify, request
import sqlite3
app = Flask(__name__)
conn = sqlite3.connect(r'C:\Users\Administrator\Desktop\SCHOOL\database\29.12.2023.db', check_same_thread=False)  # duong dan toiws file .db

# TERMINAL -> flask --app api run

@app.route('/parents', methods=['POST'])    #POST PARENT REQ: USER ID / ROLE PARENT
def add_parent():
    data = request.get_json()
    parent_id = data.get('parent_id')
    parent_name = data.get('parent_name')
    parent_email = data.get('parent_email')
    user_id = data.get('user_id')

    try:
        cursor = conn.cursor()

        # Check for existing user ID
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone() is not None
        if not user_exists:
            return jsonify({'error': 'Invalid user ID'}), 400

        # Check user role
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        user_role = cursor.fetchone()[0]  # Assuming 'role' is the column name
        if user_role != 'parent':
            return jsonify({'error': 'Invalid user role'}), 400

        # Check for conflicts in other tables
        cursor.execute("SELECT 1 FROM students WHERE user_id = ?", (user_id,))
        exists_in_students = cursor.fetchone() is not None
        cursor.execute("SELECT 1 FROM teachers WHERE user_id = ?", (user_id,))
        exists_in_teachers = cursor.fetchone() is not None
        cursor.execute("SELECT 1 FROM parents WHERE user_id = ?", (user_id,))
        exists_in_parents = cursor.fetchone() is not None
        if exists_in_students or exists_in_teachers or exists_in_parents:
            return jsonify({'error': 'User ID already exists in another table'}), 400

        # Insert parent if all checks pass
        query = """
            INSERT INTO parents (parent_id, parents_name, parents_email, user_id)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (parent_id, parent_name, parent_email, user_id))
        conn.commit()
        return jsonify({'message': 'Parents added successfully'}), 201

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/users', methods=['POST'])  #POST USER REQ: UNIQUE ID
def add_user():
    data = request.get_json()
    user_id = data.get('user_id') 
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    full_name = data.get('full_name')
    email = data.get('email')

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users 
            (user_id, username, password, role, full_name, email)
            VALUES (?, ?, ?, ?, ?, ?)"""
            , (user_id, username, password, role, full_name, email))
        conn.commit()
        cursor.close()
        return jsonify({'message': 'User added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400    

@app.route('/students', methods=['POST'])  #POST STUDENT REQ: USER ID / ROLE STUDENT REQ: PARENTS ID
def add_student():
    data = request.get_json()
    student_id = data.get('student_id')
    student_name = data.get('student_name')
    student_email = data.get('student_email')
    class_id = data.get('class_id')
    user_id = data.get('user_id')
    parents_id = data.get('parents_id')

    try:
        cursor = conn.cursor()

        # Check for existing user ID
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone() is not None
        if not user_exists:
            return jsonify({'error': 'Invalid user ID'}), 400

        # Check user role
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        user_role = cursor.fetchone()[0]  # Assuming 'role' is the column name
        if user_role != 'student':
            return jsonify({'error': 'Invalid user role'}), 400

        # Check for conflicts in other tables
        cursor.execute("SELECT 1 FROM teachers WHERE user_id = ?", (user_id,))
        exists_in_teachers = cursor.fetchone() is not None
        cursor.execute("SELECT 1 FROM parents WHERE user_id = ?", (user_id,))
        exists_in_parents = cursor.fetchone() is not None
        if exists_in_teachers or exists_in_parents:
            return jsonify({'error': 'User ID already exists in another table'}), 400

        # Check for class
        cursor.execute("SELECT 1 FROM classes WHERE class_id = ?", (class_id,))
        exists_in_class = cursor.fetchone() is not None
        if not exists_in_class:
            return jsonify({'error': 'Invalid class ID'}), 400

        # Check for existing parent ID
        cursor.execute("SELECT 1 FROM parents WHERE parents_id = ?", (parents_id,))
        parent_exists = cursor.fetchone() is not None
        if not parent_exists:
            return jsonify({'error': 'Invalid parent ID'}), 400

        # Insert student if all checks pass
        query = """
            INSERT INTO students (student_id, student_name, student_email, class_id, user_id, parents_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (student_id, student_name, student_email, class_id, user_id, parents_id))
        conn.commit()
        return jsonify({'message': 'Student added successfully'}), 201

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/teachers', methods=['POST'])   #POST TEACHERS REQ: USER ID / ROLE TEACHER
def add_teacher():
    data = request.get_json()
    teacher_name = data.get('teacher_name')
    teacher_email = data.get('teacher_email')
    teacher_id = data.get('teacher_id')
    user_id = data.get('user_id')

    try:
        cursor = conn.cursor()

        # Check for existing user ID
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone() is not None
        if not user_exists:
            return jsonify({'error': 'Invalid user ID'}), 400
        
        # Check for existing user ID in teachers
        cursor.execute("SELECT 1 FROM teachers WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone() is not None
        if user_exists:
            return jsonify({'error': 'Invalid user ID (already a teacher)'}), 400

         # Check user role
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        user_role = cursor.fetchone()[0]  # Assuming 'role' is the column name
        if user_role != 'teacher':
            return jsonify({'error': 'Invalid user role'}), 400

        # Check for conflicts in other tables
        cursor.execute("SELECT 1 FROM students WHERE user_id = ?", (user_id,))
        exists_in_students = cursor.fetchone() is not None
        cursor.execute("SELECT 1 FROM parents WHERE user_id = ?", (user_id,))
        exists_in_parents = cursor.fetchone() is not None
        if exists_in_students or exists_in_parents:
            return jsonify({'error': 'User ID already exists in another table'}), 400

        # Insert teacher if all checks pass
        query = """
            INSERT INTO teachers (teacher_id, teacher_name, teacher_email, user_id)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (teacher_id, teacher_name, teacher_email, user_id))
        conn.commit()
        return jsonify({'message': 'Teacher added successfully'}), 201

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/classes', methods=['POST'])    #POST CLASSES REQ: TEACHER ID
def add_class():
    data = request.get_json()
    class_id = data.get('class_id')
    class_name = data.get('class_name')
    head_teacher_id = data.get('head_teacher_id')

    try:
        cursor = conn.cursor()

        # Check for existing head teacher ID in the teachers table
        cursor.execute("SELECT 1 FROM teachers WHERE teacher_id = ?", (head_teacher_id,))
        head_teacher_exists = cursor.fetchone() is not None
        if not head_teacher_exists:
            return jsonify({'error': 'Invalid head teacher ID'}), 400

        query = """
            INSERT INTO classes (class_id, class_name, head_teacher_id)
            VALUES (?, ?, ?)
        """
        cursor.execute(query, (class_id, class_name, head_teacher_id))
        conn.commit()
        return jsonify({'message': 'Class added successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/enrollments', methods=['POST']) #POST ENROLLMENT REQ: STUDENT ID REQ: SUBJECT ID
def add_enrollment():
    data = request.get_json()
    student_id = data.get('student_id')
    subject_id = data.get('subject_id')
    school_year_id = data.get('school_year_id')
    enrollment_date = data.get('enrollment_date')  # data type date

    try:
        cursor = conn.cursor()

         # Check for existing student ID
        cursor.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,))
        student_exists = cursor.fetchone() is not None
        if not student_exists:
            return jsonify({'error': 'Invalid student ID'}), 400

        # Check for existing subject ID
        cursor.execute("SELECT 1 FROM subjects WHERE subject_id = ?", (subject_id,))
        subject_exists = cursor.fetchone() is not None
        if not subject_exists:
            return jsonify({'error': 'Invalid subject ID'}), 400
        
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

@app.route('/subjects', methods=['POST']) #POST SUBJECT REQ: TEACHER ID
def add_subject():
    data = request.get_json()
    subject_id = data.get('subject_id')
    subject_name = data.get('subject_name')
    managing_teacher_id = data.get('managing_teacher')

    try:
        cursor = conn.cursor()

        # Check for existing managing teacher ID
        cursor.execute("SELECT 1 FROM teachers WHERE user_id = ?", (managing_teacher_id,))
        teacher_exists = cursor.fetchone() is not None
        if not teacher_exists:
            return jsonify({'error': 'Invalid managing teacher ID'}), 400

        # Insert subject if managing teacher ID exists
        query = """
            INSERT INTO subjects (subject_id, subject_name, managing_teacher)
            VALUES (?, ?, ?)
        """
        cursor.execute(query, (subject_id, subject_name, managing_teacher_id))
        conn.commit()
        return jsonify({'message': 'Subject added successfully'}), 201

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/users/<int:user_id>') #GET SPECIFIC USER ID
def get_user_info(user_id):
    try:
        cursor = conn.cursor()
        query = """
            SELECT user_id, username, full_name, email, role
            FROM users
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

@app.route('/users')    #GET ALL USERS
def get_all_users():
    try:
        cursor = conn.cursor()
        query = "SELECT user_id, username, full_name, email, role FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        return jsonify(users), 200
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/students') #GET ALL STUDENTS
def get_all_students():
    
    # lays du lieu tu table
    cursor = conn.cursor()
    query = """
        SELECT students.student_id, student_name, class_name, user_id, parents_id
        FROM students
        JOIN classes ON students.class_id = classes.class_id
    """
    cursor.execute(query)
    students = cursor.fetchall()
    return jsonify(students)