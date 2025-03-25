from flask import Flask, request, render_template, jsonify
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Set the non-GUI backend before importing pyplot
import matplotlib.pyplot as plt
import os
from datetime import datetime
import xlsxwriter
from webdriver_manager.chrome import ChromeDriverManager
from flask import session

# Flask app
app = Flask(__name__)
#Set the secret key to a random bytes or a string
app.secret_key = 'jhrguwe2gr289rhhevfqehfvqfh'


# Configure Selenium Chrome options
chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument("--allow-insecure-localhost")

# Function to scrape data
def scrape_roll_numbers(roll_numbers, driver_path):
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)
    website = "https://aupulse.campx.in/aupulse/ums/results"
    student_data = []
    branch_list = {'B TECH in ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING': 'AIML', 'B TECH in ARTIFICIAL INTELLIGENCE': 'AI', 'B TECH in Computer Science and Engineering': 'CSE', 'B TECH in Electronics and Communication Engineering': 'ECE'}
    
    for roll_no in roll_numbers:
        try:
            driver.get(website)
            roll_no_input = wait.until(EC.presence_of_element_located((By.ID, "rollNo")))
            roll_no_input.send_keys(roll_no)
            exam_type_dropdown = wait.until(EC.presence_of_element_located((By.ID, "examType")))
            exam_type_dropdown.click()
            general_option = wait.until(EC.presence_of_element_located((By.XPATH, "//li[@data-value='general']")))
            general_option.click()
            button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[text()='Get Result']")))
            button.click()

            wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]")))
            student_name = driver.find_element(By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[2]/p").text
            hall_ticket_number = driver.find_element(By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[1]/p").text
            program_element = driver.find_element(By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[3]/p").text
            program = "B tech" if "B TECH" in program_element else "None"
            branch = branch_list[program_element]
            section = hall_ticket_number[-3]
            cgpa_element = driver.find_element(By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[2]").text
            cgpa = cgpa_element.split(":")[1].strip() if ":" in cgpa_element else cgpa_element.strip()

            # Extract semester tables
            tables = driver.find_elements(By.CLASS_NAME, 'css-1n196hx')
            sem1_table = []
            sem2_table = []
            sem3_table = []

            for index, table in enumerate(tables):
                headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]
                rows = table.find_elements(By.TAG_NAME, 'tr')
                for row in rows[1:]:
                    cells = row.find_elements(By.TAG_NAME, 'td')
                    row_data = {headers[i]: cells[i].text for i in range(len(cells))}
                    
                    # Map the single 'Status' field to 'Status 1' and 'Status 2'
                    status = row_data.get("Status", "")
                    row_data["Status 1"] = status
                    row_data["Status 2"] = "Not Applicable"  # Default value for Status 2
                    
                    if index == 0:  # Sem1 table
                        sem1_table.append(row_data)
                    elif index == 1:  # Sem2 table
                        sem2_table.append(row_data)
                    elif index == 2:  # Sem3 table
                        sem3_table.append(row_data)

            # Add semester tables to student data
            student_data.append({
                "Hall Ticket Number": hall_ticket_number,
                "Student Name": student_name,
                "Program": program,
                "Branch": branch,
                "Section": section,
                "CGPA": cgpa,
                "Sem1 Details": sem1_table,
                "Sem2 Details": sem2_table,
                "Sem3 Details": sem3_table
            })

        except Exception as e:
            print(f"Error scraping roll number {roll_no}: {e}")

    driver.quit()
    return student_data

# Function to manage parallel scraping
def run_parallel_scraping(all_roll_numbers, driver_path, max_threads=5):
    chunk_size = len(all_roll_numbers) // max_threads
    chunks = [all_roll_numbers[i:i + chunk_size] for i in range(0, len(all_roll_numbers), chunk_size)]
    all_data = []
    with ThreadPoolExecutor(max_threads) as executor:
        futures = [executor.submit(scrape_roll_numbers, chunk, driver_path) for chunk in chunks]
        for future in futures:
            all_data.extend(future.result())
    return all_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    all_roll_numbers = []  # Initialize the list for all roll numbers
    choice = request.form.get('choice')
    file_name = request.form.get('filename')
    if not file_name.endswith('.xlsx'):
        file_name += '.xlsx'

    # Get selected columns from the form
    selected_columns = request.form.getlist('columns')

    # Handling different choices (single or range)
    if choice == 'single':
        single_rollno = request.form['single']
        if single_rollno:  # Ensure it's not empty
            all_roll_numbers.append(single_rollno)
        else:
            return jsonify({'status': 'error', 'message': "Please provide a single roll number."})

    elif choice == 'range':
        rollno_range_from = request.form['from']
        rollno_range_to = request.form['to']
        if not rollno_range_from or not rollno_range_to:
            return jsonify({'status': 'error', 'message': "Please provide both 'From' and 'To' roll numbers for the range."})

        try:
            rollno_start = int(rollno_range_from[-2:])
            rollno_end = int(rollno_range_to[-2:])
        except ValueError:
            return jsonify({'status': 'error', 'message': "Invalid roll number format."})

        if rollno_start > rollno_end:
            return jsonify({'status': 'error', 'message': "'From' roll number must be less than or equal to 'To' roll number."})

        # Generate roll numbers in the range
        all_roll_numbers.extend([f"{rollno_range_from[:-2]}{str(i).zfill(2)}" for i in range(rollno_start, rollno_end + 1)])

        # For additional ranges, if any
        from_roll_nos = request.form.getlist('from')
        to_roll_nos = request.form.getlist('to')
        for i in range(1, len(from_roll_nos)):
            from_roll_no = from_roll_nos[i]
            to_roll_no = to_roll_nos[i]
            try:
                rollno_start = int(from_roll_no[-2:])
                rollno_end = int(to_roll_no[-2:])
                all_roll_numbers.extend([f"{from_roll_no[:-2]}{str(i).zfill(2)}" for i in range(rollno_start, rollno_end + 1)])
            except ValueError:
                return jsonify({'status': 'error', 'message': "Invalid roll number format for additional ranges."})

    else:
        return jsonify({'status': 'error', 'message': "Invalid choice."})

    # Setup the driver to automatically download and install ChromeDriver
    driver_path = ChromeDriverManager().install()  # This will give you the path to the installed ChromeDriver
    service = Service(driver_path)  # Create a Service object with the driver path
    driver = webdriver.Chrome(service=service, options=chrome_options)  
    try:
        # Wait for the browser to be fully initialized before accessing capabilities
        WebDriverWait(driver, 10).until(lambda d: d.capabilities)
        browser_name = driver.capabilities.get("browserName")
        print(f"Browser Name: {browser_name}")
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")

    try:
        # Run parallel scraping to get student data
        results = run_parallel_scraping(all_roll_numbers, driver_path, max_threads=5)

        # Create a list to store all rows for the final DataFrame
        all_rows = []

        for student in results:
            # Extract basic details
            student_row = {
                ("Hall Ticket Number", ""): student["Hall Ticket Number"],
                ("Student Name", ""): student["Student Name"],
                ("Program", ""): student["Program"],
                ("Branch", ""): student["Branch"],
                ("Section", ""): student["Section"],
                ("CGPA", ""): student["CGPA"],
                ("No of Backlogs", ""): student.get("No of Backlogs", 0)
            }

            # Add semester tables as multi-indexed columns
            for sem in ["Sem1 Details", "Sem2 Details", "Sem3 Details"]:
                if sem in student:
                    for course in student[sem]:
                        course_name = course["Course Name"]
                        student_row[(course_name, "Grade")] = course.get("Grade", "")
                        student_row[(course_name, "Status 1")] = course.get("Status 1", "")
                        student_row[(course_name, "Status 2")] = course.get("Status 2", "")
                        student_row[(course_name, "Credits")] = course.get("Credits", "")

            # Add semester SGPA values
            student_row[("Sem1 SGPA", "")] = student.get("Sem1 SGPA", "N/A")
            student_row[("Sem2 SGPA", "")] = student.get("Sem2 SGPA", "N/A")
            student_row[("Sem3 SGPA", "")] = student.get("Sem3 SGPA", "N/A")

            # Append the student row to the final DataFrame
            all_rows.append(student_row)

        # Create a MultiIndex DataFrame
        multi_index_columns = pd.MultiIndex.from_tuples(student_row.keys(), names=["S.no", ""])
        formatted_df = pd.DataFrame(all_rows, columns=multi_index_columns)

        # Save to Excel
        output_file = f"{file_name}"
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            formatted_df.to_excel(writer, sheet_name='Results', startrow=0)
            worksheet = writer.sheets["Results"]
            # Optional: Adjust formatting (e.g., column widths)
            for col_num, value in enumerate(formatted_df.columns.values):
                worksheet.set_column(col_num, col_num, len(str(value)) + 2)

        return render_template('submit.html', file=output_file)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    


    
from flask import session  # Import session from Flask

import os  # Import os to handle directory operations

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        # Check if a file was uploaded
        print("Files in request:", request.files)
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': "No file part."})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': "No selected file."})
        
        # Create the uploads directory if it doesn't exist
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)  # Create the directory

        # Read the uploaded file
        try:
            # Save the uploaded file to a temporary location
            file_path = os.path.join(uploads_dir, file.filename)  # Ensure the 'uploads' directory exists
            file.save(file_path)  # Save the file

            # Store the file path in the session
            session['file_path'] = file_path

            # Load the DataFrame
            df = pd.read_excel(file_path)
            print(f"Columns in uploaded file: {df.columns.tolist()}")

            # Clean up column headers if needed
            df.columns = [col.strip() for col in df.columns]

            # Extract course names
            courses = [col for col in df.columns if 'Unnamed' not in col and col not in ['S.no', 'Hall Ticket Number', 'Student Name', 'Program', 'Branch', 'Section', 'CGPA', 'Sem1 SGPA', 'Sem2 SGPA', 'Sem3 SGPA']]
            print(f"Courses found: {courses}")

            # Store courses in the session
            session['courses'] = courses

            # Render the graph selection page with available courses
            return render_template('graph_result.html', subjects=courses,file=file_path)

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    elif request.method == 'GET':
        # Render the upload form if it's a GET request
        return render_template('upload_form.html')  # Ensure you have this template

    return jsonify({'status': 'error', 'message': "Invalid request method."})

@app.route('/analyze/graph', methods=['POST'])
def analyze_graph():
    try:
        # Get selected course and graph type
        selected_course = request.form.get('subject')
        graph_type = request.form.get('graphType')

        # Validate inputs
        if not selected_course or not graph_type:
            return jsonify({'status': 'error', 'message': "Course or graph type not provided."})

        # Access the file path from the session
        file_path = session.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return jsonify({'status': 'error', 'message': "No valid file path found in session."})

        # Load the DataFrame
        df = pd.read_excel(file_path, header=[0, 1])
        print("Actual columns in the DataFrame:", df.columns.tolist())

        # Access the courses from the session
        courses = session.get('courses')
        if not courses:
            return jsonify({'status': 'error', 'message': "No courses found in session."})

        # Ensure the static directory exists
        static_dir = os.path.join(os.getcwd(), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)

        # Calculate pass/fail percentages
        if selected_course == "Overall":
            if 'CGPA' not in df.columns:
                return jsonify({'status': 'error', 'message': "CGPA column is missing in the file."})
            
            pass_count = df['CGPA'].apply(pd.to_numeric, errors='coerce').notna().sum()
            fail_count = (df['CGPA'] == "--").sum()
        else:
            status_col = (selected_course, 'Status 2')
            print(status_col)
            if status_col not in df.columns:
                return jsonify({'status': 'error', 'message': f"Column {status_col} is missing in the file."})
            
            pass_count = (df[status_col] == "Not Applicable").sum()
            fail_count = (df[status_col] == "F").sum()
            print(pass_count,fail_count)
        # Generate graph
        labels = ['Pass', 'Fail']
        values = [pass_count, fail_count]
        plt.figure(figsize=(4, 6))
        if graph_type == "bar":
            plt.bar(labels, values, color=['green', 'red'])
            plt.title(f"Pass/Fail Count for {selected_course}")
            plt.ylabel("Count")
        elif graph_type == "pie":
            plt.pie(values, labels=labels, autopct='%1.1f%%', colors=['green', 'red'])
            plt.title(f"Pass/Fail Percentage for {selected_course}")
        elif graph_type == "line":
            plt.plot(labels, values, marker='o', color='blue')
            plt.title(f"Pass/Fail Count for {selected_course}")
            plt.ylabel("Count")
        else:
            return jsonify({'status': 'error', 'message': "Invalid graph type selected."})

        # Save graph
        graph_path = os.path.join(static_dir, f"{selected_course}_graph.png")
        plt.savefig(graph_path)
        plt.close()

        # Render graph result
        return render_template('graph_result.html', subjects=courses, graph_url=f"/static/{selected_course}_graph.png",selected_course=selected_course, graph_type=graph_type)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
