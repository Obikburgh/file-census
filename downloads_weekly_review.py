#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Downloads Weekly Review - Generate Obsidian-formatted markdown for weekly file review
Outputs to stdout for Templater integration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timedelta
import argparse
from urllib.parse import quote

# Configure UTF-8 encoding for Windows
if os.name == 'nt':  # Windows
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


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


def format_date(timestamp):
    """Format timestamp for readable display"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')


def get_downloads_folder():
    """Get Windows Downloads folder path"""
    if os.name == 'nt':  # Windows
        downloads_path = Path.home() / 'Downloads'
    else:  # Fallback for other systems
        downloads_path = Path.home() / 'Downloads'
    
    return downloads_path


def scan_downloads_folder(folder_path):
    """
    Scan Downloads folder recursively and return file information and subfolder data
    Returns tuple: (files_data, subfolders_data)
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"Error: Downloads folder not found: {folder_path}", file=sys.stderr)
        sys.exit(1)
    
    if not folder_path.is_dir():
        print(f"Error: Path is not a directory: {folder_path}", file=sys.stderr)
        sys.exit(1)
    
    files_data = []
    subfolders_data = []
    
    try:
        # Scan all files recursively
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                try:
                    stat_info = file_path.stat()
                    
                    file_info = {
                        'name': file_path.name,
                        'size_bytes': stat_info.st_size,
                        'size_formatted': format_file_size(stat_info.st_size),
                        'modified_time': stat_info.st_mtime,
                        'modified_formatted': format_date(stat_info.st_mtime),
                        'path': str(file_path),
                        'relative_path': str(file_path.relative_to(folder_path))
                    }
                    
                    files_data.append(file_info)
                    
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
        
        # Analyze subfolders (direct subdirectories only)
        for subfolder_path in folder_path.iterdir():
            if subfolder_path.is_dir():
                try:
                    # Count files and calculate total size in this subfolder
                    file_count = 0
                    total_size = 0
                    
                    for file_path in subfolder_path.rglob('*'):
                        if file_path.is_file():
                            try:
                                stat_info = file_path.stat()
                                file_count += 1
                                total_size += stat_info.st_size
                            except (OSError, PermissionError):
                                continue
                    
                    if file_count > 0:  # Only include folders with files
                        # Get folder creation/modification time
                        folder_stat = subfolder_path.stat()
                        
                        subfolder_info = {
                            'name': subfolder_path.name,
                            'file_count': file_count,
                            'total_size': total_size,
                            'total_size_formatted': format_file_size(total_size),
                            'created_time': folder_stat.st_ctime,
                            'created_formatted': format_date(folder_stat.st_ctime),
                            'path': str(subfolder_path)
                        }
                        subfolders_data.append(subfolder_info)
                        
                except (OSError, PermissionError):
                    # Skip folders we can't access
                    continue
                    
    except PermissionError:
        print(f"Error: Permission denied accessing folder: {folder_path}", file=sys.stderr)
        sys.exit(1)
    
    return files_data, subfolders_data


def analyze_files(files_data, subfolders_data):
    """Analyze file data and return various statistics"""
    if not files_data:
        return {
            'total_files': 0,
            'total_size': 0,
            'average_size': 0,
            'oldest_date': None,
            'newest_date': None,
            'largest_files': [],
            'recent_files': [],
            'oldest_files': [],
            'subfolders': []
        }
    
    # Basic stats
    total_files = len(files_data)
    total_size = sum(f['size_bytes'] for f in files_data)
    average_size = total_size / total_files if total_files > 0 else 0
    
    # Date range
    oldest_date = min(f['modified_time'] for f in files_data)
    newest_date = max(f['modified_time'] for f in files_data)
    
    # Top 15 largest files
    largest_files = sorted(files_data, key=lambda x: x['size_bytes'], reverse=True)[:15]
    
    # Files from last 7 days
    seven_days_ago = datetime.now().timestamp() - (7 * 24 * 60 * 60)
    recent_files = [f for f in files_data if f['modified_time'] >= seven_days_ago]
    recent_files.sort(key=lambda x: x['modified_time'], reverse=True)
    
    # 15 oldest files
    oldest_files = sorted(files_data, key=lambda x: x['modified_time'])[:15]
    
    # Sort subfolders by size (largest first)
    sorted_subfolders = sorted(subfolders_data, key=lambda x: x['total_size'], reverse=True)
    
    return {
        'total_files': total_files,
        'total_size': total_size,
        'total_size_formatted': format_file_size(total_size),
        'average_size': average_size,
        'average_size_formatted': format_file_size(average_size),
        'oldest_date': format_date(oldest_date),
        'newest_date': format_date(newest_date),
        'largest_files': largest_files,
        'recent_files': recent_files,
        'oldest_files': oldest_files,
        'subfolders': sorted_subfolders
    }


def truncate_filename(filename, max_length=40):
    """Truncate filename if too long, preserving extension"""
    if len(filename) <= max_length:
        return filename
    
    # Try to preserve file extension
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        if len(ext) < max_length - 3:  # Leave room for "..." and extension
            available_length = max_length - len(ext) - 4  # 4 for "..." and "."
            if available_length > 0:
                return f"{name[:available_length]}...{ext}"
    
    # If no extension or extension too long, just truncate
    return f"{filename[:max_length-3]}..."


def generate_markdown_report(analysis):
    """Generate markdown report for Obsidian"""
    
    print("# Downloads Weekly Review")
    print()
    
    # Summary Section
    print("## Summary")
    print()
    print(f"- **Total files:** {analysis['total_files']:,}")
    print(f"- **Date range:** {analysis['oldest_date']} to {analysis['newest_date']}")
    print(f"- **Total size:** {analysis['total_size_formatted']}")
    print(f"- **Average file size:** {analysis['average_size_formatted']}")
    print()
    
    # Action button to open Downloads folder
    downloads_path = get_downloads_folder()
    print(f'```button')
    print(f'name Open Downloads Folder 📁')
    print(f'type link')
    print(f'action file:///{downloads_path}')
    print(f'```')
    print()
    
    # Top 15 Largest Files
    print("## 🔥 Top 15 Largest Files")
    print()
    if analysis['largest_files']:
        print("| File | Size | Date | Delete |")
        print("|------|------|------|--------|")
        for file_info in analysis['largest_files']:
            # Truncate and escape pipes in filename for markdown table
            filename = truncate_filename(file_info['name']).replace('|', '\\|')
            # Create URI link for deletion using Shell Commands with custom variable
            file_path_clean = file_info['path'].replace('\\', '/')
            # URL encode the file path to handle special characters like brackets
            file_path_encoded = quote(file_path_clean, safe='/:')
            # Use the working shell command ID (19bemkchg3) with _file_path parameter
            delete_link = f"[🗑️](obsidian://shell-commands/?execute=19bemkchg3&_file_path={file_path_encoded})"
            print(f"| {filename} | {file_info['size_formatted']} | {file_info['modified_formatted']} | {delete_link} |")
    else:
        print("*No files found*")
    print()
  
   
    # Files from Last Week
    print("## 📅 Files from Last Week")
    print()
    if analysis['recent_files']:
        print(f"*{len(analysis['recent_files'])} files modified in the last 7 days*")
        print()
        print("| File | Size | Date |")
        print("|------|------|------|")
        for file_info in analysis['recent_files']:
            filename = truncate_filename(file_info['name']).replace('|', '\\|')
            print(f"| {filename} | {file_info['size_formatted']} | {file_info['modified_formatted']} |")
    else:
        print("*No files modified in the last 7 days*")
    print()
    
    # Subfolders
    print("## 📁 Subfolders")
    print()
    if analysis['subfolders']:
        print("| Folder | Files | Total Size | Created |")
        print("|--------|-------|------------|---------|")
        for folder_info in analysis['subfolders']:
            folder_name = folder_info['name'].replace('|', '\\|')
            print(f"| {folder_name} | {folder_info['file_count']:,} | {folder_info['total_size_formatted']} | {folder_info['created_formatted']} |")
    else:
        print("*No subfolders found*")
    print()
    
    # 15 Oldest Files
    print("## 🕰️ 15 Oldest Files")
    print()
    if analysis['oldest_files']:
        print("| File | Size | Date |")
        print("|------|------|------|")
        for file_info in analysis['oldest_files']:
            filename = truncate_filename(file_info['name']).replace('|', '\\|')
            print(f"| {filename} | {file_info['size_formatted']} | {file_info['modified_formatted']} |")
    else:
        print("*No files found*")
    print()


def main():
    parser = argparse.ArgumentParser(description='Generate Downloads weekly review for Obsidian')
    parser.add_argument('--folder', '-f', 
                       help='Downloads folder path (default: Windows Downloads folder)')
    
    args = parser.parse_args()
    
    # Determine folder to scan
    if args.folder:
        downloads_folder = Path(args.folder)
    else:
        downloads_folder = get_downloads_folder()
    
    try:
        # Scan folder
        files_data, subfolders_data = scan_downloads_folder(downloads_folder)
        
        # Analyze data
        analysis = analyze_files(files_data, subfolders_data)
        
        # Generate markdown report
        generate_markdown_report(analysis)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()