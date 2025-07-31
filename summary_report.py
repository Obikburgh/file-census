#!/usr/bin/env python3
"""
Summary Report Generator - Create markdown summary from file census data
"""

import os
import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import argparse


def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def read_csv_data(csv_file):
    """Read file data from CSV file"""
    files_data = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert size to integer
                row['size_bytes'] = int(row['size_bytes'])
                # Parse modified date
                row['modified_datetime'] = datetime.strptime(row['modified_date'], '%Y-%m-%d %H:%M:%S')
                files_data.append(row)
    except FileNotFoundError:
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    return files_data


def analyze_data(files_data):
    """Analyze file data and return statistics"""
    analysis = {}
    
    # Total files
    analysis['total_files'] = len(files_data)
    
    # Total size
    total_size = sum(file_info['size_bytes'] for file_info in files_data)
    analysis['total_size'] = total_size
    analysis['total_size_formatted'] = format_file_size(total_size)
    
    # Top 10 largest files
    largest_files = sorted(files_data, key=lambda x: x['size_bytes'], reverse=True)[:10]
    analysis['largest_files'] = largest_files
    
    # File type breakdown
    extension_counts = Counter()
    extension_sizes = defaultdict(int)
    
    for file_info in files_data:
        ext = file_info['extension'].lower()
        if not ext:
            ext = '(no extension)'
        extension_counts[ext] += 1
        extension_sizes[ext] += file_info['size_bytes']
    
    analysis['file_types'] = []
    for ext, count in extension_counts.most_common():
        analysis['file_types'].append({
            'extension': ext,
            'count': count,
            'total_size': extension_sizes[ext],
            'total_size_formatted': format_file_size(extension_sizes[ext])
        })
    
    # Files by year
    year_counts = defaultdict(int)
    year_sizes = defaultdict(int)
    
    for file_info in files_data:
        year = file_info['modified_datetime'].year
        year_counts[year] += 1
        year_sizes[year] += file_info['size_bytes']
    
    analysis['files_by_year'] = []
    for year in sorted(year_counts.keys(), reverse=True):
        analysis['files_by_year'].append({
            'year': year,
            'count': year_counts[year],
            'total_size': year_sizes[year],
            'total_size_formatted': format_file_size(year_sizes[year])
        })
    
    return analysis


def generate_markdown_report(analysis, output_file):
    """Generate markdown report"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    markdown_content = f"""# File Census Summary Report

Generated on: {timestamp}

## Overview

- **Total Files**: {analysis['total_files']:,}
- **Total Size**: {analysis['total_size_formatted']} ({analysis['total_size']:,} bytes)

## Top 10 Largest Files

| Rank | Filename | Size | Modified Date |
|------|----------|------|---------------|
"""
    
    for i, file_info in enumerate(analysis['largest_files'], 1):
        filename = file_info['filename'].replace('|', '\\|')  # Escape pipes for markdown
        markdown_content += f"| {i} | `{filename}` | {file_info['size_formatted']} | {file_info['modified_date']} |\n"
    
    markdown_content += "\n## File Type Breakdown\n\n"
    markdown_content += "| Extension | Count | Total Size | Percentage |\n"
    markdown_content += "|-----------|-------|------------|------------|\n"
    
    for type_info in analysis['file_types'][:20]:  # Top 20 file types
        percentage = (type_info['count'] / analysis['total_files']) * 100
        ext_display = type_info['extension'] if type_info['extension'] != '(no extension)' else '*no extension*'
        markdown_content += f"| `{ext_display}` | {type_info['count']:,} | {type_info['total_size_formatted']} | {percentage:.1f}% |\n"
    
    if len(analysis['file_types']) > 20:
        remaining = len(analysis['file_types']) - 20
        markdown_content += f"| *...and {remaining} more* | | | |\n"
    
    markdown_content += "\n## Files by Year\n\n"
    markdown_content += "| Year | Count | Total Size | Percentage |\n"
    markdown_content += "|------|-------|------------|------------|\n"
    
    for year_info in analysis['files_by_year']:
        percentage = (year_info['count'] / analysis['total_files']) * 100
        markdown_content += f"| {year_info['year']} | {year_info['count']:,} | {year_info['total_size_formatted']} | {percentage:.1f}% |\n"
    
    # Add file type summary for Obsidian tags
    markdown_content += "\n## File Extensions Summary\n\n"
    for type_info in analysis['file_types'][:10]:
        ext = type_info['extension'].replace('.', '') if type_info['extension'].startswith('.') else type_info['extension']
        if ext != '(no extension)':
            markdown_content += f"#{ext} "
    
    markdown_content += "\n\n---\n\n*Report generated by File Census Tool*\n"
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Summary report created: {Path(output_file).absolute()}")
    except Exception as e:
        print(f"Error writing markdown file: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Generate markdown summary report from CSV data')
    parser.add_argument('csv_file', 
                       help='Input CSV file from file census')
    parser.add_argument('--output', '-o', 
                       help='Output markdown file (default: auto-generated name)')
    
    args = parser.parse_args()
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"file_census_summary_{timestamp}.md"
    
    print(f"Reading data from: {args.csv_file}")
    files_data = read_csv_data(args.csv_file)
    
    print("Analyzing data...")
    analysis = analyze_data(files_data)
    
    print("Generating markdown report...")
    generate_markdown_report(analysis, output_file)


if __name__ == "__main__":
    main()