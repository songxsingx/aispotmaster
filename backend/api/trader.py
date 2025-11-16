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
