# CampusFix — Smart College Complaint & Problem Tracking System

CampusFix is a web-based college complaint management system designed to make campus problem reporting, tracking, assignment, and resolution more organized and transparent.

The platform allows students to report problems such as Wi-Fi issues, electricity problems, classroom issues, water problems, cleanliness, furniture damage, and other campus-related complaints.

Administrators can review complaints, assign departments, update priority and status, add progress comments, and keep students informed through notifications.

---

## 🚀 Project Overview

In many colleges, students report campus problems through informal channels such as messages, calls, or verbal communication. This can make it difficult to track complaints, know their current status, or identify which department is responsible.

CampusFix provides a centralized platform where:

**Student Reports → Admin Reviews → Department Handles → Status Updates → Student Tracks → Problem Gets Resolved**

The main goal is to create a simple and transparent complaint-management workflow for a college campus.

---

## ✨ Features

### 👨‍🎓 Student Features

- Student registration and login
- Secure password hashing
- Student dashboard
- Report a campus problem
- Select complaint category
- Select priority
- Add location and room number
- Upload an image as evidence
- View submitted complaints
- View complaint details
- Track complaint status
- View complaint update timeline
- Manage profile information
- Receive notifications
- Mark notifications as read
- Logout functionality

### 🛠️ Admin Features

- Admin authentication
- Admin dashboard
- View complaint statistics
- View all complaints
- Filter and manage complaints
- View complete complaint details
- Assign complaints to departments
- Change complaint priority
- Update complaint status
- Add comments/progress updates
- Generate notifications for students
- Monitor complaint progress

---

## 🔄 Complaint Workflow

The main workflow of CampusFix is:

```text
        STUDENT
           │
           ▼
   Report a Problem
           │
           ▼
    Complaint Created
           │
           ▼
      ADMIN REVIEW
           │
           ▼
   Assign Department
           │
           ▼
  Set Priority / Status
           │
           ▼
     Work on Problem
           │
           ▼
    Update Progress
           │
           ▼
   Student Gets Update
           │
           ▼
      Issue Resolved
```

## Simple MVP Flow
```
    REPORT
      ↓
    TRACK
      ↓
    PRIORITIZE
      ↓
    ASSIGN
      ↓
    RESOLVE
```

## 🗄️ Database Design

CampusFix currently uses MySQL with Flask-SQLAlchemy.

The application contains 5 main database tables:

1. users

Stores student and admin account information.

Main fields include:
```
--id
--full_name
--email
--password_hash
--student_id
--branch
--year
--role
--created_at
```
2. departments

Stores departments responsible for handling complaints.

Main fields include:
```
--id
--name
--description
--created_at
```
3. complaints

Stores all submitted complaints.

Main fields include:
```
--id
--complaint_id
--user_id
--department_id
--title
--description
--category
--location
--room_number
--priority
--status
--image_path
--contact_pref
--created_at
--updated_at
```
4. complaint_updates

Stores the history and progress updates of complaints.

Main fields include:
```
--id
--complaint_id
--user_id
--status
--comment
--created_at
```
5. notifications

Stores notifications sent to users.

Main fields include:
```
--id
--user_id
--complaint_id
--message
--is_read
--created_at
```

## 🔗 Database Relationships

The main relationships are:

User
 │
 ├─── 1:N ─── Complaints
 │
 ├─── 1:N ─── Complaint Updates
 │
 └─── 1:N ─── Notifications

Department
 │
 └─── 1:N ─── Complaints

Complaint
 │
 ├─── 1:N ─── Complaint Updates
 │
 └─── 1:N ─── Notifications

## 🛠️ Technology Stack
--Frontend
    HTML5
    CSS3
    JavaScript
--Backend
    Python
    Flask
    Flask-SQLAlchemy
    Database
    MySQL
    PyMySQL
--Other Technologies
    Werkzeug
    python-dotenv

## 📁 Project Structure
CampusFix/
│
├── app.py
├── README.md
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── student-dashboard.html
│   ├── report-problem.html
│   ├── my-complaints.html
│   ├── complaint-details.html
│   ├── profile.html
│   ├── notifications.html
│   ├── admin-dashboard.html
│   ├── admin-complaints.html
│   ├── admin-complaint-details.html
│   ├── _flash.html
│   │
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── uploads/
│       └── .gitkeep
│
└── ...

##🔐 Security

--CampusFix includes several basic security practices:

    Passwords are stored using password hashing rather than plain text.
    Authentication is handled using Flask sessions.
    Student and admin routes are protected based on user roles.
    Uploaded files are restricted to supported image formats.
    Maximum upload size is limited.
    Environment variables are used for database credentials and secret configuration.
    Unauthorized users are prevented from accessing protected functionality.

##🖼️ Complaint Categories

--CampusFix currently supports the following complaint categories:

    Internet/Wi-Fi
    Electricity
    Water
    Classroom
    Laboratory
    Furniture
    Cleanliness
    Other

##📌 Priority Levels

--Complaints can have one of four priority levels:

    Low
    Medium
    High
    Critical

##📊 Complaint Status

--The system currently supports:

    Pending
    In Progress
    Resolved
    Rejected

##🤖 AI-Assisted Development

This project is part of my learning journey.

I am still learning JavaScript and CSS, so I used AI tools as a coding assistant during development.

AI assistance was used for:

Understanding unfamiliar JavaScript and CSS concepts
Getting explanations for errors
Debugging frontend issues
Exploring possible implementation approaches
Iterating on parts of the frontend
Improving UI styling
Understanding how different parts of the application connect

The project was then integrated with my Flask backend, MySQL database, authentication system, routes, and application workflow.

I am mentioning this because I want to be transparent about my learning process rather than presenting myself as someone who already has advanced knowledge of every technology used in the project.

For me, AI was not a replacement for learning. It was a tool that helped me understand unfamiliar concepts, solve problems, experiment with ideas, and continue building the project.

##📚 What I Learned

Working on CampusFix helped me understand several concepts beyond basic Python programming.

--Python & Flask
```
    Flask routing
    Request handling
    Sessions
    Authentication
    Form processing
    File uploads
    Error handling
    Role-based access
```
--Database
```
    MySQL
    SQLAlchemy ORM
    Database models
    Primary keys
    Foreign keys
    One-to-many relationships
    CRUD operations
```
--Web Development
```
    HTML templates
    CSS
    JavaScript
    Flask url_for
    Form submission
    Frontend-backend integration
```
--Project Development
```
    Structuring a full-stack application
    Debugging integration problems
    Designing database relationships
    Building an end-to-end workflow
    Working with AI as a learning/coding assistant
    Understanding the difference between frontend and backend responsibilities
```

## 🎯 Project Goal

--The goal of CampusFix is to make campus problem reporting:

    Simple • Organized • Trackable • Transparent

Instead of students repeatedly asking:

    "What happened to my complaint?"

    CampusFix provides a centralized system where the complaint and its progress can be tracked.

##📄 Project Status

-- Status: Functional End-to-End Prototype

--The current version includes:

    Flask backend
    MySQL database
    Student authentication
    Admin authentication
    Complaint management
    Department assignment
    Priority management
    Status management
    Complaint updates
    Notifications
    Image uploads
    Student dashboard
    Admin dashboard

##⭐ If You Find This Project Interesting

--If you are interested in the project, feel free to explore the code, suggest improvements, or share feedback.

--This project represents my learning journey from Python fundamentals toward building a complete web application.

## 📜 License

--This project is created for educational and hackathon purposes.

## Author
- Bhupendra Singh
- B.Tech CSE (AI) Student
