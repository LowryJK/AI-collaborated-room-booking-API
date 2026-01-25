import uuid
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from threading import Lock # Added locking mechanism for booking

app = Flask(__name__)
app.secret_key = "super_secret_key_for_demo"  # Required for session management

# --- IN-MEMORY DATABASE ---
users = []
rooms = []
bookings = []

# Global lock for writing operations
booking_lock = Lock()

# --- MODELS & SEEDING ---
def seed_data():
    # 1. Create Rooms
    room_names = ["Conference Room A", "Meeting Room B", "Quiet Room C"]
    for name in room_names:
        rooms.append({
            "id": str(uuid.uuid4()),
            "name": name
        })

    # 2. Create Users (1 Admin, 3 Standard)
    # Admin
    users.append({
        "id": str(uuid.uuid4()), 
        "first": "Admin", 
        "last": "User", 
        "email": "admin@company.com", 
        "role": "admin"
    })
    
    # Standard Users
    premade_users = [
        ("John", "Doe", "john@test.com"),
        ("Jane", "Smith", "jane@test.com"),
        ("Bob", "Jones", "bob@test.com")
    ]
    for first, last, email in premade_users:
        users.append({
            "id": str(uuid.uuid4()),
            "first": first,
            "last": last,
            "email": email,
            "role": "user"
        })
    
    print(f"System initialized with {len(rooms)} rooms and {len(users)} users.")

# Run seeding immediately
seed_data()

# --- HELPER FUNCTIONS ---
def get_user_by_email(email):
    return next((u for u in users if u["email"] == email), None)

def get_current_user():
    if 'user_id' not in session:
        return None
    return next((u for u in users if u['id'] == session['user_id']), None)

def is_overlapping(room_id, start_dt, end_dt):
    for b in bookings:
        if b["room_id"] == room_id:
            # Logic: (StartA < EndB) and (EndA > StartB)
            if start_dt < b["end_time"] and end_dt > b["start_time"]:
                return True
    return False

# --- ROUTES: VIEWS ---

@app.route('/')
def index():
    user = get_current_user()
    if not user:
        return render_template('index.html', page='login', users=users)
    
    return render_template('index.html', page='dashboard', user=user, rooms=rooms)

@app.route('/rooms/<room_id>/list')
def room_details(room_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('index'))
    
    # 1. Find the room
    room = next((r for r in rooms if r["id"] == room_id), None)
    if not room:
        return "Room not found", 404

    # 2. Filter bookings for this room
    room_bookings = [b for b in bookings if b["room_id"] == room_id]

    # 3. Sort bookings by start time
    room_bookings.sort(key=lambda x: x['start_time'])

    return render_template('room_list.html', room=room, bookings=room_bookings, user=user)

# --- ROUTES: AUTH ---

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    user = get_user_by_email(email)
    if user:
        session['user_id'] = user['id']
        session['user_role'] = user['role']
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/register', methods=['POST'])
def register():
    first = request.form.get('first')
    last = request.form.get('last')
    email = request.form.get('email')

    if not first or not last or not email:
        return "Missing fields", 400
    if "@" not in email:
        return "Invalid email format", 400
    if get_user_by_email(email):
        return "Email already exists", 400

    new_user = {
        "id": str(uuid.uuid4()),
        "first": first,
        "last": last,
        "email": email,
        "role": "user"
    }
    users.append(new_user)
    session['user_id'] = new_user['id']
    session['user_role'] = new_user['role']
    return redirect(url_for('index'))

# --- ROUTES: API ---

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    # Helper to format for Frontend Calendar
    events = []
    current_user_id = session.get('user_id')
    user_role = session.get('user_role')

    for b in bookings:
        events.append({
            "id": b["id"],
            "resourceId": b["room_id"],
            "title": f"Booked by {b['booker_name']}",
            "start": b["start_time"].isoformat(),
            "end": b["end_time"].isoformat(),
            # Frontend uses this to decide if it should show a delete prompt
            "extendedProps": {
                "can_delete": b["user_id"] == current_user_id or user_role == 'admin'
            }
        })
    return jsonify(events)

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    room_id = data.get('roomId')
    start_str = data.get('start')
    end_str = data.get('end')

    # 1. Validation: Data Existence
    if not room_id or not start_str or not end_str:
        return jsonify({"error": "Missing booking details"}), 400

    # Check that room_id actually exists in the in-memory database, if not return error
    room_exists = any(r['id'] == room_id for r in rooms)
    if not room_exists:
        return jsonify({"error": "Invalid Room ID"}), 404

    try:
        # Convert ISO strings to datetime (handle Z or no Z)
        start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00')).replace(tzinfo=None)
        end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00')).replace(tzinfo=None)
    except ValueError:
        return jsonify({"error": "Invalid timestamp format"}), 400

    # 2. Business Rules
    if start_dt < datetime.now():
        return jsonify({"error": "Cannot book in the past"}), 400
    if start_dt >= end_dt:
        return jsonify({"error": "Start time must be before end time"}), 400

    duration = (end_dt - start_dt).total_seconds() / 60
    if duration < 30:
        return jsonify({"error": "Minimum booking duration is 30 minutes"}), 400
    if duration > (8 * 60):
        return jsonify({"error": "Maximum booking duration is 8 hours"}), 400

    # Lock mechanism added here to checking overlap
    with booking_lock:
        if is_overlapping(room_id, start_dt, end_dt):
            return jsonify({"error": "Room is already booked for this time slot"}), 409

        # Create Booking
        new_booking = {
            "id": str(uuid.uuid4()),
            "user_id": user['id'],
            "booker_name": f"{user['first']} {user['last']}",
            "room_id": room_id,
            "start_time": start_dt,
            "end_time": end_dt,
            "created_at": datetime.now()
        }
        bookings.append(new_booking)

    return jsonify({"success": True, "booking": new_booking})

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    with booking_lock:
        booking = next((b for b in bookings if b["id"] == booking_id), None)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        # Check ownership or admin status
        if booking['user_id'] != user['id'] and user['role'] != 'admin':
            return jsonify({"error": "You can only delete your own bookings"}), 403

        bookings.remove(booking)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)