from flask import Flask, jsonify, request, session, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pandas as pd
import re
import json







app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
  # Replace with secure random value
  
REGISTRATION_CODE = os.environ.get("REGISTRATION_CODE")  

# In-memory user "database"
users = {}




@app.route('/login-page')
def login_page():
    return render_template('login.html')



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    reg_code = data.get('reg_code')

    print(f"Received registration code: {reg_code}")  # Debugging line
    print("Received registration code from user:", reg_code)
    print("Expected registration code from env:", os.environ.get("REGISTRATION_CODE"))


    if reg_code != os.environ.get("REGISTRATION_CODE"):
        return jsonify({"error": "Invalid registration code"}), 403

    if username in users:
        return jsonify({"error": "User already exists"}), 400

    users[username] = generate_password_hash(password)
    save_users(users)
    return jsonify({"message": "User registered successfully"})





@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    stored_password_hash = users.get(username)
    if not stored_password_hash or not check_password_hash(stored_password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    session['username'] = username
    return jsonify({"message": f"Welcome {username}!"})


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({"message": "Logged out"})


@app.route('/whoami', methods=['GET'])
def whoami():
    username = session.get('username')
    if not username:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({"username": username})

@app.route('/search-page')
def search_page():
    return render_template('search.html')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

USER_FILE = 'users.json'

def load_users():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            print("⚠️ Warning: users.json is corrupted. Reinitializing.")
            return {}
    return {}


def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

users = load_users()

# Function to check for valid file types (Excel files)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# This function is responsible for searching the item in the loaded Excel file
def search_item_in_excel(item_name, selected_file):
    try:
        xls = pd.read_excel(selected_file, sheet_name=None)
        results = []
        for sheet_name, df in xls.items():
            sheet_results = df[df.apply(lambda row: row.astype(str).str.contains(item_name, case=False).any(), axis=1)]
            for _, row in sheet_results.iterrows():
                values = row.astype(str).tolist()
                number_like = [v for v in values if re.match(r'^[\d,.]+$', v)]
                unit_price = None
                if len(number_like) >= 2:
                    try:
                        unit_price = int(number_like[-2].replace(",", ""))
                    except ValueError:
                        pass
                summary = " ".join(values[:6])
                results.append({
                    'sheet': sheet_name,
                    'summary': summary,
                    'price': unit_price if unit_price else 'N/A'
                })
        return results
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}


# Route to handle the search request
@app.route('/search', methods=['POST'])
def search_item():
    item_name = request.form.get('item_name')
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        results = search_item_in_excel(item_name, file_path)
        return jsonify(results)

    return jsonify({"error": "Invalid file format"}), 400

if __name__ == "__main__":
    app.run(debug=True)
