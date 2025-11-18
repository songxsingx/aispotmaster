"""交易员管理API"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from core.trader import trader_engine
import time


router = APIRouter(prefix="/api/traders", tags=["traders"])


class TraderCreate(BaseModel):
    """创建交易员请求"""
    name: str
    strategy: str = "grid"
    symbol: str = "BTC/USDT"
    config: Dict[str, Any] = {
        "amount": 0.0005,
        "grid_gap": 2.0,
        "check_interval": 60
    }


@router.post("")
async def create_trader(request: TraderCreate):
    """
    创建交易员
    
    参数:
    - name: 交易员名称
    - strategy: 策略类型（grid）
    - symbol: 交易对（BTC/USDT）
    - config: 策略配置
        - amount: 每次交易数量（默认0.0005 BTC）
        - grid_gap: 网格间隔百分比（默认2%）
        - check_interval: 检查间隔秒数（默认60秒）
    """
    # 生成交易员ID
    trader_id = f"trader_{int(time.time())}"
    
    try:
        trader = trader_engine.create_trader(
            trader_id=trader_id,
            name=request.name,
            strategy=request.strategy,
            symbol=request.symbol,
            config=request.config
        )
        
        return {
            "code": 0,
            "message": "交易员创建成功",
            "data": trader
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_traders():
    """获取所有交易员"""
    try:
        traders = trader_engine.list_traders()
        return {
            "code": 0,
            "message": "success",
            "data": traders
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trader_id}")
async def get_trader(trader_id: str):
    """获取交易员详情"""
    trader = trader_engine.get_trader(trader_id)
    
    if not trader:
        raise HTTPException(status_code=404, detail="交易员不存在")
    
    # 添加实时运行状态
    if trader_id in trader_engine.strategies:
        trader['runtime_status'] = trader_engine.strategies[trader_id].get_status()
    
    return {
        "code": 0,
        "message": "success",
        "data": trader
    }


@router.post("/{trader_id}/start")
async def start_trader(trader_id: str):
    """启动交易员"""
    success = trader_engine.start_trader(trader_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="启动失败，交易员可能已在运行或不存在")
    
    return {
        "code": 0,
        "message": "交易员已启动",
        "data": {"trader_id": trader_id, "status": "running"}
    }


@router.post("/{trader_id}/stop")
async def stop_trader(trader_id: str):
    """停止交易员"""
    success = trader_engine.stop_trader(trader_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="停止失败，交易员可能未运行")
    
    return {
        "code": 0,
        "message": "交易员已停止",
        "data": {"trader_id": trader_id, "status": "stopped"}
    }


@router.delete("/{trader_id}")
async def delete_trader(trader_id: str):
    """删除交易员"""
    success = trader_engine.delete_trader(trader_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="交易员不存在")
    
    return {
        "code": 0,
        "message": "交易员已删除",
        "data": {"trader_id": trader_id}
    }


@router.get("/{trader_id}/pnl")
async def get_trader_pnl(trader_id: str):
    """
    获取交易员盈亏数据
    
    返回:
    - realized_pnl: 已实现盈亏（已完成的买卖对）
    - unrealized_pnl: 未实现盈亏（当前持仓）
    - total_pnl: 总盈亏
    - pnl_pct: 盈亏率百分比
    - total_cost: 总成本
    - current_value: 当前价值
    """
    from core.exchange import GateIOExchange
    from config import settings
    import sqlite3
    
    # 检查交易员是否存在
    trader = trader_engine.get_trader(trader_id)
    if not trader:
        raise HTTPException(status_code=404, detail="交易员不存在")
    
    try:
        # 1. 从数据库获取所有交易记录
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT action, price, amount FROM trades WHERE trader_id = ? ORDER BY id",
            (trader_id,)
        )
        trades = cursor.fetchall()
        conn.close()
        
        if not trades:
            return {
                "code": 0,
                "data": {
                    "realized_pnl": 0.0,
                    "unrealized_pnl": 0.0,
                    "total_pnl": 0.0,
                    "pnl_pct": 0.0,
                    "total_cost": 0.0,
                    "current_value": 0.0,
                    "current_position": 0.0,
                    "current_price": 0.0
                }
            }
        
        # 2. 计算持仓和成本
        total_bought = 0.0  # 总买入数量
        total_buy_cost = 0.0  # 总买入成本
        total_sold = 0.0  # 总卖出数量
        total_sell_revenue = 0.0  # 总卖出收入
        
        for trade in trades:
            if trade[0] == 'buy':
                total_bought += trade[2]
                total_buy_cost += trade[1] * trade[2]
            elif trade[0] == 'sell':
                total_sold += trade[2]
                total_sell_revenue += trade[1] * trade[2]
        
        # 3. 当前持仓
        current_position = total_bought - total_sold
        
        # 4. 已实现盈亏（已卖出部分）
        if total_sold > 0:
            avg_buy_price = total_buy_cost / total_bought if total_bought > 0 else 0
            realized_pnl = total_sell_revenue - (avg_buy_price * total_sold)
        else:
            realized_pnl = 0.0
        
        # 5. 未实现盈亏（当前持仓）
        unrealized_pnl = 0.0
        current_price = 0.0
        current_value = 0.0
        
        if current_position > 0:
            # 获取当前市场价格
            exchange = GateIOExchange(settings.gate_api_key, settings.gate_api_secret, testnet=settings.gate_testnet)
            ticker = exchange.get_ticker(trader['symbol'])
            current_price = ticker['last']
            
            # 当前持仓的平均成本
            remaining_cost = total_buy_cost - (total_buy_cost / total_bought * total_sold) if total_bought > 0 else 0
            
            # 当前持仓的市场价值
            current_value = current_position * current_price
            
            # 未实现盈亏 = 当前价值 - 剩余成本
            unrealized_pnl = current_value - remaining_cost
        
        # 6. 总盈亏
        total_pnl = realized_pnl + unrealized_pnl
        
        # 7. 盈亏率
        pnl_pct = (total_pnl / total_buy_cost * 100) if total_buy_cost > 0 else 0.0
        
        return {
            "code": 0,
            "data": {
                "realized_pnl": round(realized_pnl, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "total_pnl": round(total_pnl, 2),
                "pnl_pct": round(pnl_pct, 2),
                "total_cost": round(total_buy_cost, 2),
                "current_value": round(current_value, 2),
                "current_position": current_position,
                "current_price": round(current_price, 2) if current_price > 0 else 0.0
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算盈亏失败: {str(e)}")
