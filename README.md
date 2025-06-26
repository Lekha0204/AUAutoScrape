# Student Result Analysis System

A comprehensive Flask-based web application for scraping and analyzing student academic results with advanced data visualization and customizable Excel exports.

## Features

- **Web Scraping**: Automatically scrape student results from university portals
- **Dynamic Semester Detection**: Automatically detects and handles any number of semester tables (sem1, sem2, sem3, sem4, etc.)
- **Column Selection**: Choose which data fields to include in Excel exports via checkbox interface
- **Data Analysis**: Comprehensive statistical analysis with interactive charts
- **Professional UI**
- **Excel Export**: Customizable Excel reports with enhanced formatting

## Prerequisites

- Python 3.8 or higher
- Chrome browser (for web scraping)
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd student-result-analysis
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   # Create .env file
   echo "SESSION_SECRET=your-secret-key-here" > .env
   
   # On Windows Command Prompt
   set SESSION_SECRET=your-secret-key-here
   
   # On Windows PowerShell
   $env:SESSION_SECRET="your-secret-key-here"
   
   # On macOS/Linux
   export SESSION_SECRET="your-secret-key-here"
   ```

## Running the Application

1. **Start the Flask application**
   ```bash
   python app.py
   ```
   
   Or using Gunicorn (recommended for production):
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

2. **Access the application**
   Open your browser and navigate to: `http://localhost:5000`

## Usage

### Web Scraping
1. Choose between individual roll numbers or range-based scraping
2. Select which columns to include in the Excel export
3. Enter roll numbers or specify a range
4. Click "Start Scraping" to begin the process
5. Monitor progress in real-time
6. Download the generated Excel file

### Data Analysis
1. Upload an existing Excel or CSV file
2. View comprehensive statistical analysis
3. Explore interactive charts and visualizations
4. Download enhanced analysis reports

## Project Structure

```
student-result-analysis/
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── scraper.py            # Web scraping functionality
├── data_analyzer.py      # Data analysis engine
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css    # Custom styling
│   └── js/
│       ├── main.js      # Main JavaScript
│       └── charts.js    # Chart functionality
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Main dashboard
│   ├── analyze.html     # Analysis page
│   └── progress.html    # Progress tracking
└── uploads/             # File upload directory
```

## Configuration

### Environment Variables
- `SESSION_SECRET`: Secret key for Flask sessions (required)
- `DATABASE_URL`: Database connection string (optional)

### Customization
- Modify `scraper.py` to adapt to different university portals
- Update CSS variables in `static/css/style.css` for theme customization
- Adjust analysis parameters in `data_analyzer.py`

## Dependencies

The application requires the following Python packages:
- Flask (web framework)
- Selenium (web scraping)
- Pandas (data manipulation)
- XlsxWriter (Excel generation)
- Matplotlib/Seaborn (data visualization)
- WebDriver Manager (Chrome driver management)

## Browser Requirements

For web scraping functionality:
- Chrome browser must be installed
- ChromeDriver is automatically managed by webdriver-manager

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Ensure Chrome browser is installed
   - Check internet connection for automatic driver download

2. **Permission errors**
   - Run with appropriate permissions
   - Check file system permissions for uploads/ directory

3. **Port already in use**
   - Change port in app.py or kill existing process
   - Use different port: `python app.py --port 5001`

4. **Module not found errors**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

## Development

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Include error handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed description

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.