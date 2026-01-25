import uuid
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from threading import Lock

app = Flask(__name__)
app.secret_key = "super_secret_key_for_demo"

# --- DOMAIN MODELS (CLASSES) ---

class User:
    def __init__(self, uid, first, last, email, role="user"):
        self.id = uid
        self.first = first
        self.last = last
        self.email = email
        self.role = role

    def to_dict(self):
        """Helper to serialize object for API responses if needed"""
        return {
            "id": self.id,
            "first": self.first,
            "last": self.last,
            "email": self.email,
            "role": self.role
        }

class Room:
    def __init__(self, rid, name):
        self.id = rid
        self.name = name
    
    def to_dict(self):
        return {"id": self.id, "name": self.name}

class Booking:
    def __init__(self, bid, user_id, booker_name, room_id, start_time, end_time, created_at):
        self.id = bid
        self.user_id = user_id
        self.booker_name = booker_name
        self.room_id = room_id
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "booker_name": self.booker_name,
            "room_id": self.room_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "created_at": self.created_at.isoformat()
        }

# --- IN-MEMORY DATABASE ---
users = []
rooms = []
bookings = []

# Global lock for writing operations
booking_lock = Lock()

# --- SEEDING ---
def seed_data():
    # 1. Create Rooms
    room_names = ["Conference Room A", "Meeting Room B", "Quiet Room C"]
    for name in room_names:
        rooms.append(Room(str(uuid.uuid4()), name))

    # 2. Create Users
    # Admin
    users.append(User(
        str(uuid.uuid4()), "Admin", "User", "admin@company.com", "admin"
    ))
    
    # Standard Users
    premade_users = [
        ("John", "Doe", "john@test.com"),
        ("Jane", "Smith", "jane@test.com"),
        ("Bob", "Jones", "bob@test.com")
    ]
    for first, last, email in premade_users:
        users.append(User(
            str(uuid.uuid4()), first, last, email, "user"
        ))
    
    print(f"System initialized with {len(rooms)} rooms and {len(users)} users.")

seed_data()

# --- HELPER FUNCTIONS ---
def get_user_by_email(email):
    # Changed from u['email'] to u.email
    return next((u for u in users if u.email == email), None)

def get_current_user():
    if 'user_id' not in session:
        return None
    # Changed from u['id'] to u.id
    return next((u for u in users if u.id == session['user_id']), None)

def is_overlapping(room_id, start_dt, end_dt):
    for b in bookings:
        if b.room_id == room_id:
            # Logic: (StartA < EndB) and (EndA > StartB)
            # Accessing attributes directly
            if start_dt < b.end_time and end_dt > b.start_time:
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
    room = next((r for r in rooms if r.id == room_id), None)
    if not room:
        return "Room not found", 404

    # 2. Filter bookings for this room
    room_bookings = [b for b in bookings if b.room_id == room_id]

    # 3. Sort bookings by start time
    room_bookings.sort(key=lambda x: x.start_time)

    return render_template('room_list.html', room=room, bookings=room_bookings, user=user)

# --- ROUTES: AUTH ---

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    user = get_user_by_email(email)
    if user:
        session['user_id'] = user.id
        session['user_role'] = user.role
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

    new_user = User(
        uid=str(uuid.uuid4()),
        first=first,
        last=last,
        email=email,
        role="user"
    )
    users.append(new_user)
    session['user_id'] = new_user.id
    session['user_role'] = new_user.role
    return redirect(url_for('index'))

# --- ROUTES: API ---

@app.route('/api/bookings', methods=['GET'])
def get_bookings():

    # Get query parameters
    start_param = request.args.get('start')
    end_param = request.args.get('end')

    events = []
    current_user_id = session.get('user_id')
    user_role = session.get('user_role')

    # Parse range (if provided) to filter logic
    range_start = None
    range_end = None
    
    if start_param and end_param:
        try:
            range_start = datetime.fromisoformat(start_param.replace('Z', '+00:00')).astimezone(timezone.utc)
            range_end = datetime.fromisoformat(end_param.replace('Z', '+00:00')).astimezone(timezone.utc)
        except ValueError:
            pass

    for b in bookings:
        # Skip bookings entirely outside the requested range
        if range_start and range_end:
            if b.end_time <= range_start or b.start_time >= range_end:
                continue

        events.append({
            "id": b.id,
            "resourceId": b.room_id,
            "title": f"Booked by {b.booker_name}",
            "start": b.start_time.isoformat(),
            "end": b.end_time.isoformat(),
            "extendedProps": {
                "can_delete": b.user_id == current_user_id or user_role == 'admin'
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

    if not room_id or not start_str or not end_str:
        return jsonify({"error": "Missing booking details"}), 400

    # Check room existence using object attribute
    room_exists = any(r.id == room_id for r in rooms)
    if not room_exists:
        return jsonify({"error": "Invalid Room ID"}), 404

    try:
        start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00')).astimezone(timezone.utc)
        end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00')).astimezone(timezone.utc)
    except ValueError:
        return jsonify({"error": "Invalid timestamp format"}), 400

    now_utc = datetime.now(timezone.utc)

    if start_dt < now_utc:
        return jsonify({"error": "Cannot book in the past"}), 400
    if start_dt >= end_dt:
        return jsonify({"error": "Start time must be before end time"}), 400

    duration = (end_dt - start_dt).total_seconds() / 60
    if duration < 30:
        return jsonify({"error": "Minimum booking duration is 30 minutes"}), 400
    if duration > (8 * 60):
        return jsonify({"error": "Maximum booking duration is 8 hours"}), 400

    with booking_lock:
        if is_overlapping(room_id, start_dt, end_dt):
            return jsonify({"error": "Room is already booked for this time slot"}), 409

        # Instantiate Booking Object
        new_booking = Booking(
            bid=str(uuid.uuid4()),
            user_id=user.id,
            booker_name=f"{user.first} {user.last}",
            room_id=room_id,
            start_time=start_dt,
            end_time=end_dt,
            created_at=now_utc
        )
        bookings.append(new_booking)

    # Return serialized object
    return jsonify({"success": True, "booking": new_booking.to_dict()}), 201

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    with booking_lock:
        # Find booking by attribute
        booking = next((b for b in bookings if b.id == booking_id), None)
        if not booking:
            return jsonify({"error": "Booking not found"}), 404

        # Check permissions using attributes
        if booking.user_id != user.id and user.role != 'admin':
            return jsonify({"error": "You can only delete your own bookings"}), 403

        bookings.remove(booking)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)