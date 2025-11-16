"""策略基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, trader_id: str, symbol: str, config: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            trader_id: 交易员ID
            symbol: 交易对
            config: 策略配置
        """
        self.trader_id = trader_id
        self.symbol = symbol
        self.config = config
        self.running = False
    
    @abstractmethod
    def run(self):
        """
        运行策略（主循环）
        子类必须实现此方法
        """
        pass
    
    def stop(self):
        """停止策略"""
        self.running = False
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取策略状态
        
        Returns:
            状态信息字典
        """
        return {
            'trader_id': self.trader_id,
            'symbol': self.symbol,
            'running': self.running,
            'config': self.config
        }
