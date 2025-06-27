from flask import Flask, request, render_template, jsonify, session, redirect, url_for, flash, send_file
import pandas as pd
import os
import json
import logging
from datetime import datetime, date
import threading
from werkzeug.utils import secure_filename
from scraper import StudentResultScraper
from data_analyzer import DataAnalyzer

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Flask app initialization
app = Flask(__name__)
app.secret_key = os.environ["SESSION_SECRET"]

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for progress tracking
scraping_progress_data= {}
analysis_progress = {}

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
import numpy as np

def make_json_serializable(obj):
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(i) for i in obj]
    elif isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    else:
        return obj
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/scrape', methods=['GET', 'POST'])
def scrape_results():
    """Handle result scraping requests"""
    if request.method == 'GET':
        return render_template('index.html')
    
    try:
        # Get form data
        choice = request.form.get('choice')
        filename = request.form.get('filename', 'student_results')
        selected_columns = request.form.getlist('columns')  # Get selected columns
        
        if not filename or not filename.strip():
            filename = 'student_results'
        
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        all_roll_numbers = []
        
        # Process roll numbers based on choice
        if choice == 'single':
            single_rollno = request.form.get('single', '').strip()
            if not single_rollno:
                flash('Please provide a valid roll number.', 'error')
                return redirect(url_for('index'))
            all_roll_numbers.append(single_rollno)
            
        elif choice == 'range':
            rollno_from = request.form.get('from', '').strip()
            rollno_to = request.form.get('to', '').strip()
            
            if not rollno_from or not rollno_to:
                flash('Please provide both From and To roll numbers.', 'error')
                return redirect(url_for('index'))
            
            try:
                # Extract numeric parts for range generation
                start_num = int(rollno_from[-2:])
                end_num = int(rollno_to[-2:])
                base_rollno = rollno_from[:-2]
                
                if start_num > end_num:
                    flash('From roll number must be less than or equal to To roll number.', 'error')
                    return redirect(url_for('index'))
                
                # Generate roll numbers in range
                for i in range(start_num, end_num + 1):
                    all_roll_numbers.append(f"{base_rollno}{str(i).zfill(2)}")
                    
            except (ValueError, IndexError):
                flash('Invalid roll number format. Please check your input.', 'error')
                return redirect(url_for('index'))
        else:
            flash('Invalid choice selected.', 'error')
            return redirect(url_for('index'))
        
        # Generate unique session ID for progress tracking
        session_id = f"scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session['scraping_session_id'] = session_id
        scraping_progress_data[session_id] = {
            'total': len(all_roll_numbers),
            'completed': 0,
            'status': 'starting',
            'filename': filename
        }
        
        # Start scraping in background thread
        scraper = StudentResultScraper()
        threading.Thread(
            target=run_scraping_task,
            args=(scraper, all_roll_numbers, filename, session_id, selected_columns)
        ).start()
        
        # Redirect to results page to show progress
        return redirect(url_for('scraping_progress'))
        
    except Exception as e:
        logging.error(f"Error in scrape_results: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

def run_scraping_task(scraper, roll_numbers, filename, session_id, selected_columns=None):
    """Background task for scraping student results"""
    try:
        scraping_progress_data[session_id]['status'] = 'scraping'
        
        # Perform scraping with progress callback
        def progress_callback(completed, total):
            scraping_progress_data[session_id]['completed'] = completed
        
        results = scraper.scrape_parallel(roll_numbers, progress_callback=progress_callback)
        
        # Save results to Excel
        scraping_progress_data[session_id]['status'] = 'saving'
        output_path = os.path.join(UPLOAD_FOLDER, filename)
        scraper.save_to_excel(results, output_path, selected_columns=selected_columns)
        
        scraping_progress_data[session_id]['status'] = 'completed'
        scraping_progress_data[session_id]['file_path'] = output_path
        
    except Exception as e:
        logging.error(f"Scraping task error: {str(e)}")
        scraping_progress_data[session_id]['status'] = 'error'
        scraping_progress_data[session_id]['error'] = str(e)

@app.route('/scraping-progress')
def scraping_progress():
    """Show scraping progress page"""
    session_id = session.get('scraping_session_id')
    if not session_id or session_id not in scraping_progress_data:
        flash('No active scraping session found.', 'error')
        return redirect(url_for('index'))
    
    progress_data = scraping_progress_data[session_id]
    return render_template('results.html', 
                         progress=progress_data, 
                         session_id=session_id,
                         page_type='scraping')

@app.route('/api/scraping-status/<session_id>')
def get_scraping_status(session_id):
    """API endpoint to get scraping progress status"""
    if session_id in scraping_progress_data:
        return jsonify(scraping_progress_data[session_id])
    return jsonify({'status': 'not_found'}), 404

@app.route('/progress/<session_id>')
def get_progress(session_id):
    return jsonify(scraping_progress_data.get(session_id, {
        'status': 'unknown',
        'completed': 0,
        'total': 0
    }))


@app.route('/analyze', methods=['GET', 'POST'])
def analyze_data():
    """Handle data analysis requests"""
    if request.method == 'GET':
        return render_template('analyze.html')
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(url_for('analyze_data'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('analyze_data'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload Excel or CSV files only.', 'error')
            return redirect(url_for('analyze_data'))
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Generate unique session ID for analysis
        session_id = f"analyze_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session['analysis_session_id'] = session_id
        analysis_progress[session_id] = {
            'status': 'starting',
            'filename': filename,
            'file_path': file_path
        }
        
        # Start analysis in background thread
        analyzer = DataAnalyzer()
        threading.Thread(
            target=run_analysis_task,
            args=(analyzer, file_path, session_id)
        ).start()
        
        return redirect(url_for('analysis_progress_'))
        
    except Exception as e:
        logging.error(f"Error in analyze_data: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('analyze_data'))

def run_analysis_task(analyzer, file_path, session_id):
    """Background task for data analysis"""
    try:
        analysis_progress[session_id]['status'] = 'analyzing'
        
        # Perform comprehensive analysis
        results = analyzer.analyze_file(file_path)
        
        analysis_progress[session_id]['status'] = 'completed'
        analysis_progress[session_id]['results'] = results
        
    except Exception as e:
        logging.error(f"Analysis task error: {str(e)}")
        analysis_progress[session_id]['status'] = 'error'
        analysis_progress[session_id]['error'] = str(e)

@app.route('/analysis-progress')
def analysis_progress_():
    """Show analysis progress page"""
    session_id = session.get('analysis_session_id')
    if not session_id or session_id not in analysis_progress:
        flash('No active analysis session found.', 'error')
        return redirect(url_for('analyze_data'))
    
    progress_data = analysis_progress[session_id]
    return render_template('results.html', 
                         progress=progress_data, 
                         session_id=session_id,
                         page_type='analysis')

@app.route('/api/analysis-status/<session_id>')


def get_analysis_status(session_id):
    """API endpoint to get analysis progress status"""
    if session_id in analysis_progress:
        safe_result = make_json_serializable(analysis_progress)
        return jsonify(safe_result[session_id])

    return jsonify({'status': 'not_found'}), 404


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        flash('Error downloading file.', 'error')
        return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('analyze_data'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    logging.error(f"Server error: {str(e)}")
    return render_template('500.html'), 500

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)
