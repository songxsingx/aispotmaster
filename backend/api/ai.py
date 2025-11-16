"""
AI决策API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import time
from ai.client import DeepSeekClient
from ai.prompts import generate_trade_prompt
from core.exchange import GateIOExchange
from config import settings

router = APIRouter(prefix="/api/ai", tags=["ai"])

# 创建DeepSeek客户端
deepseek_client = None
if settings.deepseek_api_key:
    deepseek_client = DeepSeekClient(settings.deepseek_api_key)


class AIDecisionRequest(BaseModel):
    """AI决策请求"""
    symbol: str = "BTC/USDT"
    trader_id: Optional[str] = None


@router.post("/decide")
async def make_decision(req: AIDecisionRequest):
    """
    AI决策接口
    
    Args:
        symbol: 交易对
        trader_id: 交易员ID（可选）
        
    Returns:
        AI决策结果
    """
    if not deepseek_client:
        raise HTTPException(status_code=500, detail="DeepSeek API未配置")
    
    try:
        # 创建交易所实例
        exchange = GateIOExchange(
            api_key=settings.gate_api_key,
            api_secret=settings.gate_api_secret,
            testnet=settings.gate_testnet
        )
        
        # 获取市场数据
        ticker = exchange.get_ticker(req.symbol)
        usdt_balance = exchange.get_balance("USDT")
        btc_balance = exchange.get_balance("BTC")
        
        # 计算24h涨跌幅
        change_24h = 0.0
        if ticker.get('percentage'):
            change_24h = ticker['percentage']
        elif ticker.get('high') and ticker.get('low') and ticker.get('last'):
            change_24h = ((ticker['last'] - ticker['low']) / ticker['low']) * 100
        
        # 构造市场数据
        market_data = {
            'symbol': req.symbol,
            'price': ticker['last'],
            'change_24h': change_24h,
            'high_24h': ticker.get('high', ticker['last']),
            'low_24h': ticker.get('low', ticker['last']),
            'position': btc_balance['free'],
            'balance': usdt_balance['free']
        }
        
        # 生成提示词
        prompt = generate_trade_prompt(market_data)
        
        # 调用AI决策
        decision = deepseek_client.make_decision(prompt)
        
        # 保存决策记录到数据库
        save_decision(
            trader_id=req.trader_id or 'manual',
            symbol=req.symbol,
            action=decision['action'],
            reasoning=decision['reasoning'],
            confidence=decision['confidence'],
            market_data=market_data
        )
        
        return {
            "code": 0,
            "message": "AI决策成功",
            "data": {
                "action": decision['action'],
                "reasoning": decision['reasoning'],
                "confidence": decision['confidence'],
                "market_data": market_data
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def save_decision(trader_id: str, symbol: str, action: str, reasoning: str, confidence: float, market_data: dict):
    """
    保存AI决策记录
    
    Args:
        trader_id: 交易员ID
        symbol: 交易对
        action: 决策动作
        reasoning: 决策理由
        confidence: 置信度
        market_data: 市场数据
    """
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 创建ai_decisions表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trader_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            action TEXT NOT NULL,
            reasoning TEXT,
            confidence REAL,
            price REAL,
            timestamp INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        INSERT INTO ai_decisions (trader_id, symbol, action, reasoning, confidence, price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        trader_id,
        symbol,
        action,
        reasoning,
        confidence,
        market_data['price'],
        int(time.time() * 1000)
    ))
    
    conn.commit()
    conn.close()


@router.get("/decisions/{trader_id}")
async def get_decisions(trader_id: str, limit: int = 10):
    """
    获取AI决策历史
    
    Args:
        trader_id: 交易员ID
        limit: 返回数量限制
        
    Returns:
        决策历史列表
    """
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, symbol, action, reasoning, confidence, price, timestamp
        FROM ai_decisions
        WHERE trader_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (trader_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    decisions = []
    for row in rows:
        decisions.append({
            'id': row[0],
            'symbol': row[1],
            'action': row[2],
            'reasoning': row[3],
            'confidence': row[4],
            'price': row[5],
            'timestamp': row[6]
        })
    
    return {
        "code": 0,
        "message": "success",
        "data": decisions
    }
