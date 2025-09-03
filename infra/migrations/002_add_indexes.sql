-- Add metadata columns and indexes for faster queries

-- Characters
ALTER TABLE characters ADD COLUMN project_id TEXT;
ALTER TABLE characters ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_characters_project_id ON characters(project_id);
CREATE INDEX IF NOT EXISTS idx_characters_created_at ON characters(created_at);
CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name);

-- Locations
ALTER TABLE locations ADD COLUMN project_id TEXT;
ALTER TABLE locations ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_locations_project_id ON locations(project_id);
CREATE INDEX IF NOT EXISTS idx_locations_created_at ON locations(created_at);
CREATE INDEX IF NOT EXISTS idx_locations_name ON locations(name);

-- Factions
ALTER TABLE factions ADD COLUMN project_id TEXT;
ALTER TABLE factions ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_factions_project_id ON factions(project_id);
CREATE INDEX IF NOT EXISTS idx_factions_created_at ON factions(created_at);
CREATE INDEX IF NOT EXISTS idx_factions_name ON factions(name);

-- Economy profiles
ALTER TABLE economy_profiles ADD COLUMN project_id TEXT;
ALTER TABLE economy_profiles ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_economy_profiles_project_id ON economy_profiles(project_id);
CREATE INDEX IF NOT EXISTS idx_economy_profiles_created_at ON economy_profiles(created_at);
CREATE INDEX IF NOT EXISTS idx_economy_profiles_name ON economy_profiles(name);

-- Timeline events
ALTER TABLE timeline_events ADD COLUMN project_id TEXT;
ALTER TABLE timeline_events ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_timeline_events_project_id ON timeline_events(project_id);
CREATE INDEX IF NOT EXISTS idx_timeline_events_created_at ON timeline_events(created_at);
CREATE INDEX IF NOT EXISTS idx_timeline_events_title ON timeline_events(title);

-- Worlds
ALTER TABLE worlds ADD COLUMN project_id TEXT;
ALTER TABLE worlds ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_worlds_project_id ON worlds(project_id);
CREATE INDEX IF NOT EXISTS idx_worlds_created_at ON worlds(created_at);
CREATE INDEX IF NOT EXISTS idx_worlds_name ON worlds(name);
