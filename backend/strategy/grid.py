"""网格交易策略"""
import time
import sqlite3
from typing import Dict, Any
from strategy.base import BaseStrategy
from core.exchange import GateIOExchange


class GridStrategy(BaseStrategy):
    """
    简单网格策略
    
    原理：
    - 价格下跌时买入
    - 价格上涨时卖出
    - 在价格波动中赚取差价
    """
    
    def __init__(self, trader_id: str, symbol: str, config: Dict[str, Any], exchange: GateIOExchange):
        """
        初始化网格策略
        
        Args:
            trader_id: 交易员ID
            symbol: 交易对，如 BTC/USDT
            config: 配置参数
                - amount: 每次交易数量（BTC）
                - grid_gap: 网格间隔（百分比，如2表示2%）
                - check_interval: 检查间隔（秒）
            exchange: 交易所实例
        """
        super().__init__(trader_id, symbol, config)
        self.exchange = exchange
        
        # 策略参数
        self.amount = float(config.get('amount', 0.0005))  # 默认0.0005 BTC
        self.grid_gap = float(config.get('grid_gap', 2.0))  # 默认2%
        self.check_interval = int(config.get('check_interval', 60))  # 默认60秒
        
        # 运行状态
        self.last_price = None
        self.last_action = None
        self.trade_count = 0
    
    def run(self):
        """运行网格策略"""
        self.running = True
        print(f"[{self.trader_id}] 网格策略启动: {self.symbol}, 网格间隔{self.grid_gap}%")
        
        while self.running:
            try:
                # 获取当前价格
                ticker = self.exchange.get_ticker(self.symbol)
                current_price = ticker['last']
                
                # 第一次运行，记录初始价格
                if self.last_price is None:
                    self.last_price = current_price
                    print(f"[{self.trader_id}] 初始价格: ${current_price:,.2f}")
                    time.sleep(self.check_interval)
                    continue
                
                # 计算价格变化百分比
                price_change_pct = ((current_price - self.last_price) / self.last_price) * 100
                
                # 价格下跌超过网格间隔 → 买入
                if price_change_pct <= -self.grid_gap and self.last_action != 'buy':
                    print(f"[{self.trader_id}] 价格下跌 {price_change_pct:.2f}% → 买入 {self.amount} BTC @ ${current_price:,.2f}")
                    try:
                        result = self.exchange.market_buy(self.symbol, self.amount)
                        self._save_trade(result)
                        self.last_price = current_price
                        self.last_action = 'buy'
                        self.trade_count += 1
                        print(f"[{self.trader_id}] ✅ 买入成功，订单ID: {result['order_id']}")
                    except Exception as e:
                        print(f"[{self.trader_id}] ❌ 买入失败: {e}")
                
                # 价格上涨超过网格间隔 → 卖出
                elif price_change_pct >= self.grid_gap and self.last_action != 'sell':
                    print(f"[{self.trader_id}] 价格上涨 {price_change_pct:.2f}% → 卖出 {self.amount} BTC @ ${current_price:,.2f}")
                    try:
                        result = self.exchange.market_sell(self.symbol, self.amount)
                        self._save_trade(result)
                        self.last_price = current_price
                        self.last_action = 'sell'
                        self.trade_count += 1
                        print(f"[{self.trader_id}] ✅ 卖出成功，订单ID: {result['order_id']}")
                    except Exception as e:
                        print(f"[{self.trader_id}] ❌ 卖出失败: {e}")
                
                else:
                    # 价格变化未达到网格间隔
                    print(f"[{self.trader_id}] 价格变化 {price_change_pct:+.2f}% (网格间隔±{self.grid_gap}%) → 等待")
                
                # 等待下一次检查
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"[{self.trader_id}] 策略运行错误: {e}")
                time.sleep(self.check_interval)
        
        print(f"[{self.trader_id}] 网格策略已停止，共执行 {self.trade_count} 笔交易")
    
    def _save_trade(self, trade_data: Dict[str, Any]):
        """
        保存交易记录到数据库
        
        Args:
            trade_data: 交易数据
        """
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO trades (trader_id, strategy, symbol, action, price, amount, cost, fee_amount, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.trader_id,
            'grid',
            trade_data['symbol'],
            trade_data['action'],
            trade_data['price'],
            trade_data['amount'],
            trade_data['cost'],
            trade_data.get('fee', 0),
            trade_data['timestamp']
        ))
        
        conn.commit()
        conn.close()
    
    def get_status(self) -> Dict[str, Any]:
        """获取策略状态"""
        status = super().get_status()
        status.update({
            'last_price': self.last_price,
            'last_action': self.last_action,
            'trade_count': self.trade_count,
            'amount': self.amount,
            'grid_gap': self.grid_gap,
            'check_interval': self.check_interval
        })
        return status
