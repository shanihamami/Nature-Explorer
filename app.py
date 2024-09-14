from flask import Flask, request, render_template, g, jsonify, redirect, url_for, flash, session
from datetime import datetime
import sqlite3
import urllib.parse

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
    db = get_db_trails()
    tours_query = "SELECT * FROM organized_tours"
    tours = db.execute(tours_query).fetchall()
    tours = [dict(row) for row in tours]
    return render_template('the_map.html', tours=tours)

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
    if request.method == 'POST' or request.args:
        # קבלת נתונים מהטופס או מה-URL (GET)
        areas = request.form.getlist('areas[]') if request.method == 'POST' else request.args.getlist('areas')
        durations = request.form.getlist('durations[]') if request.method == 'POST' else request.args.getlist('durations')
        seasons = request.form.getlist('seasons[]') if request.method == 'POST' else request.args.getlist('seasons')
        difficulties = request.form.getlist('difficulty[]') if request.method == 'POST' else request.args.getlist('difficulties')

        # משתנים בינאריים
        suitable_for_families = 'family' in request.form if request.method == 'POST' else 'family' in request.args
        possibility_of_entering_water = 'water' in request.form if request.method == 'POST' else 'water' in request.args
        suitable_for_bicycles = 'bicycles' in request.form if request.method == 'POST' else 'bicycles' in request.args
        suitable_for_disabled = 'disabled' in request.form if request.method == 'POST' else 'disabled' in request.args

        # תנאים לבניית השאילתה
        conditions = []
        params = []

        # תנאים לפי אזור
        if areas:
            conditions.append("main_location IN ({})".format(','.join('?' * len(areas))))
            params.extend(areas)
        # תנאים לפי אורך מסלול
        if durations:
            conditions.append("duration IN ({})".format(','.join('?' * len(durations))))
            params.extend(durations)
        # תנאים לפי עונה
        if seasons:
            conditions.append("season IN ({})".format(','.join('?' * len(seasons))))
            params.extend(seasons)
        # תנאים לפי רמת קושי
        if difficulties:
            conditions.append("difficulty IN ({})".format(','.join('?' * len(difficulties))))
            params.extend(difficulties)

        # תנאים לפי משתנים בינאריים
        if suitable_for_families:
            conditions.append("suitable_for_families = 1")
        if possibility_of_entering_water:
            conditions.append("possibility_of_entering_water = 1")
        if suitable_for_bicycles:
            conditions.append("suitable_for_bicycles = 1")
        if suitable_for_disabled:
            conditions.append("suitable_for_disabled = 1")

        # בניית השאילתה
        query = "SELECT * FROM trails"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        db = get_db_trails()
        results = db.execute(query, params).fetchall()

        # שליפת סיורים עתידיים
        today = datetime.now().strftime('%Y-%m-%d')
        future_tours_query = """
            SELECT organized_tours.trail_name as trail_name, organized_tours.date, organized_tours.title
            FROM organized_tours
            WHERE (substr(organized_tours.date, 7, 4) || '-' || substr(organized_tours.date, 4, 2) || '-' || substr(organized_tours.date, 1, 2)) >= ?
        """
        future_tours = db.execute(future_tours_query, (today,)).fetchall()

        # ארגון סיורים עתידיים לפי שם מסלול
        future_tours_dict = {}
        for tour in future_tours:
            trail_name = tour['trail_name']
            if trail_name not in future_tours_dict:
                future_tours_dict[trail_name] = []
            future_tours_dict[trail_name].append({
                'date': tour['date'],
                'title': tour['title']
            })

        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 10

        # חישוב מספר הרשומות הכולל
        total_results = len(results)
        total_pages = (total_results + per_page - 1) // per_page

        # חישוב את הרשומות של העמוד הנוכחי
        start = (page - 1) * per_page
        end = start + per_page
        results_to_display = results[start:end]

        has_prev = page > 1
        has_next = page < total_pages

        return render_template(
            'search_results.html',
            results=results_to_display,
            future_tours=future_tours_dict,
            page=page,
            has_prev=has_prev,
            has_next=has_next,
            areas=areas, durations=durations, seasons=seasons, difficulties=difficulties,
            family=suitable_for_families, water=possibility_of_entering_water, bicycles=suitable_for_bicycles, disabled=suitable_for_disabled
        )
    else:
        return render_template('search.html')




@app.route('/search_results')
def search_results():
    return render_template('search_results.html')

@app.route('/register/<tour_title>', methods=['POST', 'GET'])
def register(tour_title):
    tour_title = urllib.parse.unquote(tour_title)
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        number_of_participants = request.form['number_of_participants']
        comments = request.form['comments']

        query = """
        INSERT INTO participants (full_name,  phone_number, number_of_participants, tour, comments)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (full_name, phone_number, number_of_participants, tour_title, comments)

        try:
            db = get_db_registration()
            db.execute(query, params)
            db.commit()
            return redirect(url_for('registration_success'))
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return f"An error occurred while inserting data: {e}"

    # התחברות ל-Database
    conn = sqlite3.connect('trails.db')
    cur = conn.cursor()

    # שליפת פרטי הסיור על פי שם הסיור
    cur.execute("""
    SELECT organized_tours.title, trails.trail_name, organized_tours.date, organized_tours.time, organized_tours.description
    FROM organized_tours
    JOIN trails ON organized_tours.trail_name = trails.trail_name
    WHERE organized_tours.title = ?
    """, (tour_title,))

    tour_details = cur.fetchone()
    conn.close()

    if tour_details:
        return render_template('registration.html', tour=tour_details)
    else:
        return "לא נמצא סיור עם השם הזה"

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

    cursor_reg = db_trails.cursor()
    cursor_reg.execute("SELECT * FROM organized_tours LIMIT 5")
    tours = cursor_reg.fetchall()

    cursor_msgs = db_messages.cursor()
    cursor_msgs.execute("SELECT id, fullname, message FROM messages LIMIT 5")
    messages = cursor_msgs.fetchall()

    return render_template('admin_dashboard.html', trails=trails, tours=tours, messages=messages)

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
    cur = db.execute('SELECT * FROM participants')  # Adjust the query as needed
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
        suitable_for_disabled = 1 if 'suitable_for_disabled' in request.form else 0

        query = """
        INSERT INTO trails (main_location, trail_name, short_description, start_point, end_point, lengthKM, difficulty, season, point_of_interest, interactive_activity, duration, possibility_of_entering_water, suitable_for_families, suitable_for_bicycles, circular, suitable_for_disabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (main_location, trail_name, short_description, start_point, end_point, lengthKM, difficulty, season, point_of_interest, interactive_activity, duration, possibility_of_entering_water, suitable_for_families, suitable_for_bicycles, circular, suitable_for_disabled)

        try:
            db = get_db_trails()
            db.execute(query, params)
            db.commit()
            flash('השביל נוסף בהצלחה!')
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
        suitable_for_disabled = 1 if 'suitable_for_disabled' in request.form else 0

        query = """
        UPDATE trails
        SET main_location = ?, trail_name = ?, short_description = ?, start_point = ?, end_point = ?, lengthKM = ?, difficulty = ?, season = ?, point_of_interest = ?, interactive_activity = ?, duration = ?, possibility_of_entering_water = ?, suitable_for_families = ?, suitable_for_bicycles = ?, circular = ?, suitable_for_disabled = ?
        WHERE id = ?
        """
        params = (main_location, trail_name, short_description, start_point, end_point, lengthKM, difficulty, season, point_of_interest, interactive_activity, duration, possibility_of_entering_water, suitable_for_families, suitable_for_bicycles, circular, suitable_for_disabled, trail_id)

        try:
            db.execute(query, params)
            db.commit()
            flash('פרטי השביל עודכנו בהצלחה!')
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
        flash('השביל נמחק בהצלחה!')
        return redirect(url_for('manage_trails'))
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return f"An error occurred while deleting data: {e}"




@app.route('/add_tour', methods=['GET', 'POST'])
def add_tour():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        trail_name = request.form['trail_name']

        # התאריך יגיע כבר בפורמט yyyy-mm-dd
        date = request.form['date']

        # המרת התאריך לפורמט dd/mm/yyyy
        try:
            date_parts = date.split('-')
            year = date_parts[0]
            month = date_parts[1]
            day = date_parts[2]
            formatted_date = f"{day}/{month}/{year}"
        except IndexError:
            formatted_date = ""  # ניהול מצב בו התאריך לא קיים או לא בפורמט הצפוי

        # המרת השעה לפורמט hh:mm
        hour = request.form['hour']
        minute = request.form['minute']
        time = f"{hour}:{minute}"

        description = request.form['description']

        query = """
        INSERT INTO organized_tours (title, trail_name, date, time, description)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (title, trail_name, formatted_date, time, description)

        try:
            db = get_db_trails()
            db.execute(query, params)
            db.commit()
            flash('הסיור נוסף בהצלחה!')
            return redirect(url_for('view_registrations'))
        except sqlite3.Error as e:
            print("SQLite error:", e)
            return f"An error occurred while inserting data: {e}"

    db_trails = get_db_trails()
    cursor_trails = db_trails.cursor()
    cursor_trails.execute("SELECT trail_name FROM trails")
    trails = [row[0] for row in cursor_trails.fetchall()]
    return render_template('add_tour.html', trails=trails)



# פונקציה לשליפת נתוני סיור מתוך מסד הנתונים לפי מזהה (id)
def get_tour(tour_id):
    conn = sqlite3.connect('trails.db')
    conn.row_factory = sqlite3.Row  # תוצאה כמילון
    cursor = conn.cursor()

    # שליפת הסיור לפי ID
    cursor.execute("SELECT * FROM organized_tours WHERE id = ?", (tour_id,))
    tour = cursor.fetchone()
    conn.close()

    return tour


# פונקציה לעדכון סיור
@app.route('/edit_tour/<int:tour_id>', methods=['GET', 'POST'])
def edit_tour(tour_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('trails.db')
    cursor = conn.cursor()

    # שלב ראשון - שליפת כל המסלולים כדי להציג אותם בבחירת המסלול
    cursor.execute("SELECT trail_name FROM trails")
    trails = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        # שלב שני - קבלת הנתונים מהטופס
        title = request.form['title']
        trail_name = request.form['trail_name']
        # התאריך יגיע כבר בפורמט yyyy-mm-dd
        date = request.form['date']

        # המרת התאריך לפורמט dd/mm/yyyy
        try:
            date_parts = date.split('-')
            year = date_parts[0]
            month = date_parts[1]
            day = date_parts[2]
            formatted_date = f"{day}/{month}/{year}"
        except IndexError:
            formatted_date = ""  # ניהול מצב בו התאריך לא קיים או לא בפורמט הצפוי

        # המרת השעה לפורמט hh:mm
        hour = request.form['hour']
        minute = request.form['minute']
        time = f"{hour}:{minute}"
        description = request.form['description']

        # שלב שלישי - עדכון הסיור ב-Database
        cursor.execute("""
            UPDATE organized_tours
            SET title = ?, trail_name = ?, date = ?, time = ?, description = ?
            WHERE id = ?
        """, (title, trail_name, formatted_date, time, description, tour_id))

        conn.commit()
        conn.close()

        flash('הסיור עודכן בהצלחה!')
        return redirect(url_for('view_registrations'))

    else:
        # שלב רביעי - שליפת הסיור לפי ID והצגת הטופס עם הנתונים הקיימים
        tour = get_tour(tour_id)
        conn.close()

        if tour is None:
            flash('סיור לא נמצא!')
            return redirect(url_for('home'))

        return render_template('edit_tour.html', tour=tour, trails=trails)

@app.route('/delete_tour/<int:tour_id>', methods=['POST'])
def delete_tour(tour_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db_trails()
    try:
        db.execute('DELETE FROM organized_tours WHERE id = ?', (tour_id,))
        db.commit()
        flash('הסיור נמחק בהצלחה!')
        return redirect(url_for('view_registrations'))
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return f"An error occurred while deleting data: {e}"



@app.route('/guided_tours')
def guided_tours():
    conn = sqlite3.connect('trails.db')
    cur = conn.cursor()

    # שליפת סיורים עתידיים מהטבלה
    cur.execute("""
        SELECT organized_tours.title, trails.trail_name, organized_tours.date, organized_tours.time, organized_tours.description
        FROM organized_tours
        JOIN trails ON organized_tours.trail_name = trails.trail_name
        WHERE (substr(organized_tours.date, 7, 4) || '-' || substr(organized_tours.date, 4, 2) || '-' || substr(organized_tours.date, 1, 2)) >= ?
        ORDER BY (substr(organized_tours.date, 7, 4) || '-' || substr(organized_tours.date, 4, 2) || '-' || substr(organized_tours.date, 1, 2)) ASC
        """, (datetime.now().strftime('%Y-%m-%d'),))

    tours = cur.fetchall()

    page = request.args.get('page', 1, type=int)
    per_page = 10

    # חישוב מספר הרשומות הכולל
    total_tours = len(tours)

    # חישוב מספר העמודים
    total_pages = (total_tours + per_page - 1) // per_page

    # חישוב את הרשומות של העמוד הנוכחי
    start = (page - 1) * per_page
    end = start + per_page
    tours_to_display = tours[start:end]

    has_prev = page > 1
    has_next = page < total_pages

    conn.close()

    return render_template('guided_tours.html', tours=tours_to_display, page=page, has_prev=has_prev, has_next=has_next)


@app.route('/api/tours', methods=['GET'])
def api_tours():
    db = get_db_trails()

    # שליפת סיורים
    tours_query = "SELECT * FROM organized_tours ORDER BY SUBSTR(date, 7, 4) || '-' || SUBSTR(date, 4, 2) || '-' || SUBSTR(date, 1, 2) "
    tours = db.execute(tours_query).fetchall()

    # ארגון סיורים עם נרשמים
    tours_list = []
    db = get_db_registration()
    for tour in tours:
        # השתמש בעמודה הנכונה שנקראת 'tour'
        participants_query = "SELECT * FROM participants WHERE tour = ?"
        participants = db.execute(participants_query, (tour['title'],)).fetchall()

        tours_list.append({
            'id': tour['id'],
            'title': tour['title'],
            'trail_name': tour['trail_name'],
            'date': tour['date'],
            'time': tour['time'],
            'description': tour['description'],
            'participants': [dict(participant) for participant in participants]
        })

    return jsonify(tours_list)

@app.route('/view-participants')
def view_participants():
    # מקבל את שם הסיור מהפרמטרים של ה-URL
    tour_title = request.args.get('tour')
    return render_template('view_participants.html', tour_title=tour_title)


@app.route('/api/participants')
def api_participants():
    # מקבל את שם הסיור מהפרמטרים של ה-URL
    tour_title = request.args.get('tour')

    # דוגמה לשליפה ממסד נתונים
    db = get_db_registration()
    participants_query = "SELECT * FROM participants WHERE tour = ?"
    participants = db.execute(participants_query, (tour_title,)).fetchall()

    # הפיכת הרשומה לאובייקט JSON כדי להחזיר ללקוח
    participants_list = []
    for participant in participants:
        participants_list.append({
            "full_name": participant["full_name"],
            "phone_number": participant["phone_number"],
            "number_of_participants": participant["number_of_participants"],
            "comments": participant["comments"]
        })

    return jsonify(participants_list)

def get_latest_news():
    # חיבור ל-Database
    conn = sqlite3.connect('registration.db')
    cursor = conn.cursor()

    # שאילתא לשליפת 5 העדכונים האחרונים
    cursor.execute('''
        SELECT title
        FROM news
        ORDER BY publish_date DESC
        LIMIT 5
    ''')
    latest_news = cursor.fetchall()

    # סגירת החיבור
    conn.close()

    return [item[0] for item in latest_news]  # החזרת רשימת הכותרות

# יצירת ה-API שמחזיר את העדכונים ב-JSON
@app.route('/api/news', methods=['GET'])
def api_get_news():
    news_titles = get_latest_news()
    return jsonify(news_titles)  # החזרת הנתונים כ-JSON


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

