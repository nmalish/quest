# Quest Project

## Setup and Running the Application

### Activate Virtual Environment
```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
.\venv\Scripts\activate
```

### Run Django Application
```bash
# Make sure you're in the project root directory
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Viewing Questions

There are three ways to view the questions in the database:

### 1. Questions List Page
Visit http://127.0.0.1:8000/questions/ to see a beautiful, interactive list of all questions with:
- Question descriptions
- Question images (if available)
- All possible answers
- Visual indication of correct answers
- Responsive design that works on all devices

### 2. Admin Interface
Visit http://127.0.0.1:8000/admin/ to access the Django admin interface where you can:
- View all questions and their answers
- Add new questions
- Edit existing questions
- Delete questions

### 3. API Endpoint
Visit http://127.0.0.1:8000/api/questions/ to see all questions in JSON format, including:
- Question descriptions
- Question types
- Associated answers
- Correct answer indicators
