# 🚀 How to Run the Application (Step‑by‑Step, Windows)

This guide is written for **non‑technical users first**, with a more technical section at the end.

---

## 1. Easiest way (recommended for teachers / HODs on this PC)

Use this if you are sitting at the **Windows computer where the project is already installed**.

### 1.1 Start the dashboard

1. Open **File Explorer**.
2. Go to the folder:
   - `C:\Users\pawan\Desktop\qwen\attendance_dashboard`
3. Inside this folder, find the file named:
   - `start.bat`
4. **Double‑click** `start.bat`.
5. A **black window** (terminal) will open and you will see messages like:
   - `Starting Attendance Analytics Dashboard...`
   - `Activating virtual environment...`
   - `Starting FastAPI server...`
   - Later: `Uvicorn running on http://0.0.0.0:8000`

> Important: **Do not close this black window** while you are using the website.  
> If you close it, the site will stop working.

### 1.2 Open the website in your browser

Once the black window shows that the server is running:

1. Open **Google Chrome**, **Microsoft Edge**, or another modern browser.
2. In the address bar at the top, type:
   - `http://localhost:8000` and press Enter.
3. You should now see the **Attendance Dashboard home page**.

From there, you can visit:

- **Landing Page**: `http://localhost:8000`
- **Student Dashboard**: `http://localhost:8000/student`
- **Class Analytics**: `http://localhost:8000/analytics`
- **API Documentation (for developers)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### 1.3 Stopping the dashboard

When you are finished using the dashboard:

1. Go back to the **black terminal window** that opened when you ran `start.bat`.
2. Click anywhere inside the window so it is active.
3. Press the keys:
   - `Ctrl` and `C` together (`Ctrl + C`).
4. The server will stop and the window may close.

You can always **start it again later** by double‑clicking `start.bat` again.

---

## 2. What is happening behind the scenes (in simple words)

- The file `start.bat`:
  - Activates a private **Python environment** (so it uses the right Python packages).
  - Starts a small **web server** on your computer.
  - This server listens on **port 8000**.
- When you open `http://localhost:8000` in your browser:
  - Your browser connects to that local web server.
  - The server sends back the HTML pages and data that make up the dashboard.

You do **not** need internet access for this local setup, as long as everything is already installed.

---

## 3. Where the data is stored

For this local Windows setup:

- The application uses a simple file‑based database called **SQLite**.
- The main data file is:
  - `attendance_dashboard\backend\attendance.db`

What this means for you:

- You do **not** have to install a separate database system just to try the dashboard.
- All attendance information is stored in that single `.db` file.

> If the dashboard has been configured with PostgreSQL instead, your IT/development team will know and manage that setup. Non‑technical users usually do not need to worry about this.

---

## 4. Automatic sample data (for demos and testing)

When the application is run with seeding enabled:

- It automatically creates:
  - Many **sample students** (with fake names and roll numbers).
  - Several **subjects** (like Data Structures, Database Management, etc.).
  - A large number of **attendance records** over a period of time.

This means:

- You can immediately see charts, tables, and defaulter lists.
- You can safely **demo** the system to staff and management without entering real student data first.

If you ever need to **reset the demo data** (technical step):

1. Stop the server (`Ctrl + C` in the terminal).
2. Delete the file `backend\attendance.db`.
3. Start the server again (`start.bat`).
4. The database file will be recreated and seeded with fresh demo data.

---

## 5. For technical users – manual commands (Windows)

If you are a developer or IT staff and prefer to run things manually instead of using `start.bat`, you can follow these steps.

### 5.1 Navigate to the project

```bash
cd C:\Users\pawan\Desktop\qwen\attendance_dashboard
```

### 5.2 Activate the virtual environment

```bash
venv\Scripts\activate
```

If this fails, you may need to create the virtual environment first:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 5.3 Start the FastAPI server

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should then see lines like:

```text
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Open your browser at `http://localhost:8000` as described earlier.

To stop the server, press `Ctrl + C` in that terminal.

---

## 6. (Optional) Using PostgreSQL instead of SQLite

For **production** or shared multi‑user deployments, you may prefer **PostgreSQL**.

High‑level steps (for technical staff only):

1. Install PostgreSQL.
2. Create a database:
   ```bash
   createdb attendance_db
   ```
3. Set the `DATABASE_URL` environment variable (example):
   ```bash
   set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_db
   ```
4. Start the server again (via `start.bat` or manual commands).

When `DATABASE_URL` is set, the application will connect to PostgreSQL instead of the local `attendance.db` file.

---

## 7. Troubleshooting (common issues)

### 7.1 The website does not open

- **Check the terminal window**
  - Make sure the black window from `start.bat` is still open.
  - If it has closed, run `start.bat` again.
- **Check the address**
  - Confirm that you typed `http://localhost:8000` (not `https` and no extra spaces).

### 7.2 Port 8000 already in use

Sometimes another program is already using port 8000.

- Quick workaround (technical):

  ```bash
  cd backend
  python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
  ```

  Then open `http://localhost:8001` in your browser instead.

### 7.3 “Module not found” or missing packages

This usually means the Python dependencies are not installed.

```bash
cd C:\Users\pawan\Desktop\qwen\attendance_dashboard
venv\Scripts\activate
pip install -r requirements.txt
```

### 7.4 Database errors or strange data

- If you are only using demo data and something looks wrong, you can reset:

  ```bash
  # From project root, in a terminal
  del backend\attendance.db
  ```

  Then start the application again so it can recreate and reseed the database.

> Only do this if you are okay with **losing all existing data**. For real student data, consult your IT/admin team first.

---

## 8. Summary

- **Non‑technical users**:
  - Double‑click `start.bat`.
  - Open `http://localhost:8000` in your browser.
  - Use the dashboards; ignore the technical details.
- **Technical users**:
  - May run the server manually with `uvicorn`, switch to PostgreSQL, and manage dependencies as needed.

If you are unsure about anything, it is safest to **use only the `start.bat` method** and ask your technical team for help with advanced changes.
