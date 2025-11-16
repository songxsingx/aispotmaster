"""
交易API路由
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import time
from core.exchange import GateIOExchange
from config import settings

router = APIRouter(prefix="/api", tags=["trade"])

# 创建交易所实例（使用配置中的API密钥）
exchange = GateIOExchange(
    api_key=settings.gate_api_key,
    api_secret=settings.gate_api_secret,
    testnet=settings.gate_testnet
)

class TradeRequest(BaseModel):
    """交易请求"""
    symbol: str = "BTC/USDT"
    amount: float
    action: str  # buy 或 sell

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    # 读取并执行SQL脚本
    with open('data/init.sql', 'r') as f:
        cursor.executescript(f.read())
    
    conn.commit()
    conn.close()

def save_trade(trade_data: dict, trader_id: str = "manual"):
    """保存交易记录到数据库"""
    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trades (trader_id, strategy, symbol, action, price, amount, cost, fee_amount, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trader_id,
        'manual',
        trade_data['symbol'],
        trade_data['action'],
        trade_data['price'],
        trade_data['amount'],
        trade_data['cost'],
        trade_data.get('fee', 0),
        trade_data['timestamp']
    ))
    
    conn.commit()
    trade_id = cursor.lastrowid
    conn.close()
    
    return trade_id

@router.get("/config")
async def get_config():
    """获取当前配置状态"""
    return {
        "code": 0,
        "message": "success",
        "data": {
            "testnet": settings.gate_testnet,
            "has_api_key": bool(settings.gate_api_key),
            "demo_mode": not bool(settings.gate_api_key)
        }
    }

@router.post("/config")
async def update_config(
    api_key: str = "",
    api_secret: str = "",
    testnet: bool = True
):
    """
    更新API配置
    
    Args:
        api_key: Gate.io API Key
        api_secret: Gate.io API Secret
        testnet: 是否使用测试网
    """
    global exchange
    
    # 更新配置
    settings.gate_api_key = api_key
    settings.gate_api_secret = api_secret
    settings.gate_testnet = testnet
    
    # 重新创建交易所实例
    exchange = GateIOExchange(
        api_key=api_key,
        api_secret=api_secret,
        testnet=testnet
    )
    
    # 保存到.env文件
    env_content = f"""# Gate.io API配置
GATE_API_KEY={api_key}
GATE_API_SECRET={api_secret}
GATE_TESTNET={str(testnet).lower()}

# 应用配置
APP_ENV=development
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    return {
        "code": 0,
        "message": "API配置已更新",
        "data": {
            "testnet": testnet,
            "demo_mode": not bool(api_key)
        }
    }

@router.get("/balance")
async def get_balance(currency: str = "USDT"):
    """
    获取账户余额
    
    Args:
        currency: 币种，默认USDT
        
    Returns:
        余额信息
    """
    try:
        balance = exchange.get_balance(currency)
        
        # 同时获取BTC余额
        btc_balance = exchange.get_balance("BTC")
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "usdt": balance,
                "btc": btc_balance
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticker")
async def get_ticker(symbol: str = "BTC/USDT"):
    """获取行情"""
    try:
        ticker = exchange.get_ticker(symbol)
        return {
            "code": 0,
            "message": "success",
            "data": ticker
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/buy")
async def buy(symbol: str = "BTC/USDT", amount: float = 0.001):
    """
    市价买入
    
    Args:
        symbol: 交易对
        amount: 买入数量
    """
    try:
        # 执行买入
        order = exchange.market_buy(symbol, amount)
        
        # 保存到数据库
        trade_id = save_trade(order)
        order['trade_id'] = trade_id
        
        return {
            "code": 0,
            "message": "买入成功",
            "data": order
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/sell")
async def sell(symbol: str = "BTC/USDT", amount: float = 0.001):
    """
    市价卖出
    
    Args:
        symbol: 交易对
        amount: 卖出数量
    """
    try:
        # 执行卖出
        order = exchange.market_sell(symbol, amount)
        
        # 保存到数据库
        trade_id = save_trade(order)
        order['trade_id'] = trade_id
        
        return {
            "code": 0,
            "message": "卖出成功",
            "data": order
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trades(limit: int = 20):
    """获取交易历史"""
    try:
        conn = sqlite3.connect('data/database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trades 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        trades = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "code": 0,
            "message": "success",
            "data": trades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 初始化数据库
try:
    init_database()
except Exception as e:
    print(f"数据库初始化警告: {e}")
