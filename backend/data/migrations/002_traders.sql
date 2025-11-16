-- 交易员表
CREATE TABLE IF NOT EXISTS traders (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    strategy TEXT NOT NULL,
    symbol TEXT NOT NULL DEFAULT 'BTC/USDT',
    status TEXT NOT NULL CHECK(status IN ('stopped', 'running', 'paused')) DEFAULT 'stopped',
    config TEXT NOT NULL,  -- JSON配置
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_traders_status ON traders(status);
CREATE INDEX IF NOT EXISTS idx_traders_created_at ON traders(created_at);
