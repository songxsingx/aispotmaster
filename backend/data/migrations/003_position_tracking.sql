-- Phase 3.5: 持仓追踪系统 - 数据库迁移
-- 现货交易约束：持仓不能为负

-- 1. 添加持仓追踪字段
ALTER TABLE trades ADD COLUMN position_before REAL DEFAULT 0;
ALTER TABLE trades ADD COLUMN position_after REAL DEFAULT 0;
ALTER TABLE trades ADD COLUMN is_real INTEGER DEFAULT 0;  -- 0=demo, 1=real

-- 2. 回填历史数据的持仓信息
-- 为每笔交易计算交易前后的持仓
UPDATE trades SET position_before = (
    SELECT COALESCE(SUM(
        CASE 
            WHEN t2.action = 'buy' THEN t2.amount 
            WHEN t2.action = 'sell' THEN -t2.amount 
            ELSE 0 
        END
    ), 0)
    FROM trades t2
    WHERE t2.trader_id = trades.trader_id 
    AND t2.symbol = trades.symbol
    AND t2.id < trades.id
);

UPDATE trades SET position_after = position_before + 
    CASE 
        WHEN action = 'buy' THEN amount 
        WHEN action = 'sell' THEN -amount 
        ELSE 0 
    END;

-- 3. 标记真实交易（根据order_id判断，demo订单以"demo_"开头）
-- 注意：trades表可能没有order_id字段，这里暂不执行
-- UPDATE trades SET is_real = 1 WHERE NOT EXISTS (SELECT 1);

-- 4. 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_trades_trader_symbol ON trades(trader_id, symbol);
CREATE INDEX IF NOT EXISTS idx_trades_position ON trades(position_after);

-- 验证数据完整性
-- 查询可能存在的负持仓（现货不允许）
SELECT trader_id, symbol, id, action, amount, position_after
FROM trades
WHERE position_after < 0
ORDER BY id;
