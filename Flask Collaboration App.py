from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store room-specific data (for simplicity, in-memory storage)
rooms = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create-room', methods=['POST'])
def create_room():
    """API to create a new collaboration room."""
    room_id = request.json.get('room_id')
    if room_id in rooms:
        return jsonify({"message": "Room already exists!"}), 400
    rooms[room_id] = {"users": [], "messages": []}
    return jsonify({"message": f"Room '{room_id}' created successfully."}), 200

@socketio.on('join_room')
def handle_join(data):
    """Handle user joining a room."""
    room_id = data['room']
    username = data['username']
    
    if room_id not in rooms:
        emit('error', {'message': f"Room '{room_id}' does not exist."})
        return
    
    join_room(room_id)
    rooms[room_id]['users'].append(username)
    emit('user_joined', {'username': username, 'room': room_id}, room=room_id)

@socketio.on('message')
def handle_message(data):
    """Handle messages sent to a room."""
    room_id = data['room']
    message = data['message']
    username = data['username']

    if room_id in rooms:
        rooms[room_id]['messages'].append({'username': username, 'message': message})
        emit('message', {'username': username, 'message': message}, room=room_id)

@socketio.on('leave_room')
def handle_leave(data):
    """Handle user leaving a room."""
    room_id = data['room']
    username = data['username']

    if room_id in rooms and username in rooms[room_id]['users']:
        rooms[room_id]['users'].remove(username)
        leave_room(room_id)
        emit('user_left', {'username': username, 'room': room_id}, room=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
