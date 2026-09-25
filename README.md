# CodeCraftHub Learning Management System

CodeCraftHub is a simple personalized learning platform for developers. It provides a REST API for managing courses and tracking their learning progress.

The project is built using Python and Flask, with course data stored in a JSON file instead of a database.

## Features

- Add new courses
- View all courses
- View a specific course
- Update course information
- Delete courses
- Track course status
- Validate target completion dates
- Store data in a JSON file
- Automatic creation of `courses.json`
- Course statistics by status
- Error handling for invalid requests

## Technologies Used

- Python
- Flask
- Flask-CORS
- JSON
- REST API

## Project Structure

```text
CodeCraftHub/
├── .venv/              # Python virtual environment
├── app.py              # Main Flask application
├── courses.json        # Course data storage
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation