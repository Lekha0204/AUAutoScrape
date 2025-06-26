"""
Enhanced web scraper for student results with improved error handling,
progress tracking, and data validation
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time
import random
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
import os
import xlsxwriter
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StudentResult:
    """Data class for student result information"""
    hall_ticket_number: str
    student_name: str
    program: str
    branch: str
    section: str
    cgpa: str
    semester_details: Dict[str, List[Dict[str, Any]]]  # Dynamic semester storage
    semester_sgpa: Dict[str, str]  # Dynamic SGPA storage
    backlog_count: int = 0
    
    def __post_init__(self):
        """Initialize default values for compatibility"""
        if not hasattr(self, 'semester_details') or not self.semester_details:
            self.semester_details = {}
        if not hasattr(self, 'semester_sgpa') or not self.semester_sgpa:
            self.semester_sgpa = {}
    
    @property
    def sem1_details(self):
        return self.semester_details.get('sem1', [])
    
    @property
    def sem2_details(self):
        return self.semester_details.get('sem2', [])
    
    @property
    def sem3_details(self):
        return self.semester_details.get('sem3', [])
    
    @property
    def sem4_details(self):
        return self.semester_details.get('sem4', [])
    
    @property
    def sem1_sgpa(self):
        return self.semester_sgpa.get('sem1', 'N/A')
    
    @property
    def sem2_sgpa(self):
        return self.semester_sgpa.get('sem2', 'N/A')
    
    @property
    def sem3_sgpa(self):
        return self.semester_sgpa.get('sem3', 'N/A')
    
    @property
    def sem4_sgpa(self):
        return self.semester_sgpa.get('sem4', 'N/A')

class StudentResultScraper:
    """Enhanced web scraper for student results"""
    
    def __init__(self):
        self.website_url = "https://aupulse.campx.in/aupulse/ums/results"
        self.branch_mapping = {
            'b tech in artificial intelligence and machine learning': 'AIML',
            'b tech in artificial intelligence': 'AI',
            'b tech in computer science and engineering': 'CSE',
            'b tech in electronics and communication engineering': 'ECE',
            'b tech in mechanical mngineering': 'ME',
            'b tech in civil engineering': 'CE'
        }
        self.chrome_options = self._setup_chrome_options()
        self.max_retries = 3
        self.request_delay = (1, 3)  # Random delay between requests
        
    def _setup_chrome_options(self) -> Options:
        """Configure Chrome options for scraping"""
        options = Options()
        options.add_argument("--headless")  # Run in background
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to avoid detection
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        return options
    
    def _create_driver(self) -> webdriver.Chrome:
        """Create and configure Chrome driver"""
        try:
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            
            # Execute script to hide automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    def _random_delay(self):
        """Add random delay between requests"""
        delay = random.uniform(self.request_delay[0], self.request_delay[1])
        time.sleep(delay)
    
    def scrape_single_student(self, roll_number: str, driver: webdriver.Chrome) -> Optional[StudentResult]:
        """Scrape data for a single student with enhanced error handling"""
        retries = 0
        
        while retries < self.max_retries:
            try:
                logger.info(f"Scraping roll number: {roll_number} (Attempt {retries + 1})")
                
                # Navigate to the website
                driver.get(self.website_url)
                wait = WebDriverWait(driver, 15)
                
                # Wait for page to load and find roll number input
                roll_no_input = wait.until(
                    EC.presence_of_element_located((By.ID, "rollNo"))
                )
                roll_no_input.clear()
                roll_no_input.send_keys(roll_number)
                
                # Select exam type
                exam_type_dropdown = wait.until(
                    EC.element_to_be_clickable((By.ID, "examType"))
                )
                exam_type_dropdown.click()
                
                general_option = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@data-value='general']"))
                )
                general_option.click()
                
                # Click get result button
                get_result_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Get Result']"))
                )
                get_result_button.click()
                
                # Wait for results to load
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]")
                    )
                )
                
                # Extract student information
                student_data = self._extract_student_data(driver, roll_number)
                
                if student_data:
                    logger.info(f"Successfully scraped data for {roll_number}")
                    self._random_delay()  # Add delay before next request
                    return student_data
                else:
                    logger.warning(f"No data found for roll number: {roll_number}")
                    return None
                    
            except TimeoutException:
                logger.warning(f"Timeout occurred for roll number {roll_number}, attempt {retries + 1}")
                retries += 1
                if retries < self.max_retries:
                    time.sleep(5)  # Wait before retry
                    
            except NoSuchElementException as e:
                logger.error(f"Element not found for roll number {roll_number}: {e}")
                # This might be a valid case where student doesn't exist
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error for roll number {roll_number}: {e}")
                retries += 1
                if retries < self.max_retries:
                    time.sleep(5)
        
        logger.error(f"Failed to scrape roll number {roll_number} after {self.max_retries} attempts")
        return None
    
    def _extract_student_data(self, driver: webdriver.Chrome, roll_number: str) -> Optional[StudentResult]:
        """Extract student data from the results page"""
        try:
            # Extract basic information
            student_name = driver.find_element(
                By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[2]/p"
            ).text.strip()
            
            hall_ticket_number = driver.find_element(
                By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[1]/p"
            ).text.strip()
            
            program_element = driver.find_element(
                By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[1]/div[3]/p"
            ).text.strip()
            
            
            # Determine program and branch
            program = "B Tech" if "B TECH" in program_element else "Unknown"
            branch = self.branch_mapping.get(program_element.lower(), "Unknown")
            section = hall_ticket_number[-3] if len(hall_ticket_number) >= 3 else "Unknown"
            
            # Extract CGPA
            cgpa_element = driver.find_element(
                By.XPATH, "//*[@id='root']/div[2]/div[2]/div[2]/div/div[2]/div[2]"
            ).text.strip()
            cgpa = cgpa_element.split(":")[1].strip() if ":" in cgpa_element else cgpa_element.strip()
            
            # Extract semester tables
            sem1_details, sem2_details, sem3_details,sem4_details = self._extract_semester_tables(driver)
            
            # Calculate backlog count
            backlog_count = self._calculate_backlogs(sem1_details, sem2_details, sem3_details,sem4_details)
            
            # Create semester details and SGPA dictionaries for dynamic storage
            semester_details = {
                'sem1': sem1_details,
                'sem2': sem2_details,
                'sem3': sem3_details,
                'sem4': sem4_details
            }
            
            # Extract SGPA values from the page
            import re

            semester_sgpa = {}
            try:
                # Find all divs that mention SGPA
                sgpa_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'SGPA')]")

                for i, element in enumerate(sgpa_elements):
                    text = element.text.strip()
                    match = re.search(r'(\d+\.\d+)', text)  # extract floating number like 7.43
                    if match:
                        semester_sgpa[f'sem{i+1}'] = match.group(1)
                    else:
                        semester_sgpa[f'sem{i+1}'] = 'N/A'

                # Optional: pad missing semesters up to sem8 as 'N/A'
                for j in range(len(semester_sgpa) + 1, 9):
                    semester_sgpa[f'sem{j}'] = 'N/A'

            except Exception as e:
                logger.warning(f"Could not extract SGPA values: {e}")
                semester_sgpa = {f'sem{i+1}': 'N/A' for i in range(8)}


            return StudentResult(
                hall_ticket_number=hall_ticket_number,
                student_name=student_name,
                program=program,
                branch=branch,
                section=section,
                cgpa=cgpa,
                semester_details=semester_details,
                semester_sgpa=semester_sgpa,
                backlog_count=backlog_count
            )
                
        except Exception as e:
            logger.error(f"Error extracting student data for {roll_number}: {e}")
            return None

    def _extract_semester_tables(self, driver: webdriver.Chrome) -> tuple:
        """Extract semester table data"""
        sem1_details = []
        sem2_details = []
        sem3_details = []
        sem4_details = []
        
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'css-1n196hx'))
                )
                tables = driver.find_elements(By.CLASS_NAME, 'css-1n196hx')
            except:
                logger.warning("Semester tables not found or timeout occurred.")
                tables = []

            
            for index, table in enumerate(tables):
                try:
                    headers = [header.text.strip() for header in table.find_elements(By.TAG_NAME, 'th')]
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    
                    semester_data = []
                    for row in rows[1:]:  # Skip header row
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        if len(cells) >= len(headers):
                            row_data = {}
                            for i, header in enumerate(headers):
                                if i < len(cells):
                                    row_data[header] = cells[i].text.strip()
                            
                            # Handle status columns
                            logger.info(f"Table {index + 1} headers: {headers}")

                            status = row_data.get("Status", "")
                            print("@@@@@@DEBUG status ",status)
                            row_data["Status"] = status
                            # row_data["Status 2"] = "Not Applicable"
                            
                            semester_data.append(row_data)
                    
                    # Store semester data dynamically - detect up to any number of semesters
                    if index == 0:
                        sem1_details = semester_data
                    elif index == 1:
                        sem2_details = semester_data
                    elif index == 2:
                        sem3_details = semester_data
                    elif index == 3:
                        sem4_details = semester_data
                    else:
                        # Handle additional semesters (sem4, sem5, etc.)
                        logger.info(f"Found additional semester table {index + 1} with {len(semester_data)} courses")
                        
                except Exception as e:
                    logger.warning(f"Error processing table {index}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error extracting semester tables: {e}")
        
        # For backward compatibility, also return all detected semesters as a dict
        all_semesters = {'sem1': sem1_details, 'sem2': sem2_details, 'sem3': sem3_details, 'sem4': sem4_details}
        
        # If more than 3 tables were found, add them to the response
        if len(tables) > 4:
            logger.info(f"Total of {len(tables)} semester tables detected")
            
        return sem1_details, sem2_details, sem3_details, sem4_details
    
    def _calculate_backlogs(self, sem1_details: List[Dict], sem2_details: List[Dict], sem3_details: List[Dict],sem4_details: List[Dict]) -> int:
        """Calculate total number of backlogs"""
        backlog_count = 0
        all_semesters = [sem1_details, sem2_details, sem3_details, sem4_details]
        
        for semester in all_semesters:
            for course in semester:
                status = course.get("Status", "").upper()
                grade = course.get("Grade", "").upper()
                
                # Count as backlog if failed or absent
                if any(keyword in status for keyword in ["F", "Ab", "RA"]) or grade in ["F", "Ab"]:
                    backlog_count += 1
        
        return backlog_count
    
    def scrape_parallel(self, roll_numbers: List[str], max_threads: int = 3, progress_callback: Optional[Callable] = None) -> List[StudentResult]:
        """Scrape multiple students in parallel with progress tracking"""
        results = []
        completed = 0
        total = len(roll_numbers)
        
        logger.info(f"Starting parallel scraping for {total} roll numbers with {max_threads} threads")
        
        # Split roll numbers into chunks for each thread
        chunk_size = max(1, len(roll_numbers) // max_threads)
        chunks = [roll_numbers[i:i + chunk_size] for i in range(0, len(roll_numbers), chunk_size)]
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Submit tasks
            future_to_chunk = {}
            for chunk in chunks:
                future = executor.submit(self._scrape_chunk, chunk)
                future_to_chunk[future] = chunk
            
            # Process completed tasks
            for future in as_completed(future_to_chunk):
                chunk_results = future.result()
                results.extend(chunk_results)
                completed += len(future_to_chunk[future])
                
                # Call progress callback if provided
                if progress_callback:
                    progress_callback(completed, total)
                
                logger.info(f"Progress: {completed}/{total} completed")
        
        logger.info(f"Scraping completed. Successfully scraped {len(results)} out of {total} roll numbers")
        return results
    
    def _scrape_chunk(self, roll_numbers: List[str]) -> List[StudentResult]:
        """Scrape a chunk of roll numbers in a single thread"""
        results = []
        driver = None
        
        try:
            driver = self._create_driver()
            
            for roll_number in roll_numbers:
                try:
                    result = self.scrape_single_student(roll_number, driver)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error scraping {roll_number} in chunk: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in chunk processing: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    logger.error(f"Error closing driver: {e}")
        
        return results
    
    def save_to_excel(self, results: List[StudentResult], filename: str, selected_columns: List[str] = None):
        """Save results to Excel with enhanced formatting"""
        print(selected_columns)
        if not results:
            raise ValueError("No results to save")

        logger.info(f"Saving {len(results)} results to {filename}")

        all_rows = []

        for student in results:
            student_row = {
                ("Hall Ticket Number", ""): student.hall_ticket_number,
                ("Student Name", ""): student.student_name,
                ("Program", ""): student.program,
                ("Branch", ""): student.branch,
                ("Section", ""): student.section,
                ("CGPA", ""): student.cgpa,
                ("No of Backlogs", ""): student.backlog_count
            }

            # Add semester details
            for sem_name, sem_data in [
                ("Sem1 Details", student.sem1_details),
                ("Sem2 Details", student.sem2_details),
                ("Sem3 Details", student.sem3_details),
                ("Sem4 Details", student.sem4_details)
            ]:
                if sem_name in selected_columns or selected_columns is None:
                    for course in sem_data:
                        course_name = course.get("Course Name", "Unknown Course")
                        student_row[(course_name, "Grade")] = course.get("Grade", "")
                        student_row[(course_name, "Status")] = course.get("Status", "")
                        student_row[(course_name, "Credits")] = course.get("Credits", "")

            # Add SGPA values if semN SGPA is selected
            if selected_columns is None or "Sem1 Details" in selected_columns:
                student_row[("Sem1 SGPA", "")] = student.sem1_sgpa
            if selected_columns is None or "Sem2 Details" in selected_columns:
                student_row[("Sem2 SGPA", "")] = student.sem2_sgpa
            if selected_columns is None or "Sem3 Details" in selected_columns:
                student_row[("Sem3 SGPA", "")] = student.sem3_sgpa
            if selected_columns is None or "Sem4 Details" in selected_columns:
                student_row[("Sem4 SGPA", "")] = student.sem4_sgpa

            all_rows.append(student_row)

        # Create DataFrame
        if all_rows:
            multi_index_columns = pd.MultiIndex.from_tuples(
                list(all_rows[0].keys()), names=["Course/Field", "Detail"]
            )
            df = pd.DataFrame(all_rows, columns=multi_index_columns)

            #  Filter columns if selected_columns is provided
            # if selected_columns:
            #     df = df[[col for col in df.columns if col[0] in selected_columns]]

            #  Sort by last 2 digits of roll number
            df = df.sort_values(
                by=("Hall Ticket Number", ""),
                key=lambda col: col.astype(str).str[-2:].astype(int)
            )
            df.index = range(1, len(df) + 1)

            #  Save to Excel
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Student Results', startrow=0)
                workbook = writer.book
                worksheet = writer.sheets['Student Results']

                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })

                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num + 1, str(value[0]), header_format)
                    worksheet.write(1, col_num + 1, str(value[1]), header_format)
                    worksheet.set_column(col_num + 1, col_num + 1, 15)

                # Set column width
                for col_num in range(len(df.columns)):
                    worksheet.set_column(col_num + 1, col_num + 1, 12)

        logger.info(f"Results successfully saved to {filename}")
