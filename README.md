# FretMastery - Guitar Learning PWA

FretMastery is a Progressive Web App designed to help guitarists master fretboard note recognition through exercises. Built with Python Flask and SQLite, the app allows admin users to create custom practice exercises with auto-generated SVG fretboard diagrams, while learners can log practice sessions and rate exercise difficulty. The platform features a public exercise library for browsing, user authentication with secure password hashing, and full CRUD operations for managing both exercises and practice sessions. Leveraging mathematical pitch logic to calculate note positions across the fretboard, FretMastery provides accurate, scalable guitar learning tools accessible to musicians of all levels.

As a fully-featured PWA, FretMastery works offline by caching exercises and diagrams, making it perfect for practicing anywhere—whether on stage, in rehearsal, or commuting. The app includes role-based authorization (admin vs. standard users), XSS protection on all pages, and search/filter functionality to help learners find exercises by note range, difficulty, or musical concept. Built as a Year 12 HSC Software Engineering project, FretMastery demonstrates modern web development practices including responsive design, secure authentication, normalized database design (3NF), and accessibility compliance with WCAG guidelines.

---

## Features
- **Interactive Fretboard Exercises**: Auto-generated SVG diagrams using mathematical pitch logic
- **User Authentication**: Secure registration and login with bcrypt password hashing
- **Role-Based Authorization**: Admin users manage exercises, standard users track practice sessions
- **Community Ratings**: See average difficulty ratings from other learners
- **Search & Filter**: Find exercises by note range, difficulty, or musical concept
- **Offline PWA**: Works without internet—cached exercises available anytime
- **Accessible Design**: WCAG-compliant interface for inclusive learning
- **Practice Tracking**: Log sessions with ratings and notes to monitor progress

---

## Technology Stack
- **Backend**: Python Flask
- **Database**: SQLite (3NF normalized schema)
- **Frontend**: HTML5, CSS3, JavaScript
- **PWA**: Service Worker, Web Manifest
- **Security**: Bcrypt password hashing, XSS prevention, secure session management
- **Graphics**: SVG generation with fretboard library and custom pitch logic

---

## System Architecture

### User Authentication Flow
![User Authentication Flowchart](docs/diagrams/User%20Authentication.drawio%20(1)%20(1).svg)

### Authorization System
![Authorization Flowchart](docs/diagrams/Authorisation.drawio%20(2)%20(1).svg)

### Application Storyboard
![Storyboard](docs/diagrams/Storyboard.drawio%20(1).svg)

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FretMaster-PWA-SWE-Assessment.git
   cd FretMaster-PWA-SWE-Assessment
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python3 app.py
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5001
   ```

---

## Database Schema
The application uses a normalized SQLite database with three main tables:
- **Users**: User credentials, roles (admin/standard), authentication data
- **Exercises**: Admin-created practice content with note ranges, descriptions, SVG paths
- **PracticeSessions**: User-logged practice attempts with difficulty ratings and notes

Relationships use foreign keys to maintain referential integrity, with JOIN operations for displaying user progress and calculating community average ratings.

---

## Project Context
Developed as a Year 12 HSC Software Engineering major project (NSW, Australia) demonstrating outcomes:
- **SE-12-02**: Applies structural elements to develop programming code
- **SE-12-05**: Explains social, ethical and legal implications of software engineering
- **SE-12-06**: Justifies selection and use of tools and resources

---

## License
This project was created for educational purposes as part of the NSW HSC Software Engineering course.

---

## Acknowledgments
- PhotoJournal tutorial series for foundational Flask PWA patterns
- fretboard library for SVG diagram generation
- NESA HSC Software Engineering syllabus and assessment guidelines
