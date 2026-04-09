# Task Manager
***

## About the Project

**Task Manager** is a web application for managing tasks with a system of statuses, labels, and filtering. The project allows you to create, track, and manage tasks, assign executors, and categorize tasks using statuses and labels.

### Hexlet tests and linter status:
[![Actions Status](https://github.com/Scopp1337/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Scopp1337/python-project-52/actions)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Scopp1337_python-project-52&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Scopp1337_python-project-52)


### Key Features

- ✅ User registration, authentication, and profile management
- ✅ Full CRUD operations for tasks
- ✅ Task status management (Create, Update, Delete)
- ✅ Label management for task categorization
- ✅ Task filtering by status, executor, labels, and "Only my tasks"
- ✅ Access control — only the author can edit/delete their tasks
- ✅ Modern responsive interface with Bootstrap 5

## Technologies

### Backend
- **Python 3.12** — core programming language
- **Django 5.2** — web framework
- **django-filter** — advanced filtering
- **PostgreSQL** — database for production
- **SQLite** — database for development
- **gunicorn** — WSGI server for production

### Frontend
- **Bootstrap 5** — CSS framework for responsive design
- **Bootstrap Icons** — icon library
- **HTML5** — page markup

### Development Tools
- **uv** — fast package manager
- **Ruff** — linter and code formatter
- **GitHub Actions** — CI/CD
- **SonarCloud** — code quality analysis
- **Make** — command automation

### Deployment
- **Render.com** — application and database hosting


## Installation

### Clone the repository:

```
git clone https://github.com/Scopp1337/python-project-52.git

cd python-project-52
```

## Testing
### Run all tests
```
make test
```

### Run tests for specific app
```
python manage.py test users
python manage.py test statuses
python manage.py test labels
python manage.py test tasks
```

### Run linter
```
make lint
```

### Auto-fix linting issues
```
make lint-fix
```

## Deployment
### Collect static files
```
make collectstatic
```

### Run with Gunicorn
```
make render-start
```