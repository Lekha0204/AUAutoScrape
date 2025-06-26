"""
Comprehensive data analyzer for student results with advanced statistical analysis,
data visualization, and performance insights
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Set non-GUI backend
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Comprehensive data analyzer for student academic performance"""
    
    def __init__(self):
        self.grade_points = {
            'O':10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'C': 5, 'F': 0, 'Ab': 0
        }
        self.grade_categories = {
            'Excellent': ['A+', 'A'],
            'Good': ['B+', 'B'],
            'Average': ['C+', 'C'],
            'Below Average': ['D'],
            'Fail': ['F', 'RA']
        }
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on uploaded data file
        
        Args:
            file_path: Path to the uploaded Excel/CSV file
            
        Returns:
            Dictionary containing all analysis results
        """
        try:
            logger.info(f"Starting analysis of file: {file_path}")
            
            # Load data
            df = self._load_data(file_path)
            df.replace(['--', 'NA', 'null', ''], np.nan, inplace=True)

            if df is None or df.empty:
                raise ValueError("Unable to load data from file or file is empty")


            
            # Perform comprehensive analysis
            analysis_results = {
                'file_info': self._get_file_info(file_path, df),
                'summary_statistics': self._calculate_summary_statistics(df),
                'grade_distribution': self._analyze_grade_distribution(df),
                'performance_trends': self._analyze_performance_trends(df),
                'branch_comparison': self._analyze_branch_performance(df),
                'subject_performance': self._analyze_subject_performance(df),
                'student_rankings': self._calculate_student_rankings(df),
                'statistical_insights': self._generate_statistical_insights(df),
                'detailed_stats': self._generate_detailed_statistics(df),
                'recommendations': self._generate_recommendations(df),
                'charts': self._prepare_chart_data(df)
            }
            logger.info("Loading file info...")
            analysis_results['file_info'] = self._get_file_info(file_path, df)

            logger.info("Calculating summary statistics...")
            analysis_results['summary_statistics'] = self._calculate_summary_statistics(df)
            # Add metadata
            analysis_results['analysis_timestamp'] = datetime.now().isoformat()
            analysis_results['total_students'] = len(df)
            
            logger.info("Analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")
    
    def _load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load data from Excel or CSV file"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                # Try to read with multi-index if it exists
                try:
                    df = pd.read_excel(file_path, header=[0, 1])
                except:
                    df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            logger.info(f"Loaded data with shape: {df.shape}")
            return self._clean_data(df)
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return None
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the data"""
        try:
            # Handle multi-index columns
            if isinstance(df.columns, pd.MultiIndex):
                # Flatten multi-index columns
                df.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in df.columns]
            
            # Remove empty rows and columns
            df = df.dropna(how='all').dropna(axis=1, how='all')
            
            # Clean column names
            df.columns = df.columns.astype(str)
            df.columns = [col.strip().replace('\n', ' ').replace('\r', '') for col in df.columns]
            
            # Convert CGPA column to numeric if it exists
            cgpa_cols = [col for col in df.columns if 'cgpa' in col.lower() or 'gpa' in col.lower()]
            for col in cgpa_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            return df
    
    def _get_file_info(self, file_path: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic file information"""
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        return {
            'filename': os.path.basename(file_path),
            'file_size': file_size,
            'rows': len(df),
            'columns': len(df.columns),
            'file_type': os.path.splitext(file_path)[1],
            'upload_time': datetime.now().isoformat()
        }
    
    def _calculate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive summary statistics"""
        try:
            summary = {
                'total_students': len(df),
                'total_columns': len(df.columns),
                'data_completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            }
            
            # Find CGPA columns
            cgpa_cols = [col for col in df.columns if 'cgpa' in col.lower()]
            if cgpa_cols:
                cgpa_data = df[cgpa_cols[0]].dropna()
                if len(cgpa_data) > 0:
                    summary.update({
                        'average_cgpa': round(cgpa_data.mean(), 2),
                        'median_cgpa': round(cgpa_data.median(), 2),
                        'min_cgpa': round(cgpa_data.min(), 2),
                        'max_cgpa': round(cgpa_data.max(), 2),
                        'std_cgpa': round(cgpa_data.std(), 2)
                    })
            
            # # Find branch information
            # branch_cols = [col for col in df.columns if 'branch' in col.lower()]
            # if branch_cols:
            #     branches = df[branch_cols[0]].dropna().unique()
            #     # summary['total_branches'] = len(branches)
            #     # summary['branches'] = branches.tolist()
            
            # Calculate pass rate 
            if cgpa_cols:
                total_count = len(cgpa_data)
                cgpa_data = df[cgpa_cols[0]].dropna()
                if len(cgpa_data) > 0:
                    summary['pass_percentage'] = round(( len(cgpa_data) /total_count) * 100, 1)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calculating summary statistics: {str(e)}")
            return {'total_students': len(df), 'error': str(e)}
    
    def _analyze_grade_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze grade distribution across all subjects"""
        try:
            grade_data = {}
            grade_counts = {grade: 0 for grade in self.grade_points.keys()}
            
            # Find grade columns
            grade_cols = [col for col in df.columns if 'grade' in col.lower() and col.lower() != 'grade']
            
            for col in grade_cols:
                grades = df[col].dropna().astype(str).str.upper()
                for grade in grades:
                    if grade in grade_counts:
                        grade_counts[grade] += 1
            
            # Calculate percentages
            total_grades = sum(grade_counts.values())
            grade_percentages = {}
            if total_grades > 0:
                grade_percentages = {
                    grade: round((count / total_grades) * 100, 1) 
                    for grade, count in grade_counts.items()
                }
            
            # Category-wise analysis
            category_counts = {}
            for category, grades in self.grade_categories.items():
                category_counts[category] = sum(grade_counts[grade] for grade in grades)
            
            return {
                'grades': list(grade_counts.keys()),
                'counts': list(grade_counts.values()),
                'percentages': grade_percentages,
                'category_distribution': category_counts,
                'total_grades_analyzed': total_grades
            }
            
        except Exception as e:
            logger.error(f"Error analyzing grade distribution: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_performance_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance trends across semesters"""
        try:
            trends = {}
            
            # Find semester-wise CGPA/SGPA columns
            sem_cols = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'sem' in col_lower and ('gpa' in col_lower or 'cgpa' in col_lower):
                    if 'sem1' in col_lower or 'semester 1' in col_lower:
                        sem_cols['Semester 1'] = col
                    elif 'sem2' in col_lower or 'semester 2' in col_lower:
                        sem_cols['Semester 2'] = col
                    elif 'sem3' in col_lower or 'semester 3' in col_lower:
                        sem_cols['Semester 3'] = col
                    elif 'sem4' in col_lower or 'semester 4' in col_lower:
                        sem_cols['Semester 4'] = col
            
            if sem_cols:
                semesters = []
                cgpa_trends = []
                pass_rates = []
                
                for sem_name, col_name in sem_cols.items():
                    sem_data = pd.to_numeric(df[col_name], errors='coerce').dropna()
                    if len(sem_data) > 0:
                        semesters.append(sem_name)
                        cgpa_trends.append(round(sem_data.mean(), 2))
                        pass_count = len(sem_data[sem_data >= 5.0])
                        pass_rates.append(round((pass_count / len(sem_data)) * 100, 1))
                
                trends = {
                    'semesters': semesters,
                    'cgpa_trends': cgpa_trends,
                    'pass_rates': pass_rates
                }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_branch_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance comparison across branches"""
        try:
            branch_analysis = {}
            
            # Find branch and CGPA columns
            branch_cols = [col for col in df.columns if 'branch' in col.lower()]
            cgpa_cols = [col for col in df.columns if 'cgpa' in col.lower()]
            
            if branch_cols and cgpa_cols:
                branch_col = branch_cols[0]
                cgpa_col = cgpa_cols[0]
                
                # Group by branch and calculate statistics
                branch_stats = df.groupby(branch_col)[cgpa_col].agg([
                    'count', 'mean', 'median', 'std', 'min', 'max'
                ]).round(2)
                
                branches = branch_stats.index.tolist()
                avg_cgpa = branch_stats['mean'].tolist()
                student_counts = branch_stats['count'].tolist()
                
                # Calculate pass rates by branch
                pass_rates = []
                for branch in branches:
                    branch_data = df[df[branch_col] == branch][cgpa_col]
                    branch_data = pd.to_numeric(branch_data, errors='coerce').dropna()
                    if len(branch_data) > 0:
                        pass_count = len(branch_data[branch_data >= 5.0])
                        pass_rates.append(round((pass_count / len(branch_data)) * 100, 1))
                    else:
                        pass_rates.append(0)
                
                branch_analysis = {
                    'branches': branches,
                    'avg_cgpa': avg_cgpa,
                    'student_counts': student_counts,
                    'pass_rates': pass_rates,
                    'detailed_stats': branch_stats.to_dict('index')
                }
            
            return branch_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing branch performance: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_subject_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance in individual subjects"""
        try:
            subject_analysis = {}
            
            # Find subject/course columns with grades
            subject_cols = [col for col in df.columns if 'grade' in col.lower() and '_grade' in col.lower()]
            
            if subject_cols:
                subjects = []
                avg_grade_points = []
                pass_rates = []
                
                for col in subject_cols[:10]:  # Limit to first 10 subjects
                    subject_name = col.replace('_Grade', '').replace('_grade', '')
                    subjects.append(subject_name)
                    
                    # Convert grades to grade points
                    grades = df[col].dropna().astype(str).str.upper()
                    grade_points = [self.grade_points.get(grade, 0) for grade in grades]
                    
                    if grade_points:
                        avg_grade_points.append(round(np.mean(grade_points), 2))
                        pass_count = len([gp for gp in grade_points if gp >= 4])
                        pass_rates.append(round((pass_count / len(grade_points)) * 100, 1))
                    else:
                        avg_grade_points.append(0)
                        pass_rates.append(0)
                
                subject_analysis = {
                    'subjects': subjects,
                    'grade_points': avg_grade_points,
                    'pass_rates': pass_rates
                }
            
            return subject_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing subject performance: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_student_rankings(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate student rankings based on CGPA"""
        try:
            rankings = {}
            
            # Find relevant columns
            name_cols = [col for col in df.columns if 'name' in col.lower()]
            cgpa_cols = [col for col in df.columns if 'cgpa' in col.lower()]
            branch_cols = [col for col in df.columns if 'branch' in col.lower()]
            
            if name_cols and cgpa_cols:
                name_col = name_cols[0]
                cgpa_col = cgpa_cols[0]
                
                # Create ranking dataframe
                ranking_df = df[[name_col, cgpa_col]].copy()
                if branch_cols:
                    ranking_df['Branch'] = df[branch_cols[0]]
                
                # Convert CGPA to numeric and sort
                ranking_df[cgpa_col] = pd.to_numeric(ranking_df[cgpa_col], errors='coerce')
                ranking_df = ranking_df.dropna().sort_values(cgpa_col, ascending=False)
                ranking_df['Rank'] = range(1, len(ranking_df) + 1)
                
                # Top performers
                top_10 = ranking_df.head(10).to_dict('records')
                
                rankings = {
                    'top_performers': top_10,
                    'total_ranked': len(ranking_df),
                    'average_cgpa': round(ranking_df[cgpa_col].mean(), 2),
                    'median_cgpa': round(ranking_df[cgpa_col].median(), 2)
                }
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error calculating rankings: {str(e)}")
            return {'error': str(e)}
    
    def _generate_statistical_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate advanced statistical insights"""
        try:
            insights = {}
            
            # Find CGPA column
            cgpa_cols = [col for col in df.columns if 'cgpa' in col.lower()]
            if cgpa_cols:
                cgpa_data = pd.to_numeric(df[cgpa_cols[0]], errors='coerce').dropna()
                
                if len(cgpa_data) > 1:
                    # Distribution analysis
                    skewness = stats.skew(cgpa_data)
                    kurtosis = stats.kurtosis(cgpa_data)
                    
                    # Normality test
                    _, p_value = stats.normaltest(cgpa_data)
                    is_normal = p_value > 0.05
                    
                    # Quartiles
                    q1 = cgpa_data.quantile(0.25)
                    q3 = cgpa_data.quantile(0.75)
                    iqr = q3 - q1
                    
                    insights = {
                        'distribution_shape': {
                            'skewness': round(skewness, 3),
                            'kurtosis': round(kurtosis, 3),
                            'is_normal_distribution': is_normal
                        },
                        'quartile_analysis': {
                            'q1': round(q1, 2),
                            'q3': round(q3, 2),
                            'iqr': round(iqr, 2)
                        },
                        'outlier_analysis': self._detect_outliers(cgpa_data),
                        'performance_categories': self._categorize_performance(cgpa_data)
                    }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating statistical insights: {str(e)}")
            return {'error': str(e)}
    
    def _detect_outliers(self, data: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        try:
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            return {
                'outlier_count': len(outliers),
                'outlier_percentage': round((len(outliers) / len(data)) * 100, 2),
                'lower_bound': round(lower_bound, 2),
                'upper_bound': round(upper_bound, 2)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _categorize_performance(self, cgpa_data: pd.Series) -> Dict[str, Any]:
        """Categorize students based on performance"""
        try:
            categories = {
                'Excellent (>= 8.0)': len(cgpa_data[cgpa_data >= 8.0]),
                'Good (7.0 - 7.9)': len(cgpa_data[(cgpa_data >= 7.0) & (cgpa_data < 8.0)]),
                'Average (6.0 - 6.9)': len(cgpa_data[(cgpa_data >= 6.0) & (cgpa_data < 7.0)]),
                'Below Average (5.0 - 5.9)': len(cgpa_data[(cgpa_data >= 5.0) & (cgpa_data < 6.0)]),
                'Poor (< 5.0)': len(cgpa_data[cgpa_data < 5.0])
            }
            
            total = len(cgpa_data)
            percentages = {
                category: round((count / total) * 100, 1) 
                for category, count in categories.items()
            }
            
            return {
                'counts': categories,
                'percentages': percentages
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_detailed_statistics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate detailed statistics table"""
        try:
            stats_table = []
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if 'cgpa' in col.lower() or 'gpa' in col.lower():
                    data = df[col].dropna()
                    if len(data) > 0:
                        stats_table.append({
                            'Metric': col,
                            'Count': len(data),
                            'Mean': round(data.mean(), 2),
                            'Median': round(data.median(), 2),
                            'Std Dev': round(data.std(), 2),
                            'Min': round(data.min(), 2),
                            'Max': round(data.max(), 2)
                        })
            
            return stats_table
            
        except Exception as e:
            logger.error(f"Error generating detailed statistics: {str(e)}")
            return []
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        try:
            recommendations = []
            
            # Find CGPA column
            cgpa_cols = [col for col in df.columns if 'cgpa' in col.lower()]
            if cgpa_cols:
                cgpa_data = pd.to_numeric(df[cgpa_cols[0]], errors='coerce').dropna()
                
                if len(cgpa_data) > 0:
                    avg_cgpa = cgpa_data.mean()
                    pass_rate = (len(cgpa_data[cgpa_data >= 5.0]) / len(cgpa_data)) * 100
                    
                    # CGPA-based recommendations
                    if avg_cgpa < 6.0:
                        recommendations.append("Overall academic performance needs significant improvement. Consider implementing additional support programs.")
                    elif avg_cgpa < 7.0:
                        recommendations.append("Academic performance is moderate. Focus on improving teaching methodologies and student engagement.")
                    else:
                        recommendations.append("Good academic performance observed. Continue current practices and explore advanced learning opportunities.")
                    
                    # Pass rate recommendations
                    if pass_rate < 70:
                        recommendations.append(f"Pass rate is {pass_rate:.1f}%, which requires immediate attention. Implement remedial classes and counseling.")
                    elif pass_rate < 85:
                        recommendations.append(f"Pass rate is {pass_rate:.1f}%. Consider additional tutorial sessions for struggling students.")
                    
                    # Grade distribution recommendations
                    grade_dist = self._analyze_grade_distribution(df)
                    if 'category_distribution' in grade_dist:
                        fail_count = grade_dist['category_distribution'].get('Fail', 0)
                        total_grades = grade_dist.get('total_grades_analyzed', 1)
                        fail_rate = (fail_count / total_grades) * 100 if total_grades > 0 else 0
                        
                        if fail_rate > 20:
                            recommendations.append("High failure rate detected in individual subjects. Review curriculum difficulty and teaching methods.")
            
            # Branch-wise recommendations
            branch_analysis = self._analyze_branch_performance(df)
            if 'branches' in branch_analysis and len(branch_analysis['branches']) > 1:
                recommendations.append("Performance varies across branches. Consider sharing best practices from high-performing branches.")
            
            if not recommendations:
                recommendations.append("Data analysis completed successfully. Monitor performance trends regularly for continuous improvement.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return ["Unable to generate recommendations due to data analysis error."]
    
    def _prepare_chart_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for charts and visualizations"""
        try:
            chart_data = {}
            
            # Grade distribution chart data
            grade_dist = self._analyze_grade_distribution(df)
            if 'grades' in grade_dist and 'counts' in grade_dist:
                chart_data['grade_distribution'] = {
                    'labels': grade_dist['grades'],
                    'data': grade_dist['counts']
                }
            
            # Performance trends chart data
            perf_trends = self._analyze_performance_trends(df)
            if 'semesters' in perf_trends:
                chart_data['performance_trends'] = perf_trends
            
            # Branch comparison chart data
            branch_analysis = self._analyze_branch_performance(df)
            if 'branches' in branch_analysis:
                chart_data['branch_comparison'] = {
                    'labels': branch_analysis['branches'],
                    'data': branch_analysis['avg_cgpa']
                }
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing chart data: {str(e)}")
            return {}