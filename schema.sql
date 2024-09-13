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
    id_card TEXT NOT NULL,
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


