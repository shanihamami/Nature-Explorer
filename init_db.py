import sqlite3
import json

connection = sqlite3.connect('trails.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

data = [
    ('גבעת העיזים', 'וואדי עמירם', 'Short description amiram wadi', [32.8089, 34.9940],
     'End point example', '4', 'בינוני', 'סתיו', 'נקודות עניין בוואדי עמירם',
     'Interactive activity example', 'שעה-שעתיים', 0, 1, 1, 1, 1),

    ('ואדי עובדיה', 'שביל הטראסות', 'Short description the terasot path', [32.8051, 34.9965],
     'End point example', '5', 'קשה', 'אביב', 'נקודות עניין בשביל הטראסות',
     'Interactive activity example', '2 hours+', 1, 1, 0, 0, 1),

    ('נחל סעדיה', 'הגשר התורכי', 'Short description the turkish bridge', [32.8000, 34.9870],
     'End point example', '3.5', 'קל', 'קיץ', 'נקודות עניין בגשר התורכי',
     'Interactive activity example', '1.5 hours', 0, 1, 1, 0, 1),

    ('שבילי יער רמת אלון', 'ואדי בן דור' , 'Short description ben-dor wadi', [32.8086, 34.9935],
     'End point example', '2.5', 'בינוני', 'קיץ', 'נקודות עניין בואדי בן דור',
     'Interactive activity example', 'שעה-שעתיים', 1, 1, 0, 1, 1),

    ('שבילי יער רמת אלון', 'ואדי שנק', 'Short description shanke wadi', [32.8066, 34.98961],
     'End point example', '5', 'בינוני', 'קיץ', 'נקודות עניין בואדי שנק',
     'Interactive activity example', 'שעה-שעתיים', 1, 1, 0, 1, 1),

    ('גבעת העיזים', 'המחצבה', 'Short description the quarry', [32.8010, 34.9925],
     'End point example', '4.5', 'קל', 'חורף', 'נקודות עניין במחצבה',
     'Interactive activity example', '2 hours+', 0, 1, 1, 0, 1)
]

for trail in data:
    trail = list(trail)  # Convert tuple to list to allow modifications
    trail[3] = json.dumps(trail[3])  # Convert the start_point list to JSON string
    cur.execute("""
    INSERT INTO trails
    (main_location, trail_name, short_description, start_point, end_point, lengthKM, difficulty, season,
    point_of_interest, interactive_activity, duration, possibility_of_entering_water,
    suitable_for_families, suitable_for_bicycles, circular, suitable_for_disabled)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trail)

connection.commit()
connection.close()

# Initialize registration database
connection_reg = sqlite3.connect('registration.db')
with open('schema.sql') as f:
    connection_reg.executescript(f.read())
connection_reg.close()

connection_messages = sqlite3.connect('messages.db')
with open('schema.sql') as f:
    connection_messages.executescript(f.read())
connection_messages.close()

