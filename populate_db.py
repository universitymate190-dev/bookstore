#!/usr/bin/env python3
"""
Sample data script to populate the Bookstore database with test data.
Run this after starting the application for the first time.
"""

import sqlite3
import json

DATABASE = 'database.db'

def populate_sample_data():
    """Add sample exams and questions to the database"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Check if data already exists
    c.execute('SELECT COUNT(*) FROM exams')
    if c.fetchone()[0] > 0:
        print("Database already contains exams. Skipping sample data insertion.")
        conn.close()
        return
    
    # Sample exams
    exams = [
        ('General Knowledge Quiz', 'General Knowledge', 10, 'admin'),
        ('Python Programming Test', 'Programming', 15, 'admin'),
        ('Web Development CAT', 'Web Development', 20, 'admin'),
        ('Data Science Assessment', 'Data Science', 25, 'admin'),
    ]
    
    # Insert exams
    for exam in exams:
        c.execute('INSERT INTO exams (title, subject, time_limit, created_by) VALUES (?, ?, ?, ?)', exam)
    
    conn.commit()
    
    # Get exam IDs for questions
    c.execute('SELECT id FROM exams ORDER BY id')
    exam_ids = [row[0] for row in c.fetchall()]
    
    # Sample questions for General Knowledge
    gk_questions = [
        (exam_ids[0], 'What is the capital of France?', 'London', 'Berlin', 'Paris', 'Madrid', 'C'),
        (exam_ids[0], 'Which planet is closest to the Sun?', 'Venus', 'Mercury', 'Mars', 'Earth', 'B'),
        (exam_ids[0], 'What is the largest ocean on Earth?', 'Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean', 'Pacific Ocean', 'D'),
        (exam_ids[0], 'Who wrote Romeo and Juliet?', 'Jane Austen', 'William Shakespeare', 'Mark Twain', 'Charles Dickens', 'B'),
        (exam_ids[0], 'What is the chemical symbol for Gold?', 'Go', 'Gd', 'Au', 'Ag', 'C'),
        (exam_ids[0], 'Which country has the largest population?', 'India', 'United States', 'China', 'Indonesia', 'C'),
        (exam_ids[0], 'What is the highest mountain in the world?', 'K2', 'Kangchenjunga', 'Mount Everest', 'Lhotse', 'C'),
        (exam_ids[0], 'What is the smallest country in the world?', 'Monaco', 'San Marino', 'Vatican City', 'Liechtenstein', 'C'),
        (exam_ids[0], 'Who painted the Mona Lisa?', 'Michelangelo', 'Leonardo da Vinci', 'Raphael', 'Donatello', 'B'),
        (exam_ids[0], 'What is the speed of light?', '300,000 km/s', '150,000 km/s', '450,000 km/s', '200,000 km/s', 'A'),
    ]
    
    # Sample questions for Python Programming
    python_questions = [
        (exam_ids[1], 'What is the output of print(type([]))?', '<class "tuple">', '<class "list">', '<class "dict">', '<class "set">', 'B'),
        (exam_ids[1], 'Which keyword is used to create a function in Python?', 'func', 'function', 'def', 'define', 'C'),
        (exam_ids[1], 'What does "len()" function return?', 'Type of object', 'Length of object', 'Memory size', 'Hash of object', 'B'),
        (exam_ids[1], 'Which of these is NOT a Python data type?', 'List', 'Dictionary', 'String', 'Char', 'D'),
        (exam_ids[1], 'What is the correct syntax for creating a list in Python?', 'list = (1, 2, 3)', 'list = {1, 2, 3}', 'list = [1, 2, 3]', 'list = <1, 2, 3>', 'C'),
        (exam_ids[1], 'Which library is used for numerical computations in Python?', 'matplotlib', 'numpy', 'pandas', 'scipy', 'B'),
        (exam_ids[1], 'What is the correct way to write a comment in Python?', '/* Comment */', '<!-- Comment -->', '# Comment', '// Comment', 'C'),
        (exam_ids[1], 'Which method removes the last item from a list?', 'remove()', 'pop()', 'delete()', 'discard()', 'B'),
        (exam_ids[1], 'What does "self" refer to in a class?', 'The class itself', 'The parent class', 'The instance of the class', 'The module', 'C'),
        (exam_ids[1], 'Which keyword is used to handle exceptions in Python?', 'catch', 'handle', 'try', 'attempt', 'C'),
        (exam_ids[1], 'What is the correct way to import a module?', 'include module', 'require module', 'import module', 'load module', 'C'),
        (exam_ids[1], 'What is the output of 5 // 2 in Python?', '2', '2.5', '3', '2.0', 'A'),
        (exam_ids[1], 'Which of these is used to create a loop that iterates a specific number of times?', 'while', 'for', 'do-while', 'repeat', 'B'),
        (exam_ids[1], 'What is the correct syntax for a lambda function?', 'lambda x: x*2', 'lambda(x): x*2', 'lambda x = x*2', 'lambda x -> x*2', 'A'),
        (exam_ids[1], 'What is the purpose of the "pass" statement in Python?', 'End the program', 'Skip to next iteration', 'Do nothing (placeholder)', 'Exit the loop', 'C'),
    ]
    
    # Sample questions for Web Development
    web_questions = [
        (exam_ids[2], 'Which HTML tag is used for the largest heading?', '<h6>', '<h1>', '<h3>', '<h2>', 'B'),
        (exam_ids[2], 'What does CSS stand for?', 'Cascading Style Sheets', 'Computer Style Sheets', 'Colorful Style Sheets', 'Creative Style Sheets', 'A'),
        (exam_ids[2], 'Which tag is used to create a hyperlink in HTML?', '<link>', '<a>', '<href>', '<url>', 'B'),
        (exam_ids[2], 'What is the correct way to add a comment in CSS?', '// Comment', '<!-- Comment -->', '/* Comment */', '# Comment', 'C'),
        (exam_ids[2], 'Which property is used to change the text color in CSS?', 'color', 'text-color', 'font-color', 'text-style', 'A'),
        (exam_ids[2], 'What does HTML stand for?', 'Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks and Text Markup Language', 'A'),
        (exam_ids[2], 'Which JavaScript method is used to select an element by its ID?', 'getElementById', 'selectElement', 'getElement', 'querySelector', 'A'),
        (exam_ids[2], 'What is the correct syntax for a JavaScript function?', 'function myFunc {}', 'function myFunc() {}', 'func myFunc() {}', 'def myFunc() {}', 'B'),
        (exam_ids[2], 'Which property is used to set the width of an element in CSS?', 'size', 'width', 'length', 'dimension', 'B'),
        (exam_ids[2], 'What does JSON stand for?', 'JavaScript Object Network', 'JavaScript Object Notation', 'Java Serialized Object Notation', 'JavaScript Oriented Node', 'B'),
        (exam_ids[2], 'Which HTTP method is used to submit data to a server?', 'GET', 'POST', 'FETCH', 'SEND', 'B'),
        (exam_ids[2], 'What is the purpose of the <meta> tag in HTML?', 'Define metadata', 'Create links', 'Style elements', 'Define scripts', 'A'),
        (exam_ids[2], 'Which CSS property is used to align text?', 'align', 'text-align', 'alignment', 'text-alignment', 'B'),
        (exam_ids[2], 'What does DOM stand for?', 'Document Object Model', 'Document Operation Module', 'Data Object Management', 'Digital Object Model', 'A'),
        (exam_ids[2], 'Which framework is used for building responsive web applications?', 'React', 'Flask', 'Django', 'Spring', 'A'),
    ]
    
    # Sample questions for Data Science
    ds_questions = [
        (exam_ids[3], 'What does "ML" stand for?', 'Machine Learning', 'Memory Location', 'Multi-Layer', 'Module Language', 'A'),
        (exam_ids[3], 'Which library is used for data manipulation in Python?', 'numpy', 'pandas', 'matplotlib', 'scipy', 'B'),
        (exam_ids[3], 'What is the first step in Data Science?', 'Model Building', 'Data Collection', 'Visualization', 'Prediction', 'B'),
        (exam_ids[3], 'Which algorithm is used for classification?', 'Linear Regression', 'Decision Tree', 'K-means', 'Dimensionality Reduction', 'B'),
        (exam_ids[3], 'What does "CSV" stand for?', 'Comma Separated Variables', 'Comma Separated Values', 'Comma Separated Vector', 'Computed Statistical Value', 'B'),
        (exam_ids[3], 'Which is used for unsupervised learning?', 'Regression', 'Classification', 'Clustering', 'All of the above', 'C'),
        (exam_ids[3], 'What is the main purpose of Cross-validation?', 'Train the model', 'Evaluate the model', 'Preprocess data', 'Visualize data', 'B'),
        (exam_ids[3], 'Which method is used to handle missing values?', 'Deletion', 'Imputation', 'Both A and B', 'None of the above', 'C'),
        (exam_ids[3], 'What is the range of correlation coefficient?', '-1 to 0', '0 to 1', '-1 to 1', '0 to 100', 'C'),
        (exam_ids[3], 'Which visualization is used to show distribution?', 'Scatter plot', 'Histogram', 'Bar chart', 'Pie chart', 'B'),
        (exam_ids[3], 'What does "NaN" represent in data?', 'Not a Number', 'Null and None', 'Missing value', 'All of the above', 'D'),
        (exam_ids[3], 'Which algorithm is used for regression?', 'K-means', 'Linear Regression', 'Naive Bayes', 'KNN', 'B'),
        (exam_ids[3], 'What is "Overfitting" in ML?', 'Model fits training data too well', 'Model does not learn', 'Model is too simple', 'Model is too complex', 'A'),
        (exam_ids[3], 'What is the purpose of feature scaling?', 'Reduce dimensions', 'Normalize features', 'Remove outliers', 'Handle missing values', 'B'),
        (exam_ids[3], 'Which library is used for visualization in Python?', 'numpy', 'pandas', 'matplotlib', 'scikit-learn', 'C'),
    ]
    
    # Insert all questions
    all_questions = gk_questions + python_questions + web_questions + ds_questions
    
    for q in all_questions:
        c.execute('''INSERT INTO questions 
                     (exam_id, question, optionA, optionB, optionC, optionD, correct_answer) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', q)
    
    conn.commit()
    
    print("✅ Sample data inserted successfully!")
    print(f"   - Added {len(exams)} exams")
    print(f"   - Added {len(all_questions)} questions")
    print("\nYou can now:")
    print("1. Login with any credentials (will create new user)")
    print("2. Go to /exams to see the sample exams")
    print("3. Take an exam and see instant grading")
    
    conn.close()

if __name__ == '__main__':
    try:
        populate_sample_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the database is initialized by running app.py first")
