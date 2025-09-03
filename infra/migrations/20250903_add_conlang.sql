-- migrations/20250903_add_conlang.sql
CREATE TABLE IF NOT EXISTS languages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  code TEXT NOT NULL UNIQUE,
  description TEXT DEFAULT '',
  script TEXT DEFAULT 'latin',
  phonology_json TEXT DEFAULT '{}',
  orthography_json TEXT DEFAULT '{}',
  morphology_json TEXT DEFAULT '{}',
  syntax_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS lexemes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  language_id INTEGER NOT NULL,
  lemma TEXT NOT NULL,
  pos TEXT NOT NULL,
  gloss TEXT DEFAULT '',
  ipa TEXT DEFAULT '',
  tags TEXT DEFAULT '',
  FOREIGN KEY(language_id) REFERENCES languages(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_lexemes_lang_lemma ON lexemes(language_id, lemma);

CREATE TABLE IF NOT EXISTS word_forms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lexeme_id INTEGER NOT NULL,
  form TEXT NOT NULL,
  features_json TEXT DEFAULT '{}',
  FOREIGN KEY(lexeme_id) REFERENCES lexemes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  language_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  scope TEXT NOT NULL,              -- 'phonology' | 'orthography' | 'morphology' | 'syntax'
  pattern TEXT NOT NULL,            -- regex
  replacement TEXT NOT NULL,
  environment TEXT DEFAULT '',
  priority INTEGER DEFAULT 100,     -- menor = aplica antes
  enabled INTEGER DEFAULT 1,
  FOREIGN KEY(language_id) REFERENCES languages(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_rules_lang_priority ON rules(language_id, priority);

CREATE TABLE IF NOT EXISTS lexicon_map (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  language_id INTEGER NOT NULL,
  source TEXT NOT NULL,             -- termo na língua de origem (pt/en)
  target TEXT NOT NULL,             -- termo na conlang
  notes TEXT DEFAULT '',
  FOREIGN KEY(language_id) REFERENCES languages(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_lexicon_map_lang_source ON lexicon_map(language_id, source);
