DROP TABLE IF EXISTS trails;

CREATE TABLE trails (
id INTEGER PRIMARY KEY AUTOINCREMENT,
main_location TEXT NOT NULL,
trail_name TEXT NOT NULL,
short_description TEXT,
start_point TEXT,
end_point TEXT,
lengthKM TEXT,
difficulty TEXT,
season TEXT,
point_of_interest TEXT,
interactive_activity TEXT,
duration TEXT,
possibility_of_entering_water BOOLEAN,
suitable_for_families BOOLEAN,
suitable_for_bicycles BOOLEAN,
circular BOOLEAN,
suitable_for_disabled BOOLEAN
);

DROP TABLE IF EXISTS participants;
CREATE TABLE participants(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    phone_number TEXT,
    number_of_participants INTEGER,
    tour TEXT,
    comments TEXT,
    FOREIGN KEY (tour) REFERENCES organized_tours(title)
);

DROP TABLE IF EXISTS messages;
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create the organized_tours table (new)
DROP TABLE IF EXISTS organized_tours;
CREATE TABLE IF NOT EXISTS organized_tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique index for each tour
    title TEXT NOT NULL,                   -- Title of the tour
    trail_name TEXT NOT NULL,                      -- Foreign key to trails table
    date TEXT NOT NULL,                    -- Date of the tour
    time TEXT NOT NULL,                    -- Time of the tour
    description TEXT,                      -- Description of the tour
    FOREIGN KEY (trail_name) REFERENCES trails(trail_name)  -- Foreign key constraint
);

DROP TABLE IF EXISTS news;
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    publish_date TEXT NOT NULL,
    active BOOLEAN NOT NULL,
    high_importance BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS forum_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS forum_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL,
    parent_comment_id INTEGER,
    FOREIGN KEY (topic_id) REFERENCES forum_topics(id),
    FOREIGN KEY (parent_comment_id) REFERENCES forum_comments(id)
);

    CREATE TABLE trail_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trail_id INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    FOREIGN KEY (trail_id) REFERENCES trails(id) ON DELETE CASCADE
);




