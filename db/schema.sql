CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  discord_id TEXT UNIQUE,
  notion_id TEXT,
  line_id TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS channels (
  user_id TEXT PRIMARY KEY,
  category_id TEXT,
  text_channel_id TEXT,
  forum_channel_id TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS threads (
  thread_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  model TEXT DEFAULT 'gemini-flash',
  read_ok INTEGER DEFAULT 1,
  write_ok INTEGER DEFAULT 0,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
