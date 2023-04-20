-- SQLite
DROP TABLE IF EXISTS User;
CREATE TABLE User (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT
);

DROP TABLE IF EXISTS Meal;
CREATE TABLE Meal (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES User (id)
);

DROP TABLE IF EXISTS user_profile;
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    weight REAL NOT NULL,
    height REAL NOT NULL,
    activity_level TEXT NOT NULL,
    dietary_preferences TEXT,
    allergies TEXT,
    health_goal TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User (id)
);


