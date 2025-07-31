#!/usr/bin/env python3
"""
File Census - Efficiently scan Downloads folder and create CSV report
"""

import os
import csv
import sys
from pathlib import Path
from datetime import datetime
import argparse


def get_downloads_folder():
    """Get the Downloads folder path for the current user"""
    if os.name == 'nt':  # Windows
        downloads_path = Path.home() / 'Downloads'
    else:  # macOS/Linux
        downloads_path = Path.home() / 'Downloads'
    
    return downloads_path


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


def scan_folder(folder_path, show_progress=True):
    """
    Efficiently scan folder and yield file information
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not folder_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")
    
    file_count = 0
    processed_count = 0
    
    # First pass: count total files for progress tracking
    if show_progress:
        print("Counting files...", end="", flush=True)
        try:
            for _ in folder_path.rglob('*'):
                if _.is_file():
                    file_count += 1
            print(f" Found {file_count} files")
        except PermissionError:
            print(" (Unable to count all files due to permissions)")
            file_count = 0
    
    # Second pass: process files
    try:
        for file_path in folder_path.rglob('*'):
            if file_path.is_file():
                try:
                    stat_info = file_path.stat()
                    
                    file_info = {
                        'filename': file_path.name,
                        'full_path': str(file_path),
                        'size_bytes': stat_info.st_size,
                        'size_formatted': format_file_size(stat_info.st_size),
                        'modified_date': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'extension': file_path.suffix.lower()
                    }
                    
                    processed_count += 1
                    
                    if show_progress and file_count > 0 and processed_count % 100 == 0:
                        progress = (processed_count / file_count) * 100
                        print(f"\rProcessing files... {processed_count}/{file_count} ({progress:.1f}%)", end="", flush=True)
                    
                    yield file_info
                    
                except (OSError, PermissionError) as e:
                    if show_progress:
                        print(f"\nSkipping {file_path}: {e}")
                    continue
                    
    except KeyboardInterrupt:
        print(f"\nInterrupted. Processed {processed_count} files.")
        return
    
    if show_progress:
        print(f"\nCompleted scanning {processed_count} files.")


def create_csv_report(folder_path, output_file=None, show_progress=True):
    """
    Create CSV report of files in the specified folder
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"file_census_{timestamp}.csv"
    
    output_path = Path(output_file)
    
    fieldnames = ['filename', 'full_path', 'size_bytes', 'size_formatted', 'modified_date', 'extension']
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            files_written = 0
            for file_info in scan_folder(folder_path, show_progress):
                writer.writerow(file_info)
                files_written += 1
            
            if show_progress:
                print(f"CSV report created: {output_path.absolute()}")
                print(f"Total files processed: {files_written}")
                
    except PermissionError:
        print(f"Error: Permission denied writing to {output_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error creating CSV report: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Scan Downloads folder and create CSV report')
    parser.add_argument('--folder', '-f', 
                       help='Folder to scan (default: Downloads folder)')
    parser.add_argument('--output', '-o', 
                       help='Output CSV file (default: auto-generated name)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress progress output')
    
    args = parser.parse_args()
    
    # Determine folder to scan
    if args.folder:
        scan_folder_path = Path(args.folder)
    else:
        scan_folder_path = get_downloads_folder()
    
    show_progress = not args.quiet
    
    if show_progress:
        print(f"Scanning folder: {scan_folder_path}")
    
    try:
        create_csv_report(scan_folder_path, args.output, show_progress)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except NotADirectoryError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()