from flask import Flask, request, render_template, g, jsonify, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'nature_explorer'
ADMIN_PASSWORD = 'password'

DATABASE_TRIALS = 'trails.db'
DATABASE_REGISTRATION = 'registration.db'
DATABASE_MESSAGES = 'messages.db'

# Function to get database connection
def get_db_trails():
    if 'db_trails' not in g:
        g.db_trails = sqlite3.connect(DATABASE_TRIALS)
        g.db_trails.row_factory = sqlite3.Row
    return g.db_trails

def get_db_registration():
    if 'db_registration' not in g:
        g.db_registration = sqlite3.connect(DATABASE_REGISTRATION)
        g.db_registration.row_factory = sqlite3.Row
    return g.db_registration

def get_db_messages():
    if 'db_messages' not in g:
        g.db_messages = sqlite3.connect(DATABASE_MESSAGES)
    return g.db_messages

# Close database connection at the end of request
@app.teardown_appcontext
def close_db(exception):
    db_trails = g.pop('db_trails', None)
    db_registration = g.pop('db_registration', None)
    db_messages = g.pop('db_messages', None)
    if db_trails is not None:
        db_trails.close()
    if db_registration is not None:
        db_registration.close()
    if db_messages is not None:
        db_messages.close()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        query = """
        INSERT INTO messages (fullname, email, phone, message) VALUES (?, ?, ?, ?)
        """
        params = (fullname, email, phone, message)

        try:
            db = get_db_messages()
            db.execute(query, params)
            db.commit()
            flash("ההודעה שלך נשלחה בהצלחה!", "success")
            return redirect(url_for('contact'))
        except sqlite3.Error as e:
            print("SQLite error:", e)
            flash("אירעה שגיאה בעת שליחת ההודעה. אנא נסה שנית.", "danger")
            return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/maps')
def the_map():
    return render_template('the_map.html')

@app.route('/recommendations')
def recommendations():
    return render_template('recommendations.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/about')
def about():
    return render_template('about.html')

# New route to fetch trail data
@app.route('/api/trails', methods=['GET'])
def get_trails():
    db = get_db_trails()
    cur = db.execute('SELECT * FROM trails')
    trails = cur.fetchall()
    return jsonify([dict(trail) for trail in trails])

# Route for search page (search.html and search_results.html)
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        area = request.form.get('area')
        duration = request.form.get('duration')
        season = request.form.get('season')
        family = 'family' in request.form
        bicycles = 'bicycles' in request.form
        water = 'water' in request.form

        query = """
        SELECT * FROM trails 
        WHERE main_location=? AND duration=? AND season=? 
        """
        params = (area, duration, season)
        db = get_db_trails()
        results = db.execute(query, params).fetchall()
        return render_template('search_results.html', results=results)
    else:
        return render_template('search.html')

@app.route('/search_results')
def search_results():
    return render_template('search_results.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        id_card = request.form['id_card']
        phone_number = request.form['phone_number']
        number_of_participants = request.form['number_of_participants']
        tour = request.form['tour']
        comments = request.form['comments']

        query = """
        INSERT INTO participants (full_name, id_card, phone_number, number_of_participants, tour, comments)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (full_name, id_card, phone_number, number_of_participants, tour, comments)

        try:
            db = get_db_registration()
            db.execute(query, params)
            db.commit()
            return redirect(url_for('registration_success'))
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return f"An error occurred while inserting data: {e}"

    return render_template('registration.html')

@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db_trails = get_db_trails()
    db_registration = get_db_registration()
    db_messages = get_db_messages()

    cursor_trails = db_trails.cursor()
    cursor_trails.execute("SELECT id, main_location, trail_name FROM trails LIMIT 5")
    trails = cursor_trails.fetchall()

    cursor_reg = db_registration.cursor()
    cursor_reg.execute("SELECT id, full_name, phone_number FROM participants LIMIT 5")
    registrations = cursor_reg.fetchall()

    cursor_msgs = db_messages.cursor()
    cursor_msgs.execute("SELECT id, fullname, message FROM messages LIMIT 5")
    messages = cursor_msgs.fetchall()

    return render_template('admin_dashboard.html', trails=trails, registrations=registrations, messages=messages)

@app.route('/manage_trails')
def manage_trails():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db_trails()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    trails = db.execute(
        'SELECT * FROM trails LIMIT ? OFFSET ?', (per_page, offset)
    ).fetchall()
    total_trails = db.execute('SELECT COUNT(*) FROM trails').fetchone()[0]
    has_next = total_trails > page * per_page

    return render_template('manage_trails.html', trails=trails, page=page, has_next=has_next)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Incorrect password. Please try again.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/view-registrations')
def view_registrations():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db_registration()
    cur = db.execute('SELECT * FROM registrations')  # Adjust the query as needed
    registrations = cur.fetchall()
    return render_template('view_registrations.html', registrations=registrations)

@app.route('/view-messages')
def view_messages():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db_messages()
    cur = db.execute('SELECT id, fullname, email, phone, message FROM messages')
    messages = cur.fetchall()
    return render_template('view_messages.html', messages=messages)

@app.route('/add_trail', methods=['GET', 'POST'])
def add_trail():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        main_location = request.form['main_location']
        trail_name = request.form['trail_name']
        short_description = request.form['short_description']
        start_point = request.form['start_point']
        end_point = request.form['end_point']
        lengthKM = request.form['lengthKM']
        difficulty = request.form['difficulty']
        season = request.form['season']
        point_of_interest = request.form['point_of_interest']
        interactive_activity = request.form['interactive_activity']
        duration = request.form['duration']
        possibility_of_entering_water = 1 if 'possibility_of_entering_water' in request.form else 0
        suitable_for_families = 1 if 'suitable_for_families' in request.form else 0
        suitable_for_bicycles = 1 if 'suitable_for_bicycles' in request.form else 0
        circular = 1 if 'circular' in request.form else 0

        query = """
        INSERT INTO trails (main_location, trail_name, short_description, start_point, end_point, lengthKM, difficulty, season, point_of_interest, interactive_activity, duration, possibility_of_entering_water, suitable_for_families, suitable_for_bicycles, circular)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (main_location, trail_name, short_description, start_point, end_point, lengthKM, difficulty, season, point_of_interest, interactive_activity, duration, possibility_of_entering_water, suitable_for_families, suitable_for_bicycles, circular)

        try:
            db = get_db_trails()
            db.execute(query, params)
            db.commit()
            return redirect(url_for('manage_trails'))
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return f"An error occurred while inserting data: {e}"
    return render_template('add_trail.html')

@app.route('/edit_trail/<int:trail_id>', methods=['GET', 'POST'])
def edit_trail(trail_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db_trails()
    if request.method == 'POST':
        main_location = request.form['main_location']
        trail_name = request.form['trail_name']
        short_description = request.form['short_description']
        start_point = request.form['start_point']
        end_point = request.form['end_point']
        lengthKM = request.form['lengthKM']
        difficulty = request.form['difficulty']
        season = request.form['season']
        point_of_interest = request.form['point_of_interest']
        interactive_activity = request.form['interactive_activity']
        duration = request.form['duration']
        possibility_of_entering_water = 1 if 'possibility_of_entering_water' in request.form else 0
        suitable_for_families = 1 if 'suitable_for_families' in request.form else 0
        suitable_for_bicycles = 1 if 'suitable_for_bicycles' in request.form else 0
        circular = 1 if 'circular' in request.form else 0

        query = """
        UPDATE trails
        SET main_location = ?, trail_name = ?, short_description = ?, start_point = ?, end_point = ?, lengthKM = ?, difficulty = ?, season = ?, point_of_interest = ?, interactive_activity = ?, duration = ?, possibility_of_entering_water = ?, suitable_for_families = ?, suitable_for_bicycles = ?, circular = ?
        WHERE id = ?
        """
        params = (main_location, trail_name, short_description, start_point, end_point, lengthKM, difficulty, season, point_of_interest, interactive_activity, duration, possibility_of_entering_water, suitable_for_families, suitable_for_bicycles, circular, trail_id)

        try:
            db.execute(query, params)
            db.commit()
            return redirect(url_for('manage_trails'))
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return f"An error occurred while updating data: {e}"

    trail = db.execute('SELECT * FROM trails WHERE id = ?', (trail_id,)).fetchone()
    return render_template('edit_trail.html', trail=trail)

@app.route('/delete_trail/<int:trail_id>', methods=['POST'])
def delete_trail(trail_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db_trails()
    try:
        db.execute('DELETE FROM trails WHERE id = ?', (trail_id,))
        db.commit()
        return redirect(url_for('manage_trails'))
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return f"An error occurred while deleting data: {e}"

if __name__ == '__main__':
    app.run(debug=True)
