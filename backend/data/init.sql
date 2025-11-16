-- 交易记录表
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trader_id TEXT DEFAULT 'manual',
    strategy TEXT DEFAULT 'manual',
    symbol TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('buy', 'sell')),
    price REAL NOT NULL,
    amount REAL NOT NULL,
    cost REAL NOT NULL,
    fee_amount REAL DEFAULT 0,
    profit REAL DEFAULT 0,
    timestamp INTEGER NOT NULL,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
