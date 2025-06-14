# EduPlatform CLI

A command-line educational platform built with Python, designed for managing students, teachers, assignments, and grades in an academic environment.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [User Guide](#user-guide)
  - [Getting Started](#1-getting-started)
  - [Registration](#2-registration)
  - [Login](#3-login)
  - [Available Roles and Commands](#4-available-roles-and-commands)
  - [Common Commands](#5-common-commands)
  - [Exporting Data](#6-exporting-data)
  - [Troubleshooting](#troubleshooting)
  - [Example Session](#example-session)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [License](#license)

## Features

- **User Management**: Support for multiple user roles (Admin, Teacher, Student, Parent)
- **Assignment Management**: Create, submit, and grade assignments
- **Grade Tracking**: Record and track student grades with statistics
- **Notifications**: Stay updated with in-app notifications
- **Data Export**: Export data to multiple formats (XLSX, CSV, SQLite)
- **CLI Interface**: Simple and intuitive command-line interface
- **Role-Based Access Control**: Different commands and permissions based on user role
- **In-Memory Storage**: Fast performance with in-memory data storage
- **Comprehensive Help**: Built-in help system with command documentation

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/eduplatform.git
   cd eduplatform
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/eduplatform.git
   cd eduplatform
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

## User Guide

### 1. Getting Started

Start the application:
```bash
python run.py
```

### 2. Registration

Register a new user with the following command:
```bash
register <role> "<full_name>" <email> <password> [phone] "[address]"
```

**Examples:**
```bash
# Register an admin
register admin "John Doe" john@example.com admin123

# Register a teacher with phone number
register teacher "Jane Smith" jane@example.com teacher123 1234567890

# Register a student with full details
register student "Alex Johnson" alex@example.com student123 9876543210 "123 School St, City"

# Register a parent
register parent "Sarah Williams" sarah@example.com parent123
```

**Notes:**
- Enclose names and addresses with spaces in quotes
- Phone number should be digits only
- Password is case-sensitive

### 3. Login

```bash
login <email> <password>
```

### 4. Available Roles and Commands

#### Admin Commands
```bash
# User Management
list_users
delete_user <email>
promote_user <email> <new_role>

# System Management
system_status
export_data <format>  # csv, json, xlsx
```

#### Teacher Commands
```bash
# Assignment Management
create_assignment "<title>" "<description>" <due_date> <max_score>
list_assignments
grade_assignment <assignment_id> <student_email> <score>

# Class Management
list_students
schedule_class "<subject>" "<date>" "<time>" "<duration>"
```

#### Student Commands
```bash
view_assignments
submit_assignment <assignment_id> "<submission_text>"
view_grades
view_schedule
```

#### Parent Commands
```bash
view_child_progress <child_email>
view_child_grades <child_email>
view_child_attendance <child_email>
```

### 5. Common Commands
```bash
# View profile
profile

# Update profile
update_profile --name "New Name" --email new@example.com --phone 1234567890

# Change password
change_password <current_password> <new_password>

# View notifications
notifications

# Mark notification as read
read_notification <notification_id>

# Clear screen
clear

# Exit the application
exit
```

### 6. Exporting Data

```bash
# Export data (admin only)
export_data csv
export_data json
export_data xlsx
```

### 7. Help

```bash
# List all available commands
help

# Get help for a specific command
help <command_name>
```

## Troubleshooting

- If you get a "command not found" error, check for typos
- For login issues, verify your email and password
- If the application crashes, restart it and try again
- Check that you have the necessary permissions for the command you're trying to use

## Example Session

```bash
# Start the application
python run.py

# Register as admin
register admin "Admin User" admin@school.edu admin123

# Login
login admin@school.edu admin123

# List all users (admin only)
list_users

# Create a new assignment (teacher)
create_assignment "Math Homework" "Complete exercises 1-10" 2023-12-31 100

# View assignments (student)
view_assignments

# Submit an assignment (student)
submit_assignment 1 "Here's my homework submission"

# Grade an assignment (teacher)
grade_assignment 1 student@school.edu 95

# View grades (student)
view_grades

# Exit the application
exit
```

## Usage Guide

### Authentication

```
# Register a new user
register <role> <full_name> <email> <password> [phone] [address]

# Login to an existing account
login <email> <password>

# Logout of the current account
logout

# Show information about the current user
whoami
```

### Assignment Management

#### For Teachers:
```
# Create a new assignment
create_assignment <title> <subject> <class_id> <due_date> [max_points=100] [difficulty=medium]

# Grade a student's assignment
grade_assignment <submission_id> <grade> [comments]
```

#### For Students:
```
# List your assignments
list_assignments [status] [subject]

# Submit an assignment
submit_assignment <assignment_id>
```

### Grade Management

```
# View your grades
view_grades [subject] [type]

# Export your grades (XLSX, CSV, or SQLite)
export_my_data [format=xlsx] [output_dir=exports]
```

### Notifications

```
# View your notifications
notifications [read|unread|all]

# Mark a notification as read
notifications mark_read <id>

# Mark all notifications as read
notifications clear
```

### Data Export (Advanced)

```
# Export your personal data
export_my_data [format=xlsx] [output_dir=exports]

# Export class data (Teachers/Admins only)
export_class <class_id> [format=xlsx] [output_dir=exports]

# Export all school data (Admins only)
export_school [format=xlsx] [output_dir=exports]
```

### System Commands

```
# Clear the terminal screen
clear

# Exit the application
exit
quit
```

## Exporting Data

The application supports exporting data in multiple formats:

1. **XLSX** (Excel) - Best for viewing in spreadsheet applications
2. **CSV** - Comma-separated values, compatible with most applications
3. **SQLite** - Relational database format for advanced analysis

### Example Exports

```bash
# Export your data to Excel
export_my_data format=xlsx

# Export class data to CSV
export_class class1 format=csv

# Export all school data to SQLite (Admin only)
export_school format=sqlite
```

## Project Structure

```
.
├── eduplatform/           # Main package directory
│   ├── __init__.py       # Package initialization
│   ├── models/           # Data models (User, Assignment, etc.)
│   ├── repositories/     # Data access layer
│   ├── services/         # Business logic
│   │   ├── auth_service.py
│   │   ├── assignment_service.py
│   │   ├── grade_service.py
│   │   └── export_service.py
│   ├── cli/              # Command-line interface
│   │   └── commands/     # Command implementations
│   └── utils/            # Utility functions
│       └── export_utils.py
├── tests/                # Test files
├── requirements.txt      # Project dependencies
├── requirements-dev.txt  # Development dependencies
├── setup.py             # Package configuration
├── run.py               # Application entry point
└── README.md            # This file
```

## Development

### Setting Up for Development

1. Fork the repository and clone your fork
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

### Running Tests

Run the test suite with:
```bash
pytest
```

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

```bash
# Format code with Black
black .

# Sort imports
isort .

# Run linter
flake8
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


## Contributing

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License 

## Acknowledgments

- Built with Python 3.8+
- Uses JWT for authentication
- Follows clean architecture principles
