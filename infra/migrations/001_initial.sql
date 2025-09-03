CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birth_year INTEGER,
    location TEXT,
    faction TEXT
);

CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    population INTEGER,
    region TEXT
);

CREATE TABLE IF NOT EXISTS factions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS economy_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    gdp REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    year INTEGER,
    era TEXT,
    scope TEXT,
    description TEXT,
    characters TEXT,
    locations TEXT,
    tags TEXT
);

CREATE TABLE IF NOT EXISTS worlds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);
