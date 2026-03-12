-- 
-- depends: 
CREATE TABLE oneshot_stats (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    description TEXT,
    key VARCHAR(255) NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

