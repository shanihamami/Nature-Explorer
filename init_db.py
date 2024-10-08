import sqlite3
import json

connection = sqlite3.connect('trails.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

data = [
    ('גבעת העיזים', 'וואדי עמירם', 'וואדי עמירם מציע מסלול הליכה בטבע הפראי של חיפה עם נוף מרהיב לים התיכון',
     [32.8089, 34.9940], 'End point example', '4', 'בינוני', 'סתיו', 'נקודת תצפית על חיפה',
     'נקודת תצפית על חיפה', 'שעה-שעתיים', 0, 1, 1, 1, 1),

    ('ואדי עובדיה', 'שביל הטראסות', 'שביל הטראסות משלב הליכה בטרסות עתיקות עם נוף עוצר נשימה של הכרמל',
     [32.8051, 34.9965], 'End point example', '5', 'קשה', 'אביב', 'נוף מרהיב',
     'נוף מרהיב', 'שעתיים+', 1, 1, 0, 0, 1),

    ('נחל סעדיה', 'הגשר התורכי', 'מסלול הגשר התורכי עובר בין גשרי אבן היסטוריים מעל נחל סעדיה',
     [32.8000, 34.9870], 'End point example', '3.5', 'קל', 'קיץ', 'מסלול הליכה לצד אתרים היסטוריים',
     'מסלול הליכה לצד אתרים היסטוריים', 'שעה-שעתיים', 0, 1, 1, 0, 1),

    ('שבילי יער רמת אלון', 'ואדי בן דור' , 'ואדי בן דור מציע שביל הליכה דרך חורש טבעי בנוף הכרמל הצפוני',
     [32.8086, 34.9935], 'End point example', '2.5', 'בינוני', 'קיץ', 'שבילי הליכה הרריים',
     'שביל הליכה הררי', 'שעה-שעתיים', 1, 1, 0, 1, 1),

    ('שבילי יער רמת אלון', 'ואדי שנק', 'מסלול ואדי שנק עובר בין חורשות ובוסתנים, ומציע נוף יפה של חיפה',
     [32.8066, 34.98961], 'End point example', '5', 'בינוני', 'קיץ', 'טיול לאורך הואדי',
     'טיול לאורך הואדי', 'שעה-שעתיים', 1, 1, 0, 1, 1),

    ('גבעת העיזים', 'המחצבה', 'מסלול המחצבה מוביל אל אתר מחצבה עתיק בכרמל עם נקודות עניין גיאולוגיות',
     [32.8010, 34.9925], 'End point example', '4.5', 'קל', 'חורף', 'אתרים ארכיאולוגיים מעניינים',
     'נקודות עניין גיאולוגיות', 'שעתיים+', 0, 1, 1, 0, 1),

    ('שבילי יער רמת אלון', 'שביל סובב סביוני דניה', 'שביל סובב שכונת סביוני דניה, עם נוף לים ולכרמל',
     [32.8060, 34.9880], 'נקודת סיום דניה', '3', 'קל', 'אביב', 'נוף מרהיב לים',
     'שביל הליכה מעגלי', 'חצי שעה-שעה', 0, 1, 0, 1, 1),

    ('שבילי יער רמת אלון', 'שביל התצפית', 'שביל תצפית מרהיבה על נוף העיר חיפה והים התיכון',
     [32.7930, 34.9730], 'נקודת סיום טיילת לואי', '1.5', 'קל', 'סתיו', 'תצפיות נוף ייחודיות',
     'צילום והסתכלות בנוף', 'חצי שעה-שעה', 0, 1, 1, 0, 1),

    ('שבילי יער רמת אלון', 'שביל העץ הקסום והחיבור לפארק הגשרים התלויים', 'שביל המשלב הליכה בפארק הכרמל עם גשרים תלויים',
     [32.7910, 34.9800], 'פארק הגשרים התלויים', '2', 'בינוני', 'חורף', 'גשרי התלייה',
     'גשרי תלייה', 'שעה-שעתיים', 0, 1, 1, 1, 1),

    ('ואדי לטם', 'גן האם', 'טיול נעים בתוך גן האם המפורסם בלב הכרמל',
     [32.7945, 34.9890], 'נקודת סיום גן האם', '1', 'קל', 'קיץ', 'שבילי הליכה',
     'שבילי הליכה בגנים', 'חצי שעה-שעה', 0, 1, 1, 1, 1),

    ('ואדי לטם', 'נחל לטם', 'שביל ייחודי עם נוף טבעי ונחל שזורם בעונות מסוימות',
     [32.8040, 34.9925], 'סיום בחיבור לוואדי בן דור', '4', 'בינוני', 'אביב', 'תצפית בסיום הנחל',
     'טיול לאורך נחל זורם', 'שעה-שעתיים', 1, 1, 0, 0, 1),

    ('ואדי לטם', 'גן אופירה נבון', 'שביל בתוך גן עירוני יפהפה עם צמחייה מגוונת',
     [32.8090, 34.9945], 'סיום בגן אופירה נבון', '1', 'קל', 'אביב', 'תצפית וגן שעשועים',
     'שבילי הליכה וגן שעשועים', 'חצי שעה-שעה', 0, 1, 1, 1, 1),

    ('גבעת העיזים', 'המערות', 'מסלול ייחודי המוביל אל מערות טבעיות בכרמל',
     [32.8000, 34.9920], 'סיום במערות', '3', 'בינוני', 'קיץ', 'נוף מרהיב',
     'חקירת המערות', 'שעתיים+', 0, 1, 0, 1, 1),

    ('גבעת העיזים', 'שביל עמירם', 'שביל המוביל לנקודת תצפית מרהיבה על חיפה',
     [32.8080, 34.9940], 'סיום בנקודת תצפית', '2.5', 'קל', 'סתיו', 'נקודת תצפית ייחודית',
     'תצפית על נוף חיפה', 'חצי שעה-שעה', 0, 1, 1, 1, 1),

    ('ואדי עובדיה', 'מערת עובדיה', 'מסלול המוביל אל מערת עובדיה, עם תצפיות על הטבע',
     [32.8050, 34.9950], 'סיום במערת עובדיה', '4', 'בינוני', 'חורף', 'נקודת תצפית',
     'חקירת המערות והטבע', 'שעה-שעתיים', 0, 1, 0, 0, 1),

    ('נחל סעדיה', 'המעיינות', 'שביל ייחודי הכולל מעיינות קטנים לאורך הדרך',
     [32.7990, 34.9860], 'סיום במעיין המרכזי', '3.5', 'קל', 'אביב', 'טיול לאורך הנחל',
     'טיול לאורך הנחל והמעיינות', 'שעה-שעתיים', 1, 1, 1, 1, 1)
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

# Example for adding organized tours data:
connection = sqlite3.connect('trails.db')
cur = connection.cursor()

organized_tours_data = [
    ('סיור אביבי בנחל לטם', 'נחל לטם', '15/10/2024', '10:00', 'סיור בנחל לטם עם מדריך מקצועי'),
    ('טיול חורף בוואדי בן דור', 'ואדי בן דור', '10/10/2024', '09:30', 'טיול מודרך בוואדי בן דור עם נוף יפה של חיפה'),
    ('סיור סתיו בגבעת העיזים', 'וואדי עמירם', '20/10/2024', '14:00', 'סיור מודרך בוואדי עמירם עם הסברים על הצמחייה המקומית'),
    ('טיול אביבי בגן אופירה נבון', 'גן אופירה נבון', '05/11/2024', '08:30', 'טיול אביבי בגן אופירה נבון עם תצפיות מרהיבות'),
    ('סיור חורפי בשביל העץ הקסום', 'שביל העץ הקסום והחיבור לפארק הגשרים התלויים', '12/10/2024', '11:00', 'סיור חורפי בשביל העץ הקסום עם סיפורי אגדה'),
    ('טיול קיץ במערת עובדיה', 'מערת עובדיה', '15/11/2024', '13:00', 'טיול למערת עובדיה עם הדרכה על ההיסטוריה והגיאולוגיה של המקום'),
    ('סיור אביבי בפארק הגשרים התלויים', 'שביל העץ הקסום והחיבור לפארק הגשרים התלויים', '01/11/2024', '09:00', 'סיור אביבי בפארק הגשרים התלויים עם פעילויות משפחתיות'),
    ('טיול סתיו בנחל סעדיה', 'הגשר התורכי', '26/11/2024', '12:00', 'טיול סתיו בגשר התורכי עם תצפיות על בעלי חיים נדירים'),
    ('סיור חורפי בואדי עובדיה', 'שביל הטראסות', '04/12/2024', '10:30', 'סיור חורפי בשביל הטראסות עם מסלול רגלי מעניין'),
    ('טיול קיץ בנחל לטם', 'נחל לטם', '16/12/2024', '07:00', 'טיול קיץ בנחל לטם עם פעילויות מים וכיף'),
    ('סיור סתיו בגן האם', 'גן האם', '16/12/2024', '15:00', 'סיור סתיו בגן האם עם הדרכה על הצמחים המקומיים'),
    ('טיול אביבי בשביל התצפית', 'שביל התצפית', '27/12/2024', '08:00', 'טיול אביבי בשביל התצפית עם נופים מרהיבים של חיפה'),
    ('סיור חורפי בוואדי שנק', 'ואדי שנק', '28/12/2024', '11:00', 'סיור חורפי בוואדי שנק עם הסברים על הנוף והטבע'),
    ('טיול סתיו בפארק הגשרים התלויים', 'שביל העץ הקסום והחיבור לפארק הגשרים התלויים', '09/01/2025', '13:00', 'טיול סתיו בפארק הגשרים התלויים עם משחקי סביבה לילדים'),
    ('סיור אביבי בגבעת העיזים', 'שביל עמירם', '15/01/2025', '09:30', 'סיור אביבי בשביל עמירם עם הכוונה והדרכה על הצמחייה המקומית')
]

for tour in organized_tours_data:
    cur.execute("""
    INSERT INTO organized_tours (title, trail_name, date, time, description)
    VALUES (?, ?, ?, ?, ?)
    """, tour)

# Commit changes and close connection
connection.commit()
connection.close()


# Initialize registration database
connection_reg = sqlite3.connect('registration.db')
with open('schema.sql') as f:
    connection_reg.executescript(f.read())
connection_reg.close()

connection = sqlite3.connect('registration.db')
cur = connection.cursor()

news_data = [
    ('סיור לנחל לוטם יוצא ב- 15/10/2024, לפרטים ולרישום היכנסו לעמוד "סיורים מודרכים"', '2024-01-01', 1, 0),
    ('מוזמנים להאזין ל"שעה בשבוע" עם מובילת "בשבילי חיפה" ענבל חן ברגב. זמין בספוטיפיי או ביוטיוב', '2024-02-01', 1, 0)
]

for news in news_data:
    cur.execute("""
    INSERT INTO news (title,  publish_date, active, high_importance)
    VALUES (?, ?, ?, ?)
    """, news)

# Commit changes and close connection
connection.commit()
connection.close()



connection = sqlite3.connect('registration.db')
cur = connection.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    publish_date TEXT NOT NULL,
    active BOOLEAN NOT NULL,
    high_importance BOOLEAN NOT NULL
);
''')




news_data = [
    ('סיור לנחל לוטם יוצא ב- 15/10/2024, לפרטים ולרישום היכנסו לעמוד "סיורים מודרכים"', '2024-01-01', 1, 0),
    ('מוזמנים להאזין ל"שעה בשבוע" עם מובילת "בשבילי חיפה" ענבל חן ברגב. זמין בספוטיפיי או ביוטיוב', '2024-02-01', 1, 0)
]

for news in news_data:
    cur.execute("""
    INSERT INTO news (title,  publish_date, active, high_importance)
    VALUES (?, ?, ?, ?)
    """, news)

# Commit changes and close connection
connection.commit()
connection.close()




# התחברות למסד הנתונים
conn = sqlite3.connect('forum.db')
c = conn.cursor()

c.execute('''
    DROP TABLE IF EXISTS forum_topics;
''')

c.execute('''
    DROP TABLE IF EXISTS forum_comments;
''')



# יצירת טבלה עבור נושאים בפורום
c.execute('''
    CREATE TABLE IF NOT EXISTS forum_topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT NOT NULL
    )
''')

# יצירת טבלה עבור תגובות בפורום
c.execute('''
    CREATE TABLE IF NOT EXISTS forum_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT NOT NULL,
        parent_comment_id INTEGER,
        FOREIGN KEY (topic_id) REFERENCES forum_topics(id),
        FOREIGN KEY (parent_comment_id) REFERENCES forum_comments(id)
    )
''')

# הוספת נושא לדוגמה לטבלת הפורום
c.execute('''
    INSERT INTO forum_topics (title, content, created_by) 
    VALUES 
    ('סיור לנחל לוטם ב 17.04', 'נהנתי מאוד בסיור', 'משתתף אנונימי')
''')

# הוספת תגובה לדוגמה לנושא בפורום
c.execute('''
    INSERT INTO forum_comments (topic_id, content, created_by)
    VALUES 
    (1, 'הטיול היה נהדר! נוף מדהים ואוויר צח.', 'ישראל ישראלי')
''')

# שמירת השינויים וסגירת החיבור למסד הנתונים
conn.commit()
conn.close()

