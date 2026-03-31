from flask import Flask, render_template, request, redirect, url_for, flash, session
from tinydb import TinyDB, Query
import bcrypt, re
import requests
import datetime
import math
from urllib.parse import urlparse
app = Flask(__name__)

db = TinyDB('uporabniki.json')
Uporabnik = Query()
app.secret_key = 'matijajepeder'


@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        if action == 'delete':
            db.remove(Uporabnik.username == username)
            flash(f'User {username} deleted successfully')
        elif action == 'make_admin':
            db.update({'is_admin': True}, Uporabnik.username == username)

    users = db.all()
    return render_template('admin.html', users=users)

#login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin':
            session['username'] = username
            return redirect(url_for('admin_panel'))

        user = db.get(Uporabnik.username == username)
        if user and user['password'] == password:
            session['username'] = username
            #flash('Login Successful')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')
    
    return render_template('login.html')

#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match")
            return render_template('register.html')
        
        if not username:  # Generate a username if the field is empty
            api_url = 'https://api.api-ninjas.com/v1/randomuser'
            response = requests.get(api_url, headers={'X-Api-Key': 'YOUR_API_KEY'})
            if response.status_code == requests.codes.ok:
                random_user = response.json()
                username = random_user.get('username', 'random_user')
            else:
                flash("Failed to generate username")
                return render_template('register.html')

        user = db.get(Uporabnik.username == username)
        if user:
            flash("Username already exists")
            return render_template('register.html')
        
        
        db.insert({'username': username, 'password': password})

        session['username'] = username
        #flash('Registration successful!')
        return redirect(url_for('setup_profile'))
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')


#profile page
@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('You need to login')
        return(url_for('login'))
    
    username = session['username']
    user = db.get(Uporabnik.username == username)

    if not user:
        #flash('User not found')
        return redirect(url_for('home'))
    return render_template('profile.html', user = user)

"""@app.route('/edit_profile')
def edit_profile():
    return render_template('edit_profile.html')"""
#kreiranje profila in dodajanje "lastnosti"
@app.route('/setup_profile', methods=['GET', 'POST'])
def setup_profile():

    username = session['username']

    if request.method == 'POST':
        
        name = request.form.get('name')
        surname = request.form.get('surname')
        genre = request.form.get('genre')
        instrument = request.form.get('instrument')
        location = request.form.get('location')
        goals = request.form.get('goals')
        experience = request.form.get('experience')

        db.update({
            
            'name': name,
            'surname': surname,
            'genre': genre,
            'instrument': instrument,
            'location': location,
            'goals': goals,
            'experience': experience
        }, Uporabnik.username == username)
        return redirect(url_for('login'))
    return render_template('setup_profile.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    #flash('Logged out successfully')
    return redirect(url_for('index'))
#urejanje profila | ni se dokoncan
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    username = session['username']
    user = db.get(Uporabnik.username == username)
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        genre = request.form.get('genre')
        instrument = request.form.get('instrument')
        location = request.form.get('location')
        goals = request.form.get('goals')
        experience = request.form.get('experience')
        profile_picture = request.form.get('profile_picture')
        youtube = request.form.get('youtube')
        instagram = request.form.get('instagram')
        tiktok = request.form.get('tiktok')

        db.update({
            'name': name,
            'surname': surname,
            'genre': genre,
            'instrument': instrument,
            'location': location,
            'goals': goals,
            'experience': experience,
            'profile_picture': profile_picture,
            'youtube': youtube,
            'instagram': instagram,
            'tiktok': tiktok
        }, Uporabnik.username == username)
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)

def geocode(location):
    """Vrne (lat, lon) za dano lokacijo ali None."""
    if not location:
        return None
    try:
        resp = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': location, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'GlasbenikiConnect/1.0'},
            timeout=5
        )
        data = resp.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None

def haversine_km(coord1, coord2):
    """Razdalja v km med dvema (lat, lon) koordinatama."""
    R = 6371
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

#pogledas profil
@app.route('/account/<username>')
def view_account(username):
    user = db.get(Uporabnik.username == username)
    if not user:
        return redirect(url_for('home'))
    user_events = events_db.search(Event.username == username)
    distance_km = None
    if 'username' in session and session['username'] != username:
        current_user = db.get(Uporabnik.username == session['username'])
        if current_user and current_user.get('location') and user.get('location'):
            coord_me = geocode(current_user['location'])
            coord_them = geocode(user['location'])
            if coord_me and coord_them:
                distance_km = round(haversine_km(coord_me, coord_them))
    return render_template('account.html', user=user, events=user_events, distance_km=distance_km)


        

@app.route('/find_people', methods = ['GET', 'POST'])
def find_people():
    vnos = ""
    results = []
    users = db.all()
    instrument = ""
    location = ""
    genre = ""
    experience = ""
    if request.method == 'POST':
        vnos = request.form.get('vnos', '').strip()
        instrument = request.form.get('instrument', '').strip()
        location = request.form.get('location', '').strip()
        genre = request.form.get('genre', '').strip()
        experience = request.form.get('experience', '').strip()

        def user_matches(user):
            if vnos:
                v = vnos.lower()
                if not (
                    v in (user.get('username','') or '').lower() or
                    v in (user.get('name','') or '').lower() or
                    v in (user.get('surname','') or '').lower()
                ):
                    return False
            if instrument and (user.get('instrument','') != instrument):
                return False
            if location and (location.lower() not in (user.get('location','') or '').lower()):
                return False
            if genre and (user.get('genre','') != genre):
                return False
            if experience and (user.get('experience','') != experience):
                return False
            return True

        results = [u for u in users if user_matches(u)]

    # Izračunaj razdalje do vseh uporabnikov
    distances = {}
    if 'username' in session:
        current_user = db.get(Uporabnik.username == session['username'])
        if current_user and current_user.get('location'):
            coord_me = geocode(current_user['location'])
            if coord_me:
                for u in users:
                    if u.get('username') != session['username'] and u.get('location'):
                        coord_them = geocode(u['location'])
                        if coord_them:
                            distances[u['username']] = round(haversine_km(coord_me, coord_them))

    return render_template('find_people.html', results=results, users=users, vnos=vnos, instrument=instrument, location=location, genre=genre, experience=experience, distances=distances)

@app.route('/generate_username', methods=['GET'])
def generate_username():
    url = 'https://api.api-ninjas.com/v1/randomuser'
    response = requests.get(url, headers={'X-Api-Key': 'ZnZWZrkHwGuE+xOhT7778g==mXjeyDDTrdIOYgGq'})
    if response.status_code == requests.codes.ok:
        random_user = response.json()
        username = random_user.get('username', 'random_user')
        return {'username': username}
    else:
        return {'error'}, 500



@app.route('/calendar')
def calendar():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    events = events_db.search(Event.username == username)

    return render_template('calendar.html', events=events)

events_db = TinyDB('events.json')
Event = Query()

@app.route('/reset_calendar', methods=['POST'])
def reset_calendar():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    events_db.remove(Event.username == username)
    return redirect(url_for('calendar'))

@app.route('/add_event', methods=['POST'])
def add_event():
    if 'username' not in session:
        flash("Login required")
        return redirect(url_for('login'))

    username = session['username']
    date = request.form['date']           # npr. "2026-03-12"
    title = request.form['title']         # npr. "Vaja"
    status = request.form['status']       # npr. "busy", "free" ali "maybe"

    if not title:
        flash("Title is required")
        return redirect(url_for('calendar'))

    events_db.insert({
        'username': username,
        'date': date,
        'title': title,
        'status': status
    })
    return redirect(request.referrer)      # nazaj na stran od koder smo poslali form






messages_db = TinyDB('messages.json')
Message = Query()

private_messages_db = TinyDB('private_messages.json')
PrivateMessage = Query()

groups_db = TinyDB('groups.json')
Group = Query()

group_messages_db = TinyDB('group_messages.json')
GroupMessage = Query()


def resolve_back_url(next_url, fallback_endpoint):
    """Allow only local relative URLs as back target to avoid open redirects."""
    fallback_url = url_for(fallback_endpoint)
    if not next_url:
        return fallback_url

    parsed = urlparse(next_url)
    is_local_relative = parsed.scheme == '' and parsed.netloc == '' and next_url.startswith('/') and not next_url.startswith('//')
    if is_local_relative:
        return next_url
    return fallback_url

@app.route('/chat', methods=['GET','POST'])
def chat_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('private_messages'))

@app.route('/private_chat/<recipient>', methods=['GET', 'POST'])
def private_chat(recipient):
    if 'username' not in session:
        return redirect(url_for('login'))

    sender = session['username']
    raw_next = request.args.get('next') or request.form.get('next')
    back_url = resolve_back_url(raw_next, 'private_messages')

    if sender == recipient:
        flash('Cannot send messages to yourself')
        return redirect(back_url)

    # Check if recipient exists
    user_exists = db.get(Uporabnik.username == recipient)
    if not user_exists:
        flash('User not found')
        return redirect(back_url)

    if request.method == 'POST':
        text = request.form.get('message')
        if text:
            private_messages_db.insert({
                'sender': sender,
                'recipient': recipient,
                'text': text,
                'timestamp': datetime.datetime.now().isoformat(),
                'read': False
            })
        return redirect(url_for('private_chat', recipient=recipient, next=back_url))

    # Get messages between sender and recipient (both directions)
    messages = private_messages_db.search(
        ((PrivateMessage.sender == sender) & (PrivateMessage.recipient == recipient)) |
        ((PrivateMessage.sender == recipient) & (PrivateMessage.recipient == sender))
    )
    messages = sorted(messages, key=lambda x: x.get('timestamp', ''))

    # Mark messages from recipient as read
    private_messages_db.update({'read': True}, (PrivateMessage.sender == recipient) & (PrivateMessage.recipient == sender) & (PrivateMessage.read == False))

    return render_template('private_chat.html', messages=messages, recipient=recipient, back_url=back_url)

@app.route('/private_messages')
def private_messages():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Show only users with whom current user already has a private conversation.
    # New chats are started from account page via /private_chat/<recipient>.
    conversation_map = {}
    all_private_messages = private_messages_db.all()
    
    for msg in all_private_messages:
        sender = msg.get('sender')
        recipient = msg.get('recipient')
        
        if sender != username and recipient != username:
            continue

        other_user = recipient if sender == username else sender
        timestamp = msg.get('timestamp', '')
        text = msg.get('text', '')

        if other_user not in conversation_map:
            conversation_map[other_user] = {
                'last_timestamp': timestamp,
                'last_text': text,
                'unread_count': 0
            }
        elif timestamp > conversation_map[other_user]['last_timestamp']:
            conversation_map[other_user]['last_timestamp'] = timestamp
            conversation_map[other_user]['last_text'] = text

        if sender == other_user and recipient == username and not msg.get('read', False):
            conversation_map[other_user]['unread_count'] += 1

    users = []
    for other_username, convo in conversation_map.items():
        other_user = db.get(Uporabnik.username == other_username)
        if not other_user:
            continue

        users.append({
            'username': other_user.get('username', other_username),
            'name': other_user.get('name', ''),
            'surname': other_user.get('surname', ''),
            'profile_picture': other_user.get('profile_picture', ''),
            'unread_count': convo['unread_count'],
            'last_message_text': convo['last_text'],
            'last_timestamp': convo['last_timestamp']
        })

    users.sort(key=lambda u: u.get('last_timestamp', ''), reverse=True)

    # Get user's groups
    my_groups = groups_db.search(Group.members.test(lambda members: username in members))
    
    for group in my_groups:
        unread_count = group_messages_db.count(
            (GroupMessage.group_id == group.doc_id) & 
            (GroupMessage.sender != username)
        )
        group['unread_count'] = unread_count

    return render_template('private_messages.html', users=users, groups=my_groups)

# GROUP CHAT ROUTES

@app.route('/groups')
def groups_list():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Get all groups user is member of
    my_groups = groups_db.search(Group.members.test(lambda members: username in members))
    
    # Get all available groups user is not member of
    all_groups = groups_db.all()
    available_groups = [g for g in all_groups if username not in g.get('members', [])]
    
    for group in my_groups:
        unread_count = group_messages_db.count(
            (GroupMessage.group_id == group.doc_id) & 
            (GroupMessage.sender != username)
        )
        group['unread_count'] = unread_count
    
    return render_template('groups_list.html', my_groups=my_groups, available_groups=available_groups)

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    if request.method == 'POST':
        group_name = request.form.get('group_name')
        selected_members = request.form.getlist('members')
        
        if not group_name:
            flash('Group name is required')
            return redirect(url_for('create_group'))
        
        # Check if group name already exists
        existing_group = groups_db.search(Group.name == group_name)
        if existing_group:
            flash('Group name already exists')
            return redirect(url_for('create_group'))
        
        # Add creator to members
        members = [username] + selected_members
        members = list(set(members))  # Remove duplicates
        
        groups_db.insert({
            'name': group_name,
            'creator': username,
            'members': members,
            'created_at': datetime.datetime.now().isoformat(),
            'description': request.form.get('description', '')
        })
        
        flash(f'Group "{group_name}" created successfully!')
        return redirect(url_for('groups_list'))
    
    # Get all users except current user
    all_users = db.all()
    users = [user for user in all_users if user.get('username') != username]
    
    return render_template('create_group.html', users=users)

@app.route('/group_chat/<int:group_id>', methods=['GET', 'POST'])
def group_chat(group_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    raw_next = request.args.get('next') or request.form.get('next')
    back_url = resolve_back_url(raw_next, 'private_messages')
    group = groups_db.get(doc_id=group_id)
    
    if not group:
        flash('Group not found')
        return redirect(back_url)
    
    # Check if user is member of group
    if username not in group.get('members', []):
        flash('You are not a member of this group')
        return redirect(back_url)
    
    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text:
            group_messages_db.insert({
                'group_id': group_id,
                'sender': username,
                'text': message_text,
                'timestamp': datetime.datetime.now().isoformat()
            })
        return redirect(url_for('group_chat', group_id=group_id, next=back_url))
    
    # Get all messages for this group
    messages = group_messages_db.search(GroupMessage.group_id == group_id)
    messages = sorted(messages, key=lambda x: x.get('timestamp', ''))
    
    # Get member info
    members = []
    for member_name in group.get('members', []):
        member = db.get(Uporabnik.username == member_name)
        if member:
            members.append(member)
    
    return render_template('group_chat.html', group=group, messages=messages, members=members, group_id=group_id, back_url=back_url)

@app.route('/add_members/<int:group_id>', methods=['GET', 'POST'])
def add_members(group_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    group = groups_db.get(doc_id=group_id)
    
    if not group:
        flash('Group not found')
        return redirect(url_for('groups_list'))
    
    # Check if user is creator of group
    if group['creator'] != username:
        flash('Only group creator can add members')
        return redirect(url_for('group_chat', group_id=group_id))
    
    if request.method == 'POST':
        new_members = request.form.getlist('members')
        current_members = group.get('members', [])
        
        for member in new_members:
            if member not in current_members:
                current_members.append(member)
        
        groups_db.update({'members': current_members}, doc_ids=[group_id])
        flash('Members added successfully!')
        return redirect(url_for('group_chat', group_id=group_id))
    
    # Get all users except current members
    all_users = db.all()
    available_users = [u for u in all_users if u.get('username') not in group.get('members', [])]
    
    return render_template('add_members.html', group=group, available_users=available_users, group_id=group_id)

@app.route('/leave_group/<int:group_id>', methods=['POST'])
def leave_group(group_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    group = groups_db.get(doc_id=group_id)
    
    if not group:
        flash('Group not found')
        return redirect(url_for('groups_list'))

    if group.get('creator') == username:
        flash('Group creator cannot leave. Delete the group instead.')
        return redirect(url_for('group_chat', group_id=group_id))
    
    members = group.get('members', [])
    if username in members:
        members.remove(username)
        
        # If no members left, delete group
        if not members:
            groups_db.remove(doc_ids=[group_id])
            flash('Group deleted (no members left)')
        else:
            groups_db.update({'members': members}, doc_ids=[group_id])
            flash('You left the group')
    
    return redirect(url_for('groups_list'))


@app.route('/delete_group/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    group = groups_db.get(doc_id=group_id)

    if not group:
        flash('Group not found')
        return redirect(url_for('groups_list'))

    if group.get('creator') != username:
        flash('Only group creator can delete the group')
        return redirect(url_for('group_chat', group_id=group_id))

    groups_db.remove(doc_ids=[group_id])
    group_messages_db.remove(GroupMessage.group_id == group_id)
    flash('Group deleted successfully')
    return redirect(url_for('groups_list'))
    




        
# JAM SESSIONS
jam_sessions_db = TinyDB('jam_sessions.json')
JamSession = Query()

@app.route('/jam_sessions')
def jam_sessions():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    current_user = db.get(Uporabnik.username == username)
    
    # Get all active jam sessions
    all_sessions = jam_sessions_db.all()
    
    # Calculate distances
    distances = {}
    if current_user and current_user.get('location'):
        coord_me = geocode(current_user['location'])
        if coord_me:
            for session_doc in all_sessions:
                if session_doc.get('location'):
                    coord_session = geocode(session_doc['location'])
                    if coord_session:
                        distances[session_doc.doc_id] = round(haversine_km(coord_me, coord_session))
    
    return render_template('jam_sessions.html', sessions=all_sessions, distances=distances, current_user=current_user)

@app.route('/create_jam_session', methods=['GET', 'POST'])
def create_jam_session():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    current_user = db.get(Uporabnik.username == username)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        date_time = request.form.get('date_time')
        genre = request.form.get('genre')
        instruments_needed = request.form.getlist('instruments_needed')
        max_participants = request.form.get('max_participants', 5)
        
        if not title or not location or not date_time:
            flash('Title, location, and date/time are required')
            return redirect(url_for('create_jam_session'))
        
        jam_sessions_db.insert({
            'creator': username,
            'title': title,
            'description': description,
            'location': location,
            'date_time': date_time,
            'genre': genre,
            'instruments_needed': instruments_needed,
            'max_participants': int(max_participants),
            'participants': [username],
            'created_at': datetime.datetime.now().isoformat()
        })
        
        flash(f'Jam session "{title}" created successfully!')
        return redirect(url_for('jam_sessions'))
    
    return render_template('create_jam_session.html', user=current_user)

@app.route('/join_jam_session/<int:session_id>', methods=['POST'])
def join_jam_session(session_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    jam_session = jam_sessions_db.get(doc_id=session_id)
    
    if not jam_session:
        flash('Jam session not found')
        return redirect(url_for('jam_sessions'))
    
    participants = jam_session.get('participants', [])
    max_participants = jam_session.get('max_participants', 5)
    
    if username in participants:
        flash('You are already a participant in this session')
    elif len(participants) >= max_participants:
        flash('This jam session is full')
    else:
        participants.append(username)
        jam_sessions_db.update({'participants': participants}, doc_ids=[session_id])
        flash(f'Successfully joined "{jam_session.get("title")}"!')
    
    return redirect(url_for('jam_sessions'))

@app.route('/leave_jam_session/<int:session_id>', methods=['POST'])
def leave_jam_session(session_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    jam_session = jam_sessions_db.get(doc_id=session_id)
    
    if not jam_session:
        flash('Jam session not found')
        return redirect(url_for('jam_sessions'))
    
    participants = jam_session.get('participants', [])
    
    if username not in participants:
        flash('You are not a participant in this session')
    elif username == jam_session.get('creator'):
        flash('Creator cannot leave the session')
    else:
        participants.remove(username)
        jam_sessions_db.update({'participants': participants}, doc_ids=[session_id])
        flash(f'You left the jam session')
    
    return redirect(url_for('jam_sessions'))


@app.route('/delete_jam_session/<int:session_id>', methods=['POST'])
def delete_jam_session(session_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    jam_session = jam_sessions_db.get(doc_id=session_id)

    if not jam_session:
        flash('Jam session not found')
        return redirect(url_for('jam_sessions'))

    if jam_session.get('creator') != username:
        flash('Only host can delete this session')
        return redirect(url_for('jam_sessions'))

    jam_sessions_db.remove(doc_ids=[session_id])
    flash('Jam session deleted')
    return redirect(url_for('jam_sessions'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)