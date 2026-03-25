from flask import Flask, render_template, request, redirect, url_for, flash, session
from tinydb import TinyDB, Query
import bcrypt, re
import requests
import datetime
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

#pogledas profil
@app.route('/account/<username>')
def view_account(username):
    user = db.get(Uporabnik.username == username)
    if not user:
        return redirect(url_for('home'))
    user_events = events_db.search(Event.username == username)
    return render_template('account.html', user=user, events=user_events)


        

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

    return render_template('find_people.html', results=results, users=users, vnos=vnos, instrument=instrument, location=location, genre=genre, experience=experience)

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

    if sender == recipient:
        flash('Cannot send messages to yourself')
        return redirect(url_for('private_messages'))

    # Check if recipient exists
    user_exists = db.get(Uporabnik.username == recipient)
    if not user_exists:
        flash('User not found')
        return redirect(url_for('private_messages'))

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
        return redirect(url_for('private_chat', recipient=recipient))

    # Get messages between sender and recipient (both directions)
    messages = private_messages_db.search(
        ((PrivateMessage.sender == sender) & (PrivateMessage.recipient == recipient)) |
        ((PrivateMessage.sender == recipient) & (PrivateMessage.recipient == sender))
    )
    messages = sorted(messages, key=lambda x: x.get('timestamp', ''))

    # Mark messages from recipient as read
    private_messages_db.update({'read': True}, (PrivateMessage.sender == recipient) & (PrivateMessage.recipient == sender) & (PrivateMessage.read == False))

    return render_template('private_chat.html', messages=messages, recipient=recipient)

@app.route('/private_messages')
def private_messages():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Get all users except current user
    all_users = db.all()
    users = [user for user in all_users if user.get('username') != username]

    # Check for unread messages for each user
    for user in users:
        unread_count = private_messages_db.count(
            (PrivateMessage.sender == user['username']) & 
            (PrivateMessage.recipient == username) & 
            (PrivateMessage.read == False)
        )
        user['unread_count'] = unread_count

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
    group = groups_db.get(doc_id=group_id)
    
    if not group:
        flash('Group not found')
        return redirect(url_for('groups_list'))
    
    # Check if user is member of group
    if username not in group.get('members', []):
        flash('You are not a member of this group')
        return redirect(url_for('groups_list'))
    
    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text:
            group_messages_db.insert({
                'group_id': group_id,
                'sender': username,
                'text': message_text,
                'timestamp': datetime.datetime.now().isoformat()
            })
        return redirect(url_for('group_chat', group_id=group_id))
    
    # Get all messages for this group
    messages = group_messages_db.search(GroupMessage.group_id == group_id)
    messages = sorted(messages, key=lambda x: x.get('timestamp', ''))
    
    # Get member info
    members = []
    for member_name in group.get('members', []):
        member = db.get(Uporabnik.username == member_name)
        if member:
            members.append(member)
    
    return render_template('group_chat.html', group=group, messages=messages, members=members, group_id=group_id)

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
    




        
if __name__ == '__main__':
    app.run(debug=True, port=5000)