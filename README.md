This project was done to create room booking API in collaboration with a selected AI tool (Google Gemini 3 Pro). I have done the project in English even though the assignment was given in Finnish. I thought it's best for my code writing and AI prompts to handle everything in English.

---

# Room Booking System

## 1. Project Overview

This project is a web-based application designed to manage room reservations efficiently. It allows users to view availability via an interactive calendar, book specific time slots, and manage their reservations. The system features role-based authentication, distinguishing between standard users and administrators.

## 2. Key Features

### A. User Management

* **Authentication:** Secure login and registration functionality.
* **Role-Based Access Control (RBAC):**
* **Admins:** Can view and delete any booking in the system.
* **Standard Users:** Can only create bookings and delete their *own* bookings.


* **Booking Quotas:** Standard users are limited to 5 active future bookings to prevent monopolization.

### B. Booking Logic

* **Interactive Calendar:** Utilizes **FullCalendar.js** to visualize time slots and room availability.
* **Conflict Detection:** The system prevents double-booking by checking for overlapping time slots before confirming a reservation.
* **Validation Rules:**
* Bookings must be in the future.
* Start time must be before end time.
* Minimum duration: 30 minutes; Maximum duration: 8 hours.



### C. Reporting

* **Room Lists:** Dedicated views for specific rooms to see a list of all associated bookings.
* **Dashboard:** A central hub showing the calendar and quick booking forms.

## 3. Technology Stack

* **Backend:** Python (Flask Framework).
* **Frontend:** HTML5, CSS3, JavaScript.
* **Libraries:**
* `FullCalendar` (v6.1.10) for the calendar interface.


* **Database:** In-Memory Python Lists (Data resets when the application stops).

## 4. Project File Structure & Setup

**Important:** You must create specific folders and place the downloaded files into them exactly as shown below. The application relies on this structure to find the HTML and CSS files.

### A. Directory Tree

Create a main project folder and set up the following hierarchy:

```text
/YourProjectFolder
├── app.py              <-- Place the main Python file here
├── templates/          <-- Create this folder manually
│   ├── index.html      <-- Place inside 'templates'
│   └── room_list.html  <-- Place inside 'templates'
└── static/             <-- Create this folder manually
    └── style.css       <-- Place inside 'static'

```

### B. File Placement Guide

1. **`app.py`**: Place this in the root (main) directory. This is the application entry point.
2. **`templates/` Folder**: You must create a folder named `templates`. Flask looks here for HTML files.
* Move `index.html` into this folder.
* Move `room_list.html` into this folder.


3. **`static/` Folder**: You must create a folder named `static`. Flask looks here for CSS and images.
* Move `style.css` into this folder.



## 5. Installation & Execution

1. **Prerequisites:** Ensure Python 3.x is installed.
2. **Install Dependencies:**
Open your terminal or command prompt and install the Flask framework:
```bash
pip install flask

```


3. **Run the Application:**
Navigate to your project folder in the terminal and run:
```bash
python app.py

```


4. **Access the App:**
Open your web browser and navigate to: `http://127.0.0.1:5000`.

## 6. Usage & Credentials

Since the database is in-memory, the system initializes with the following seed data every time it restarts.

### Demo Accounts

Use these credentials to test different user roles:

| Role | Email | Password |
| --- | --- | --- |
| **Admin** | `admin@company.com` | `admin123` |
| **User** | `john@test.com` | `password123` |
| **User** | `jane@test.com` | `password123` |
| **User** | `bob@test.com` | `password123` |

### How to Book a Room

1. Log in with a user account.
2. Select a **Room**, **Date**, **Start Time**, and **End Time** from the sidebar form.
3. Alternatively, click and drag on the calendar view to select a time slot.
4. Click **Book Now**.

## 7. API Endpoints

The application exposes the following RESTful endpoints for the frontend to consume:

* **`GET /api/bookings`**: Retrieve bookings (supports `start` and `end` query parameters for filtering).
* **`POST /api/bookings`**: Create a new booking. Requires JSON payload with `roomId`, `start`, and `end`.
* **`DELETE /api/bookings/<booking_id>`**: Cancel a specific booking (subject to permission checks).

---

**Next Step:** Would you like me to create a zip file structure summary or a quick Python script that automatically creates these folders and moves the files for you (assuming they are currently all in one place)?