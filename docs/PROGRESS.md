# FretMaster PWA - Development Progress

**Assessment Due:** Wednesday 17 December 2025, 9:00am
**Target:** 65/65 marks

---

## Phase 0: Project Setup ✅ COMPLETE
- [x] Organized clean project structure
- [x] Created documentation folder (`docs/`)
- [x] Set up proper `.gitignore`
- [x] Created `requirements.txt`
- [x] Created `README.md`
- [x] Configured `config.py` with proper paths

## Phase 1: Database ✅ COMPLETE
- [x] Created 3NF database schema (Users, Exercises, PracticeSessions)
- [x] Implemented foreign key relationships
- [x] Added sample data (3 users, 4 exercises, 6 sessions)
- [x] Verified JOIN queries with AVG calculations
- [x] Built database initialization script (`init_db.py`)
- [x] Created debugging utility (`view_db.py`)

**Files:** `database/schema.sql`, `database/init_db.py`, `database/view_db.py`

---

## Phase 2: Flask Application & Authentication ⏳ IN PROGRESS
- [ ] Create Flask app structure (`app.py`)
- [ ] Build base template with navigation (`templates/base.html`)
- [ ] Implement user registration
- [ ] Implement login/logout with session management
- [ ] Add password hashing (bcrypt/scrypt)
- [ ] XSS prevention (Jinja2 escaping)

**Next Step:** Create `app.py` and base template structure

---

## Phase 3: Core Features ⏹️ NOT STARTED
- [ ] Admin CRUD for exercises
- [ ] User CRUD for practice sessions
- [ ] Public browse mode (non-logged users)
- [ ] Search/filter functionality
- [ ] SVG diagram generation integration

---

## Phase 4: PWA Features ⏹️ NOT STARTED
- [ ] Create `manifest.json`
- [ ] Implement service worker
- [ ] Test offline functionality
- [ ] Test installation on mobile

---

## Documentation Requirements ⏹️ NOT STARTED

### Planning Diagrams (10 marks)
- [ ] IPO Chart
- [ ] Data Dictionary
- [ ] Storyboard (wireframes)
- [ ] Authentication flowchart
- [ ] Authorization flowchart

### Written Documentation (25 marks)
- [ ] Project requirements (functional, non-functional, constraints)
- [ ] Social/ethical/legal evaluation (WCAG, Australian law)
- [ ] Technical reflection (200-300 words)
- [ ] GitHub commit history screenshot

---

## Marking Criteria Progress

| Component | Marks | Status |
|-----------|-------|--------|
| Project Requirements | 10 | ⏹️ Not Started |
| Planning Diagrams | 10 | ⏹️ Not Started |
| PWA Implementation | 5 | ⏹️ Not Started |
| Code Quality | 5 | ⏳ In Progress |
| SQL Database | 5 | ✅ Complete |
| Security | 5 | ⏹️ Not Started |
| GitHub Version Control | 10 | ⏳ In Progress |
| Social/Ethical/Legal | 10 | ⏹️ Not Started |
| Technical Reflection | 5 | ⏹️ Not Started |
| **TOTAL** | **65** | **5/65 Estimated** |

---

**Last Updated:** 2025-12-03
