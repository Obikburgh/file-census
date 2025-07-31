# File Census - Downloads Organisation System

A Python-based file management system designed to help organise and clean up accumulated files, particularly the Downloads folder. Integrates seamlessly with Obsidian for weekly review workflows.

## Overview

Over the years, it's easy to accumulate thousands of files across various folders, start organisation processes, forget how they worked, and then start again. This system provides a systematic approach to file analysis and organisation, generating reports that can be integrated into your Obsidian vault for regular review and action.

## Features

- **File system scanning** with detailed metadata collection
- **Obsidian integration** via Templater plugin
- **Multiple output formats** (CSV and Markdown)
- **Subfolder analysis** with size and file count summaries
- **Weekly review workflows** with actionable insights
- **Cross-drive compatibility** (works with any drive/folder structure)

## Obsidian Setup with Templater

### Prerequisites
- Obsidian with Templater plugin installed
- Python installed and accessible from command line
- File Census scripts in accessible location

### Templater Configuration

1. **Enable User System Command Functions**
   - Go to Obsidian Settings → Community Plugins → Templater
   - Find "User System Command Functions" section
   - Enable "User System Command Functions" (accept the security warning)

2. **Add User Functions**
   - Click "Add New User Function"
   - **Function Name**: `weekly_downloads` (or preferred name)
   - **System Command**: `python J:/_learning/claude/file-census/downloads_weekly_review.py`
   - Save settings and restart Obsidian

3. **Create Weekly Template**
   ```markdown
   # Weekly Downloads Review - <% tp.date.now("YYYY-MM-DD") %>
   
   <% tp.user.weekly_downloads() %>
   
   ## Actions Taken
   - [ ] Review large files
   - [ ] Clean up old files
   - [ ] Organise recent downloads
   ```

4. **Usage**
   - Create a new note from your template
   - Run Templater: Replace templates in active file (Ctrl+P)
   - Review the generated analysis and take action

## File Descriptions

### file_census.py
**Purpose**: Basic file system scanner that creates comprehensive CSV output.

**Features**:
- Scans specified directory recursively
- Outputs: filename, path, size, modification date, file extension
- CSV format suitable for spreadsheet analysis
- Handles large directories efficiently

**Usage**: 
```bash
python file_census.py
```

### summary_report.py
**Purpose**: Converts CSV data into readable Markdown reports.

**Features**:
- Reads CSV output from file_census.py
- Creates formatted Markdown summaries
- Basic statistics and file type analysis
- Obsidian-ready output format

**Usage**:
```bash
python summary_report.py
```

### downloads_weekly_review.py
**Purpose**: Comprehensive Downloads folder analysis designed for weekly reviews.

**Features**:
- **Summary Statistics**: Total files, date range, total size, average file size
- **Top 15 Largest Files**: Identifies space hogs with sizes and dates
- **Recent Files**: All files from the last 7 days for quick review
- **15 Oldest Files**: Finds forgotten files that might need cleanup
- **Subfolder Analysis**: 
  - Lists all subfolders in Downloads
  - File count and total size per subfolder
  - Most recent file date in each subfolder
- **Direct Markdown Output**: Ready for Obsidian/Templater integration

**Usage**:
```bash
python downloads_weekly_review.py
```

**Sample Output Structure**:
```markdown
# Downloads Weekly Review

## Summary
- Total files: 801
- Date range: 2020-03-15 to 2025-07-31
- Total size: 2.3 GB
- Average file size: 2.9 MB

## Top 15 Largest Files
[Detailed file list with sizes]

## Files from Last Week
[Recent downloads for review]

## 15 Oldest Files
[Ancient files that might need cleanup]

## Subfolder Analysis
[Breakdown of subdirectories]
```

### hello.py
**Purpose**: Simple test script for validating Python and Templater integration.

**Features**:
- Prints greeting and current timestamp
- Minimal dependencies
- Perfect for testing Templater User Function setup

**Usage**:
```bash
python hello.py
```

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Obikburgh/file-census.git
   cd file-census
   ```

2. **Ensure Python is installed**:
   ```bash
   python --version
   ```

3. **Test basic functionality**:
   ```bash
   python hello.py
   python downloads_weekly_review.py
   ```

4. **Set up Obsidian integration** (see Obsidian Setup section above)

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)
- Windows, macOS, or Linux
- Obsidian (optional, for integration features)
- Templater plugin (optional, for weekly automation)

## Future Enhancements

- [ ] File duplicate detection
- [ ] Automatic file organisation rules
- [ ] Integration with additional note-taking systems
- [ ] GUI interface for non-technical users
- [ ] Configurable scan parameters
- [ ] Action buttons for direct file operations

## Contributing

This is a personal productivity project, but suggestions and improvements are welcome. Please open issues or submit pull requests.

## License

Open source - feel free to adapt for your own file organisation needs.