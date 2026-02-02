from flask import Flask, request, render_template, redirect, url_for, Response
from firebase_config import db
from datetime import datetime
import pytz
from google.cloud import firestore

app = Flask(__name__)

ADMIN_PASSWORD = "adminPassword123"  # change this to your own strong password

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Check for password in GET parameters
    password = request.args.get('password')

    if password != ADMIN_PASSWORD:
        return Response(
            "Unauthorized",
            status=401
        )

    # Fetch Firestore data (same as before)
    users_ref = db.collection('users').order_by("timestamp", direction=firestore.Query.DESCENDING)
    docs = users_ref.stream()

    user_list = []
    for doc in docs:
        data = doc.to_dict()
        user_list.append({
            'name': data.get('name', ''),
            'time': data.get('time', '')
        })

    return render_template('admin.html', users=user_list)


# -------------------------------
# Route: form submission page
# -------------------------------
@app.route('/')
def index():
    return render_template('form.html')

# -------------------------------
# Route: handle form submission
# -------------------------------
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    if not name:
        return "Name is required!", 400

    # Current time in Manila
    tz = pytz.timezone('Asia/Manila')
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M")  # hr:min format

    # Save to Firestore with server timestamp
    doc_ref = db.collection('users').document()
    doc_ref.set({
        'name': name,
        'time': current_time,               # human-readable time
        'timestamp': firestore.SERVER_TIMESTAMP  # sortable timestamp
    })

    return redirect(url_for('index'))

# -------------------------------
# Run Flask
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
