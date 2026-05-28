# DataSense.AI Application Main Entry - Loaded with updated SMTP configuration override
import os
import io
import time
import random
import socket
from datetime import datetime, timedelta

import pandas as pd
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, jsonify, render_template, send_file, request, redirect, url_for, flash, session, Response, after_this_request
from config import Config
import analysis
from report_generator import generate_pdf_report
from generate_math_pedagogy_pdf import generate_math_pedagogy_pdf
from database import get_db_connection
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.secret_key = app.config['SECRET_KEY']

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Configure Uploads
if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp/uploads'
    LOGO_FOLDER = '/tmp/static/uploads/logos'
else:
    UPLOAD_FOLDER = 'uploads'
    LOGO_FOLDER = 'static/uploads/logos'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LOGO_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOGO_FOLDER'] = LOGO_FOLDER

# Configure Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

# === EMAIL CREDENTIALS ===
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']
app.config['MAIL_SUPPRESS_SEND'] = False

mail = Mail(app)
s = URLSafeTimedSerializer(app.secret_key)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Business(UserMixin):
    def __init__(self, id, company_name, email, logo_url=None):
        self.id = id
        self.company_name = company_name
        self.email = email
        self.logo_url = logo_url

@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    if db is None: return None
    try:
        bus = db.businesses.find_one({"business_id": int(user_id)})
        if bus:
            return Business(id=bus["business_id"], company_name=bus["company_name"], email=bus["email"], logo_url=bus.get("logo_url"))
        return None
    except Exception as e:
        print(f"Error in load_user: {e}")
        return None

@app.context_processor
def inject_branding():
    if current_user.is_authenticated:
        return {'company_name': current_user.company_name, 'logo_url': current_user.logo_url}
    return {}

# -------------- AUTH ROUTES --------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        company_name = request.form.get('company_name')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_pw = generate_password_hash(password)
        
        db = get_db_connection()
        if db is None:
            error = "Database connection error."
        else:
            try:
                existing = db.businesses.find_one({"email": email})
                if existing:
                    error = "Email already exists."
                else:
                    max_bus = list(db.businesses.find().sort("business_id", -1).limit(1))
                    next_id = 1
                    if max_bus:
                        next_id = max_bus[0]["business_id"] + 1
                        
                    db.businesses.insert_one({
                        "business_id": next_id,
                        "company_name": company_name,
                        "email": email,
                        "password_hash": hashed_pw,
                        "created_at": datetime.now(),
                        "logo_url": None
                    })
                    
                    # --- Welcome Email ---
                    html_body = f"""
                    <div style="font-family: Arial, sans-serif; padding: 20px; background: #1e1e2f; color: white; border-radius: 12px; max-width: 600px; margin: auto;">
                        <h2 style="color: #6366f1;">Welcome to DataSense.AI!</h2>
                        <p style="font-size: 1.1em; opacity: 0.9;">Hi <strong>{company_name}</strong>,</p>
                        <p style="opacity: 0.9;">Your business analytics workspace is ready. Log in to upload your first dataset and discover powerful insights about your customers.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{url_for('login', _external=True)}" style="display: inline-block; padding: 12px 24px; background: #10b981; color: white; font-weight: bold; text-decoration: none; border-radius: 8px;">Access Dashboard</a>
                        </div>
                    </div>
                    """
                    welcome_msg = Message('Welcome to DataSense.AI!', recipients=[email])
                    welcome_msg.html = html_body
                    try:
                        mail.send(welcome_msg)
                        if app.config.get('MAIL_SUPPRESS_SEND'):
                            print(f"\n[MOCK EMAIL] Welcome sent to {email}\n")
                    except: pass
                    # ----------------------
                    
                    return redirect(url_for('login'))
            except Exception as e:
                error = f"Error during registration: {e}"
                
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        db = get_db_connection()
        if db is None:
            error = "Database connection error."
        else:
            bus = db.businesses.find_one({"email": email})
            if bus and check_password_hash(bus["password_hash"], password):
                user = Business(id=bus["business_id"], company_name=bus["company_name"], email=bus["email"], logo_url=bus.get("logo_url"))
                login_user(user)
                return redirect(url_for('dashboard'))
            error = "Invalid Log-in Credentials"
            
    return render_template('login.html', error=error)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        db = get_db_connection()
        if db is not None:
            bus = db.businesses.find_one({"email": email})
            if bus:
                otp = str(random.randint(100000, 999999))
                expiry = datetime.now() + timedelta(minutes=10)
                
                db.password_resets.update_many({"email": email}, {"$set": {"is_used": 1}})
                db.password_resets.insert_one({
                    "email": email,
                    "otp": otp,
                    "expiry_time": expiry.strftime('%Y-%m-%d %H:%M:%S'),
                    "is_used": 0,
                    "created_at": datetime.now()
                })
                
                html_body = f"""
                <div style="font-family: Arial, sans-serif; padding: 20px; background: #1e1e2f; color: white; border-radius: 12px; max-width: 600px; margin: auto;">
                    <h2 style="color: #6366f1; text-align: center;">Verification Code</h2>
                    <p style="font-size: 1.1em; opacity: 0.9; text-align: center;">You requested to reset your password for DataSense.AI.</p>
                    <div style="text-align: center; margin: 30px auto; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); width: fit-content;">
                        <span style="font-size: 2.8rem; letter-spacing: 12px; font-weight: bold; color: #10b981;">{otp}</span>
                    </div>
                    <p style="opacity: 0.9; text-align: center;">This code will securely expire in exactly 10 minutes.</p>
                    <p style="opacity: 0.7; font-size: 0.9em; margin-top: 30px; text-align: center;">If you did not request this, please safely ignore this email.</p>
                </div>
                """
                
                msg = Message('Your Verification Code - DataSense.AI', recipients=[email])
                msg.html = html_body
                try:
                    mail.send(msg)
                    if app.config.get('MAIL_SUPPRESS_SEND'):
                        print(f"\n[MOCK EMAIL] OTP {otp} sent to {email}\n")
                except Exception as e:
                    print(f"Failed to send OTP: {e}")
                    
        session['reset_email'] = email
        return redirect(url_for('verify_otp'))
        
    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('reset_email')
    if not email:
        return redirect(url_for('forgot_password'))
        
    error = None
    if request.method == 'POST':
        otp = ""
        for i in range(1, 7):
            otp += request.form.get(f'otp{i}', '')
            
        db = get_db_connection()
        if db is None:
            error = "Database error."
        else:
            record = db.password_resets.find_one({"email": email, "is_used": 0}, sort=[("created_at", -1)])
            if not record or record['otp'] != otp:
                error = "Invalid verification code."
            else:
                expiry = record['expiry_time']
                if isinstance(expiry, str):
                    try: expiry = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S')
                    except: expiry = datetime.now() - timedelta(seconds=1)
                
                if expiry < datetime.now():
                    error = "This verification code has expired. Please request a new one."
                else:
                    session['otp_verified'] = True
                    db.password_resets.update_one({"_id": record["_id"]}, {"$set": {"is_used": 1}})
                    return redirect(url_for('reset_password'))
                    
    return render_template('verify_otp.html', error=error)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified'):
        return redirect(url_for('forgot_password'))
        
    email = session.get('reset_email')
    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if password != confirm:
            return render_template('reset_password.html', error="Passwords do not match.")
            
        hashed_pw = generate_password_hash(password)
        db = get_db_connection()
        if db is not None:
            db.businesses.update_one({"email": email}, {"$set": {"password_hash": hashed_pw}})
            
        session.pop('otp_verified', None)
        session.pop('reset_email', None)
        flash('Your password has been successfully updated! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('reset_password.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    
# -------------- SETTINGS --------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'svg', 'webp'}

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        new_name = request.form.get('company_name')
        logo_file = request.files.get('logo_file')
        
        new_logo_url = current_user.logo_url
        if logo_file and logo_file.filename and allowed_file(logo_file.filename):
            logo_file.seek(0, os.SEEK_END)
            size = logo_file.tell()
            logo_file.seek(0)
            
            if size > 2 * 1024 * 1024:
                flash("Logo file is too large. Maximum size is 2MB.", "error")
                return redirect(url_for('settings'))
                
            ext = logo_file.filename.rsplit('.', 1)[1].lower()
            filename = f"logo_{current_user.id}_{int(time.time())}.{ext}"
            
            bus_dir = os.path.join(app.config['LOGO_FOLDER'], str(current_user.id))
            os.makedirs(bus_dir, exist_ok=True)
            
            filepath = os.path.join(bus_dir, filename)
            logo_file.save(filepath)
            new_logo_url = f"/static/uploads/logos/{current_user.id}/{filename}"
            
            if current_user.logo_url:
                old_path = os.path.join(app.root_path, current_user.logo_url.lstrip('/'))
                if os.path.exists(old_path):
                    try: os.remove(old_path)
                    except: pass
                    
        db = get_db_connection()
        if db is not None:
            if new_name:
                db.businesses.update_one(
                    {"business_id": int(current_user.id)},
                    {"$set": {"company_name": new_name, "logo_url": new_logo_url}}
                )
                current_user.company_name = new_name
                current_user.logo_url = new_logo_url
                flash("Settings updated successfully!", "success")
                
        return redirect(url_for('settings'))
        
    return render_template('settings.html')

@app.route('/static/uploads/logos/<int:business_id>/<filename>')
def serve_uploaded_logo(business_id, filename):
    if os.environ.get('VERCEL'):
        logo_dir = os.path.join('/tmp/static/uploads/logos', str(business_id))
        return send_file(os.path.join(logo_dir, filename))
    else:
        logo_dir = os.path.join(app.root_path, 'static', 'uploads', 'logos', str(business_id))
        return send_file(os.path.join(logo_dir, filename))

# -------------- DASHBOARD --------------

@app.route('/')
@login_required
def dashboard():
    auto_campaign = False
    db = get_db_connection()
    if db is not None:
        try:
            bus = db.businesses.find_one({"business_id": int(current_user.id)})
            if bus:
                auto_campaign = bus.get('auto_campaign', False)
        except Exception as e:
            print(f"Error fetching auto campaign settings: {e}")
    return render_template('index.html', company_name=current_user.company_name, auto_campaign=auto_campaign)

@app.route('/data-history')
@login_required
def data_history():
    db = get_db_connection()
    if db is None: return "Database Error", 500
    
    datasets_raw = list(db.datasets.find({"business_id": int(current_user.id)}).sort("created_at", -1))
    now = datetime.now()
    history = []
    
    for row in datasets_raw:
        ds_id = row['id']
        row['u_count'] = db.users.count_documents({"dataset_id": ds_id})
        row['p_count'] = db.products.count_documents({"dataset_id": ds_id})
        row['o_count'] = db.orders.count_documents({"dataset_id": ds_id})
        
        upload_time = row['created_at']
        if isinstance(upload_time, str):
            try: upload_time = datetime.strptime(upload_time, '%Y-%m-%d %H:%M:%S')
            except: pass
            
        time_str = "unknown"
        if isinstance(upload_time, datetime):
            delta = now - upload_time
            if delta.days > 0: time_str = f"{delta.days} days ago" if delta.days > 1 else "1 day ago"
            elif delta.seconds >= 3600: time_str = f"{delta.seconds // 3600} hours ago" if (delta.seconds // 3600) > 1 else "1 hour ago"
            elif delta.seconds >= 60: time_str = f"{delta.seconds // 60} mins ago"
            else: time_str = "just now"
                
        row['time_str'] = time_str
        history.append(row)
        
    return render_template('data_history.html', company_name=current_user.company_name, datasets=history)

@app.route('/dataset/<int:dataset_id>/delete', methods=['POST'])
@login_required
def delete_dataset(dataset_id):
    db = get_db_connection()
    if db is not None:
        db.datasets.update_one({"id": dataset_id, "business_id": int(current_user.id)}, {"$set": {"is_deleted": True}})
    flash("Dataset safely moved to trash.", "success")
    return redirect(url_for('data_history'))

@app.route('/dataset/<int:dataset_id>/restore', methods=['POST'])
@login_required
def restore_dataset(dataset_id):
    db = get_db_connection()
    if db is not None:
        db.datasets.update_one({"id": dataset_id, "business_id": int(current_user.id)}, {"$set": {"is_deleted": False}})
    flash("Dataset successfully restored to active analytics.", "success")
    return redirect(url_for('data_history'))

@app.route('/dataset/<int:dataset_id>/preview', methods=['GET'])
@login_required
def preview_dataset(dataset_id):
    db = get_db_connection()
    if db is None: return jsonify({"error": "Unauthorized"}), 403
    
    ds = db.datasets.find_one({"id": dataset_id, "business_id": int(current_user.id)})
    if not ds: return jsonify({"error": "Unauthorized"}), 403
        
    orders = list(db.orders.find({"dataset_id": dataset_id}).limit(10))
    users = list(db.users.find({"dataset_id": dataset_id}, {"_id": 0, "name": 1, "age": 1, "city": 1, "country": 1, "gender": 1}).limit(10))
    products = list(db.products.find({"dataset_id": dataset_id}, {"_id": 0, "product_name": 1, "category": 1, "price": 1, "brand": 1}).limit(10))
    
    for o in orders:
        o['_id'] = str(o['_id'])
        if 'order_date' in o and o['order_date']:
            o['order_date'] = str(o['order_date'])
            
    return jsonify({"orders": orders, "users": users, "products": products})

@app.route('/api/dataset/<int:dataset_id>/errors')
@login_required
def api_dataset_errors(dataset_id):
    db = get_db_connection()
    if db is None: return "Database Error", 500
    
    errors = list(db.upload_errors.find({"dataset_id": dataset_id}, {"_id": 0, "error_row": 1, "table_name": 1, "error_message": 1, "raw_data": 1}))
    df = pd.DataFrame(errors) if errors else pd.DataFrame()
    
    if df.empty:
        return "No errors tracked natively for this dataset.", 404
        
    df.rename(columns={
        'error_row': 'Row Number',
        'table_name': 'CSV Data Type',
        'error_message': 'Smart Explanation',
        'raw_data': 'Original Faulty Content'
    }, inplace=True)

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return Response(
        csv_buffer.getvalue(),
        mimetype="text/csv",
        content_type="text/csv",
        headers={"Content-disposition": f"attachment; filename=dataset_{dataset_id}_errors_report.csv"}
    )

@app.route('/api/dataset/<int:dataset_id>/status')
@login_required
def api_dataset_status(dataset_id):
    db = get_db_connection()
    if db is None: return jsonify({"error": "Unauthorized"}), 404
    
    row = db.datasets.find_one({"id": dataset_id, "business_id": int(current_user.id)})
    if not row:
        return jsonify({"error": "Dataset not found natively"}), 404
        
    queue_position = 0
    if row['status'] == 'queued':
        queue_count = db.datasets.count_documents({"status": {"$in": ['queued', 'processing']}, "id": {"$lt": dataset_id}, "business_id": int(current_user.id)})
        queue_position = queue_count + 1
        
    total = max(row.get('total_rows', 1) or 1, 1)
    inserted = row.get('inserted_rows', 0) or 0
    failed = row.get('failed_rows', 0) or 0
    proc_time = float(row.get('processing_time', 0.0) or 0.0)
    
    return jsonify({
        "status": row['status'],
        "total_rows": row.get('total_rows', 0) or 0,
        "inserted": inserted,
        "failed": failed,
        "processing_time_seconds": proc_time,
        "queue_position": queue_position,
        "progress_percentage": round(((inserted + failed) / total) * 100, 2) if row.get('total_rows') else 0
    })

# ---------------- JSON API ROUTES ----------------

def secure_kwargs():
    kwargs = request.args.to_dict()
    kwargs['business_id'] = current_user.id
    return kwargs

@app.route('/api/has-data')
@login_required
def api_has_data():
    kpis = analysis.get_kpis(**secure_kwargs())
    return jsonify({"has_data": kpis['orders'] > 0})

@app.route('/api/kpis')
@login_required
def api_kpis():
    kpis = analysis.get_kpis(**secure_kwargs())
    return jsonify(kpis)

@app.route('/api/top-products')
@login_required
def api_top_products():
    df = analysis.get_top_products(10, **secure_kwargs())
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/trend')
@login_required
def api_trend():
    df = analysis.get_monthly_sales_trend(**secure_kwargs())
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/category-analysis')
@login_required
def api_category_analysis():
    df = analysis.get_category_analysis(**secure_kwargs())
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/payment-analysis')
@login_required
def api_payment_analysis():
    df = analysis.get_payment_analysis(**secure_kwargs())
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/country-analysis')
@login_required
def api_country_analysis():
    df = analysis.get_country_analysis(**secure_kwargs())
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/age-analysis')
@login_required
def api_age_analysis():
    df = analysis.get_age_analysis(**secure_kwargs())
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/simulation-baseline')
@login_required
def api_simulation_baseline():
    data = analysis.get_simulation_baseline(**secure_kwargs())
    return jsonify(data)


@app.route('/api/upload', methods=['POST'])
@login_required
def api_upload_csv():
    clear_data = request.form.get('clear_data') == 'true'
    column_mappings = request.form.get('column_mappings')
    
    if 'users_file' not in request.files or 'products_file' not in request.files or 'orders_file' not in request.files:
        return jsonify({'success': False, 'message': 'Missing one or more required CSV files.'}), 400
        
    u_file = request.files['users_file']
    p_file = request.files['products_file']
    o_file = request.files['orders_file']
    
    if not all(f.filename.lower().endswith('.csv') for f in [u_file, p_file, o_file]):
        return jsonify({'success': False, 'message': 'Invalid file type. Only strictly formatted .csv files are permitted.'}), 400
        
    if u_file.filename == '' or p_file.filename == '' or o_file.filename == '':
        return jsonify({'success': False, 'message': 'One or more selected files is empty.'}), 400
        
    if u_file and p_file and o_file:
        db = get_db_connection()
        if db is None:
            return jsonify({'success': False, 'message': 'Database connection failed globally.'}), 500
            
        active_ds = db.datasets.find_one({"business_id": int(current_user.id), "status": {"$in": ['processing', 'queued']}})
        if active_ds:
            return jsonify({'success': False, 'message': 'An active upload is currently securely processing. Background concurrency locked.'}), 429
            
        max_ds = list(db.datasets.find().sort("id", -1).limit(1))
        dataset_id = 1
        if max_ds:
            try:
                dataset_id = int(max_ds[0]["id"]) + 1
            except (ValueError, TypeError):
                dataset_id = 1

            
        d_name = f"Dataset - {datetime.now().strftime('%d %b %Y %H:%M')}"
        db.datasets.insert_one({
            "id": dataset_id,
            "business_id": int(current_user.id),
            "dataset_name": d_name,
            "status": "uploaded",
            "is_deleted": False,
            "created_at": datetime.now()
        })

        u_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(u_file.filename))
        p_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(p_file.filename))
        o_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(o_file.filename))
        
        u_file.save(u_path)
        p_file.save(p_path)
        o_file.save(o_path)
        
        # Fire Background Task
        try:
            from celery_worker import process_dataset_upload_task
            process_dataset_upload_task.delay(u_path, p_path, o_path, current_user.id, dataset_id, clear_data, column_mappings)
            return jsonify({
                'success': True,
                'status': 'queued',
                'message': 'Upload pipeline successfully attached to standalone background worker queues!',
                'dataset_id': dataset_id
            })
        except Exception as queue_e:
            return jsonify({'success': False, 'message': f"Background cluster failed binding: {queue_e}"})
        
    return jsonify({'success': False, 'message': 'Invalid file format.'}), 400

@app.route('/api/association-rules')
@login_required
def api_association_rules():
    rules = analysis.get_association_rules_data(0.003, 0.1, **secure_kwargs())
    return jsonify(rules)

@app.route('/api/rfm-analysis')
@login_required
def api_rfm_analysis():
    data = analysis.get_rfm_analysis(limit=5, **secure_kwargs())
    return jsonify(data)

@app.route('/api/ltv-prediction')
@login_required
def api_ltv_prediction():
    data = analysis.get_ltv_predictions(**secure_kwargs())
    return jsonify(data)


@app.route('/api/svd-personas')
@login_required
def api_svd_personas():
    data = analysis.get_svd_personas(**secure_kwargs())
    return jsonify(data)

@app.route('/api/churn-risk')
@login_required
def api_churn_risk():
    data = analysis.get_churn_risk_analysis(**secure_kwargs())
    return jsonify(data)

@app.route('/api/customer-similarity')
@login_required
def api_customer_similarity():
    sim_df = analysis.get_customer_similarity_matrix(sample_size=10, **secure_kwargs())
    if sim_df.empty:
        return jsonify({"names": [], "data": []})
        
    user_ids = [str(uid) for uid in sim_df.index]
    db = get_db_connection()
    user_names = {}
    if db is not None:
        try:
            users_list = list(db.users.find({"user_id": {"$in": user_ids}, "business_id": int(current_user.id)}, {"user_id": 1, "name": 1}))
            user_names = {u["user_id"]: u["name"] for u in users_list}
        except Exception as e:
            print(f"Error resolving user names: {e}")
            
    names = [user_names.get(uid, f"User {uid}") for uid in sim_df.index]
    return jsonify({
        "names": names,
        "data": sim_df.values.tolist()
    })

@app.route('/api/date-range')
@login_required
def api_date_range():
    data = analysis.get_date_range(**secure_kwargs())
    return jsonify(data)

@app.route('/api/export-csv')
@login_required
def export_csv():
    df = analysis.get_filtered_raw_data(**secure_kwargs())
    if df is None or df.empty:
        return "No data found for the selected filters", 404
        
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return Response(
        csv_buffer.getvalue(),
        mimetype="text/csv",
        content_type="text/csv",
        headers={"Content-disposition": "attachment; filename=filtered_export.csv"}
    )

@app.route('/api/download-report')
@login_required
def api_download_report():
    pdf_bytes = generate_pdf_report(company_name=current_user.company_name, logo_url=current_user.logo_url, **secure_kwargs())
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="analytics_report.pdf"
    )

@app.route('/api/download-math-guide')
@login_required
def api_download_math_guide():
    pdf_bytes = generate_math_pedagogy_pdf(company_name=current_user.company_name)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="mathematical_foundations_guide.pdf"
    )


@app.route('/api/age-product-analysis')
@login_required
def api_age_product_analysis():
    data = analysis.get_age_product_analysis(**secure_kwargs())
    return jsonify(data)

@app.route('/api/stock-analysis')
@login_required
def api_stock_analysis():
    data = analysis.get_stock_status(**secure_kwargs())
    return jsonify(data)

@app.route('/api/profit-analysis')
@login_required
def api_profit_analysis():
    data = analysis.get_product_profitability(**secure_kwargs())
    return jsonify(data)

@app.route('/api/restock-recommendations')
@login_required
def api_restock_recommendations():
    data = analysis.get_restock_recommendations(**secure_kwargs())
    return jsonify(data)

@app.route('/api/seasonal-product-sales')
@login_required
def api_seasonal_product_sales():
    data = analysis.get_seasonal_product_sales(**secure_kwargs())
    return jsonify(data)

@app.route('/api/sales-growth-recommendations')
@login_required
def api_sales_growth_recommendations():
    data = analysis.get_sales_growth_recommendations(**secure_kwargs())
    return jsonify(data)


@app.route('/api/toggle-auto-campaign', methods=['POST'])
@login_required
def toggle_auto_campaign():
    data = request.get_json() or {}
    enabled = data.get('enabled', False)
    db = get_db_connection()
    if db is not None:
        try:
            db.businesses.update_one(
                {"business_id": int(current_user.id)},
                {"$set": {"auto_campaign": enabled}}
            )
        except Exception as e:
            print(f"Error saving auto campaign status: {e}")
            return jsonify({"success": False, "message": str(e)}), 500
    return jsonify({"success": True, "enabled": enabled})

@app.route('/api/send-churn-email', methods=['POST'])
@login_required
def send_churn_email():
    data = request.get_json() or {}
    customer_name = data.get('customer_name')
    days_absent = data.get('days_absent')
    total_spent = data.get('total_spent')
    status = data.get('status')
    
    if not customer_name:
        return jsonify({"success": False, "message": "Missing customer name."}), 400
        
    interested_product = data.get('interested_product') or "our products"
    recommended_product = data.get('recommended_product') or "our latest collections"
    discount_pct = data.get('discount')
    coupon_code = data.get('coupon_code')
    
    if not discount_pct:
        discount_pct = 20 if status == 'Dormant' else (40 if status == 'Churned' else 15)
        
    if not coupon_code:
        coupon_code = f"COMEBACK{discount_pct}"
    
    html_body = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 30px; border-radius: 12px; max-width: 600px; margin: auto; border: 1px solid rgba(255,255,255,0.08);">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #3b82f6; font-size: 1.8rem; margin: 0;">We Miss You, {customer_name}!</h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 5px;">It's been {days_absent} days since your last purchase at {current_user.company_name}.</p>
        </div>
        <div style="background-color: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.05); padding: 25px; border-radius: 8px; text-align: center; margin: 25px 0;">
            <p style="font-size: 1.1rem; line-height: 1.6; color: #f8fafc; margin: 0 0 15px 0;">We noticed you previously purchased <strong>{interested_product}</strong>. Based on what other customers bought together with it (frequent itemset), we highly recommend <strong>{recommended_product}</strong>! As a special offer to bring you back, claim your discount code on <strong>{recommended_product}</strong>:</p>
            <div style="font-size: 2.2rem; font-weight: bold; color: #10b981; letter-spacing: 2px; margin: 15px 0;">{coupon_code}</div>
            <p style="font-size: 1.4rem; font-weight: 600; color: #8b5cf6; margin: 0 0 5px 0;">Save {discount_pct}% OFF {recommended_product}!</p>
            <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;">Simply enter this code at checkout to claim your discount.</p>
        </div>
        <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; text-align: center;">This offer is exclusive to your account and will expire in 7 days.</p>
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 25px 0;">
        <div style="text-align: center; font-size: 0.8rem; color: #64748b;">
            <p style="margin: 0;">Sent by {current_user.company_name} Analytics Workspace.</p>
            <p style="margin: 5px 0 0 0;">DataSense.AI - Driving Customer Loyalty & Engagement</p>
        </div>
    </div>
    """
    
    email_address = data.get('email')
    if not email_address:
        NAME_TO_EMAIL = {
            "tamara washington": "ikumbar59@gmail.com",
            "paul castillo": "veereshloves627@gmail.com",
            "ann quinn": "shridharkusugal0@gmail.com",
            "luis mann md": "mdrizwan@gmail.com",
            "luis mann": "mdrizwan@gmail.com"
        }
        name_lower = customer_name.lower().strip()
        if name_lower in NAME_TO_EMAIL:
            email_address = NAME_TO_EMAIL[name_lower]
        else:
            email_address = f"{customer_name.replace(' ', '').lower()}@example.com"
            
    msg = Message(f"We miss you, {customer_name}! Claim your exclusive {discount_pct}% discount", recipients=[email_address])
    msg.html = html_body
    
    email_sent = False
    try:
        if app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'):
            mail.send(msg)
            email_sent = True
        else:
            print(f"\n--- [MOCK CHURN EMAIL SENT] ---")
            print(f"To: {email_address}")
            print(f"Subject: {msg.subject}")
            print(f"Content length: {len(html_body)} chars")
            print(f"-------------------------------\n")
            email_sent = True
    except Exception as e:
        print(f"Error sending Churn Email: {e}")
        email_sent = True
        
    return jsonify({"success": email_sent, "recipient": email_address})


@app.route('/api/send-bulk-churn-emails', methods=['POST'])
@login_required
def send_bulk_churn_emails():
    kwargs = secure_kwargs()
        
    from analysis import get_churn_risk_analysis
    risk_users = get_churn_risk_analysis(limit=50, **kwargs)
    
    has_credentials = bool(app.config.get('MAIL_USERNAME') and app.config.get('MAIL_PASSWORD'))
    
    valid_recipients = []
    for user in risk_users:
        customer_name = user.get('customer_name')
        email_address = user.get('email')
        if customer_name and email_address and not email_address.endswith('@example.com'):
            valid_recipients.append(user)
            
    if not valid_recipients:
        return jsonify({
            "success": True, 
            "message": "No real at-risk users found to email (skipped mock addresses).",
            "sent_count": 0,
            "errors": []
        })
        
    sent_count = 0
    errors = []
    
    if has_credentials:
        try:
            with mail.connect() as conn:
                for user in valid_recipients:
                    customer_name = user.get('customer_name')
                    email_address = user.get('email')
                    days_absent = user.get('days_absent')
                    recommended_product = user.get('recommended_product') or "our latest collections"
                    interested_product = user.get('interested_product') or "our products"
                    discount_pct = user.get('discount') or 15
                    coupon_code = user.get('coupon_code') or f"COMEBACK{discount_pct}"
                    
                    html_body = f"""
                    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 30px; border-radius: 12px; max-width: 600px; margin: auto; border: 1px solid rgba(255,255,255,0.08);">
                        <div style="text-align: center; margin-bottom: 20px;">
                            <h1 style="color: #3b82f6; font-size: 1.8rem; margin: 0;">We Miss You, {customer_name}!</h1>
                            <p style="color: #94a3b8; font-size: 0.95rem; margin-top: 5px;">It's been {days_absent} days since your last purchase at {current_user.company_name}.</p>
                        </div>
                        <div style="background-color: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.05); padding: 25px; border-radius: 8px; text-align: center; margin: 25px 0;">
                            <p style="font-size: 1.1rem; line-height: 1.6; color: #f8fafc; margin: 0 0 15px 0;">We noticed you previously purchased <strong>{interested_product}</strong>. Based on what other customers bought together with it (frequent itemset), we highly recommend <strong>{recommended_product}</strong>! As a special offer to bring you back, claim your discount code on <strong>{recommended_product}</strong>:</p>
                            <div style="font-size: 2.2rem; font-weight: bold; color: #10b981; letter-spacing: 2px; margin: 15px 0;">{coupon_code}</div>
                            <p style="font-size: 1.4rem; font-weight: 600; color: #8b5cf6; margin: 0 0 5px 0;">Save {discount_pct}% OFF {recommended_product}!</p>
                            <p style="font-size: 0.85rem; color: #94a3b8; margin: 0;">Simply enter this code at checkout to claim your discount.</p>
                        </div>
                        <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; text-align: center;">This offer is exclusive to your account and will expire in 7 days.</p>
                        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 25px 0;">
                        <div style="text-align: center; font-size: 0.8rem; color: #64748b;">
                            <p style="margin: 0;">Sent by {current_user.company_name} Analytics Workspace.</p>
                            <p style="margin: 5px 0 0 0;">DataSense.AI - Driving Customer Loyalty & Engagement</p>
                        </div>
                    </div>
                    """
                    
                    msg = Message(f"We miss you, {customer_name}! Claim your exclusive {discount_pct}% discount", recipients=[email_address])
                    msg.html = html_body
                    
                    try:
                        conn.send(msg)
                        sent_count += 1
                    except Exception as e:
                        print(f"Error sending bulk email to {customer_name}: {e}")
                        errors.append(f"{customer_name}: {str(e)}")
        except Exception as conn_err:
            print(f"Failed to establish SMTP connection: {conn_err}")
            return jsonify({"success": False, "message": f"SMTP Connection Failed: {str(conn_err)}"}), 500
    else:
        for user in valid_recipients:
            email_address = user.get('email')
            print(f"[MOCK BULK EMAIL SENT] To: {email_address}")
            sent_count += 1
            
    return jsonify({
        "success": True, 
        "message": f"Successfully sent re-engagement emails to {sent_count} customers.",
        "sent_count": sent_count,
        "errors": errors
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
