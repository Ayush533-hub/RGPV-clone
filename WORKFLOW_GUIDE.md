# Student Result Management - Workflow Guide

## System Overview
This system allows students to view their stored results or add new ones using an enrollment number.

## Workflow Steps

### 1. **StudentInfoPage.html** - Search by Enrollment
- User enters their **Enrollment Number**
- User clicks **"View Result"** button
- System checks database for the enrollment number

#### Outcome:
- **If Record Found**: Redirects to result.html in VIEW mode (displays saved result)
- **If Record NOT Found**: Redirects to result.html in EDIT mode (form for entering data)

---

### 2. **result.html** - Two Modes of Operation

#### MODE 1: EDIT (Add New Result)
1. Form shows empty/default values
2. User fills in all student details:
   - Name, Roll Number, Course, Branch
   - Semester, Status
   - Subject marks, credits, grades
   - SGPA, CGPA, Result
3. User clicks **"Save"** button
4. System:
   - Generates HTML result display
   - **Saves to database** (SQLite via Flask)
   - Stores enrollment number as unique key
   - Displays saved result preview

#### MODE 2: VIEW (Display Saved Result)
1. System loads saved HTML from database
2. Displays formatted result sheet
3. User can:
   - Click **"Download as PDF"** to save as PDF file
   - Click **"Edit"** to go back and modify the result
   - Click **"Back to Search"** to return to StudentInfoPage

---

## Key Features

✅ **Database Storage**: Uses SQLite (data.db) with enrollment number as primary key  
✅ **Search Functionality**: Quick lookup by enrollment number  
✅ **Edit Capability**: Modify and re-save student results  
✅ **Export to PDF**: Download results as PDF documents  
✅ **Data Persistence**: Results saved permanently in database  

---

## Technical Details

### Backend (app.py)
- **POST /save** - Save/update student result
- **GET /check** - Check if enrollment exists
- **GET /marksheet/<enrollment>** - Retrieve saved result

### Frontend (JavaScript)
- localStorage used for temporary data passing between pages
- URL parameters (mode, enrollment) control page behavior
- Fetch API for server communication

---

## How to Use

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open StudentInfoPage.html** in browser (or navigate from index.html)

3. **Enter enrollment number** and click "View Result"

4. **If new student**:
   - Fill in all details
   - Click "Save"
   - Result saved to database

5. **If existing student**:
   - View saved result
   - Click "Edit" to modify
   - Click "Download as PDF" to export
   - Click "Back to Search" to check another enrollment

---

## Database Schema

**Table**: marksheets

| Column | Type | Notes |
|--------|------|-------|
| enrollment | TEXT | Primary Key - Unique enrollment number |
| data | TEXT | Stored HTML result display |

---

## Notes
- Ensure Flask server is running on `http://127.0.0.1:5000`
- Database file (data.db) is created automatically on first run
- Each enrollment number is unique - re-saving updates the existing record
