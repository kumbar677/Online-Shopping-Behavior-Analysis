# 🛒 DataSense.AI — Online Shopping Behaviour Analysis

A multi-tenant SaaS analytics platform built with **Flask** and **MySQL** that lets businesses upload shopping data (Users, Products, Orders) and get powerful insights — including trend analysis, customer segmentation, association rules, churn prediction, and PDF report generation.

---

## 📋 Prerequisites

Before you begin, make sure you have the following installed on your system:

| Software | Version | Download Link |
|----------|---------|---------------|
| **Python** | 3.10 or higher | [python.org/downloads](https://www.python.org/downloads/) |
| **MySQL Server** | 8.0+ | [dev.mysql.com/downloads](https://dev.mysql.com/downloads/mysql/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/downloads) |
| **Redis** _(optional, for background uploads)_ | Latest | [redis.io/download](https://redis.io/download) |

> **Windows Users:** During Python installation, make sure to check ✅ **"Add Python to PATH"**.

---

## 🚀 Setup Instructions (Step by Step)

### Step 1 — Clone or Copy the Project

If cloning from GitHub:
```bash
git clone <repository-url>
cd "online shopping behaviour analysis"
```

Or if you received the folder directly, just open a terminal inside the project folder.

---

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

**Activate it:**

- **Windows (Command Prompt):**
  ```bash
  venv\Scripts\activate
  ```
- **Windows (PowerShell):**
  ```bash
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

> You should see `(venv)` appear at the beginning of your terminal prompt.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This will install Flask, pandas, numpy, matplotlib, scikit-learn, and all other required packages.

---

### Step 4 — Set Up MySQL Database

1. **Open MySQL** (via MySQL Workbench, terminal, or command prompt):
   ```bash
   mysql -u root -p
   ```

2. **Create the database:**
   ```sql
   CREATE DATABASE shopping_analysis;
   USE shopping_analysis;
   ```

3. **Import the schema** (run this from the project folder terminal, NOT inside MySQL):
   ```bash
   mysql -u root -p shopping_analysis < schema.sql
   ```

   > **Note:** The tables must be created in the correct order due to foreign key dependencies. If you get errors with the command above, open `schema.sql` in MySQL Workbench and execute the tables in this order:
   > 1. `businesses`
   > 2. `datasets`
   > 3. `users`
   > 4. `products`
   > 5. `orders`
   > 6. `password_resets`
   > 7. `upload_errors`

---

### Step 5 — Configure Environment Variables

Create a file named **`.env`** in the project root folder with this content:

```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_MYSQL_PASSWORD
MYSQL_DATABASE=shopping_analysis
SECRET_KEY=any-random-secret-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
REDIS_URL=redis://127.0.0.1:6379/0
FLASK_ENV=development
```

> ⚠️ **Important Notes:**
> - Replace `YOUR_MYSQL_PASSWORD` with your actual MySQL root password.
> - For `MAIL_PASSWORD`, you need a **Gmail App Password** (not your regular Gmail password). [How to generate one →](https://support.google.com/accounts/answer/185833)
> - If you don't need email features (password reset, welcome emails), you can leave the mail fields as-is — the app will still work.

---

### Step 6 — Run the Application

```bash
python app.py
```

You should see output like:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

**Open your browser and go to:** [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### Step 7 _(Optional)_ — Start Background Worker for CSV Uploads

If you have **Redis** installed and running, you can enable background CSV processing:

1. **Start Redis server** (in a separate terminal)
2. **Start the Celery worker** (in another separate terminal, with venv activated):
   ```bash
   celery -A celery_worker worker --loglevel=info --pool=gevent
   ```

> Without Redis/Celery, CSV upload processing will show a connection error. The rest of the app (dashboard, analytics, reports) works without it.

---

## 🎯 How to Use

1. **Register** a new business account at `/register`
2. **Log in** with your credentials
3. **Upload CSV data** — You need 3 CSV files:
   - `users.csv` — columns: `user_id, name, city, state, country, age, gender`
   - `products.csv` — columns: `product_id, product_name, category, price, brand, discount`
   - `orders.csv` — columns: `order_id, user_id, product_id, quantity, order_date, total_amount, payment_method, order_status`
4. **Explore the Dashboard** — View KPIs, charts, and analytics
5. **Download Reports** — Generate PDF analytics reports

---

## 📁 Project Structure

```
online shopping behaviour analysis/
├── app.py                 # Main Flask application
├── analysis.py            # Analytics engine (KPIs, trends, ML)
├── config.py              # Configuration loader
├── database.py            # MySQL connection pool
├── data_import.py         # CSV upload & data ingestion
├── celery_worker.py       # Background task worker
├── report_generator.py    # PDF report generation
├── schema.sql             # Database schema (CREATE TABLE statements)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this yourself)
├── seed_data.py           # Sample data seeder (optional)
├── static/                # CSS, JS, images
├── templates/             # HTML templates (Jinja2)
├── uploads/               # Temporary CSV upload storage
└── venv/                  # Virtual environment (don't share this)
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'xyz'` | Run `pip install -r requirements.txt` again |
| `Access denied for user 'root'` | Check your MySQL password in `.env` |
| `Database 'shopping_analysis' doesn't exist` | Run `CREATE DATABASE shopping_analysis;` in MySQL |
| `Can't connect to MySQL server` | Make sure MySQL service is running |
| `Table doesn't exist` | Import `schema.sql` into your database (see Step 4) |
| App runs but CSV upload fails | Redis + Celery worker needs to be running (see Step 7) |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-Login, Flask-Mail
- **Database:** MySQL 8.0+ with connection pooling
- **Analytics:** Pandas, NumPy, SciPy, Scikit-learn, Mlxtend
- **Visualization:** Matplotlib, Chart.js (frontend)
- **Reports:** FPDF2, ReportLab
- **Task Queue:** Celery + Redis + Gevent
- **Frontend:** HTML5, CSS3, JavaScript, Jinja2 Templates

---

## 📄 License

This project is developed for educational/academic purposes.

---

> **Built with ❤️ by Mohammad Rizwan**
