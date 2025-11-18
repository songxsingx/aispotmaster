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
        
        # ✅ Phase 3.5 - P1: 通用止损止盈参数（网格默认不启用）
        self.stop_loss_pct = config.get('stop_loss_pct', None)  # 止损百分比（如-10表示-10%），None表示不启用
        self.take_profit_pct = config.get('take_profit_pct', None)  # 止盈百分比（如20表示+20%），None表示不启用
        
        # ✅ Phase 3.5 - P1: 网格区间保护（可选）
        self.grid_min = config.get('grid_min', None)  # 网格下限价格，None表示不限制
        self.grid_max = config.get('grid_max', None)  # 网格上限价格，None表示不限制
        self.max_position = config.get('max_position', None)  # 最大持仓，None表示不限制
        
        # 运行状态
        self.last_price = None
        self.last_action = None
        self.trade_count = 0
        
        # ✅ Phase 3.5: 持仓追踪（现货交易约束）
        self.current_position = self._load_position()  # 从数据库加载当前持仓
        self.avg_cost = 0  # 平均成本（未来用于盈亏计算）
    
    def _load_position(self) -> float:
        """
        从trades表计算当前持仓
        
        现货交易约束：持仓 = SUM(买入) - SUM(卖出) >= 0
        
        Returns:
            当前持仓数量（BTC）
        """
        conn = sqlite3.connect('data/database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN action='buy' THEN amount ELSE 0 END) as bought,
                SUM(CASE WHEN action='sell' THEN amount ELSE 0 END) as sold
            FROM trades 
            WHERE trader_id = ? AND symbol = ?
        ''', (self.trader_id, self.symbol))
        
        row = cursor.fetchone()
        conn.close()
        
        bought = row[0] or 0
        sold = row[1] or 0
        position = bought - sold
        
        print(f"[{self.trader_id}] 加载持仓: 买入{bought:.6f} - 卖出{sold:.6f} = {position:.6f} BTC")
        
        return position
    
    def run(self):
        """运行网格策略"""
        self.running = True
        print(f"[{self.trader_id}] 网格策略启动: {self.symbol}, 网格间隔{self.grid_gap}%")
        
        while self.running:
            try:
                # ✅ Phase 3.5 - P2: 更新心跳
                self._update_heartbeat()
                
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
                
                # ✅ Phase 3.5 - P1: 检查止损止盈（通用框架）
                should_stop, stop_reason = self._check_stop_conditions(current_price)
                if should_stop:
                    print(f"[{self.trader_id}] ❗ {stop_reason}")
                    self.running = False
                    break
                
                # ✅ Phase 3.5 - P1: 网格区间保护
                if not self._is_price_in_grid_range(current_price):
                    print(f"[{self.trader_id}] ⚠️ 价格 ${current_price:,.2f} 超出网格区间，暂停交易")
                    time.sleep(self.check_interval)
                    continue
                
                # 价格下跌超过网格间隔 → 买入
                if price_change_pct <= -self.grid_gap and self.last_action != 'buy':
                    # ✅ Phase 3.5 - P1: 检查最大持仓限制
                    if self.max_position and self.current_position >= self.max_position:
                        print(f"[{self.trader_id}] ⚠️ 已达最大持仓({self.max_position} BTC)，跳过买入")
                    else:
                        # ✅ Phase 3.5: 买入前检查余额
                        balance = self.exchange.get_balance()
                        usdt_free = balance.get('USDT', {}).get('free', 0)
                        cost = self.amount * current_price
                        
                        if usdt_free < cost:
                            print(f"[{self.trader_id}] ⚠️ 余额不足({usdt_free:.2f} USDT < {cost:.2f} USDT)，跳过买入")
                        else:
                            print(f"[{self.trader_id}] 价格下跌 {price_change_pct:.2f}% → 买入 {self.amount} BTC @ ${current_price:,.2f}")
                            try:
                                result = self.exchange.market_buy(self.symbol, self.amount)
                                self._save_trade(result)
                                self.current_position += self.amount  # ✅ 更新持仓
                                self.last_price = current_price
                                self.last_action = 'buy'
                                self.trade_count += 1
                                print(f"[{self.trader_id}] ✅ 买入成功，当前持仓: {self.current_position:.6f} BTC")
                            except Exception as e:
                                print(f"[{self.trader_id}] ❌ 买入失败: {e}")
                
                # 价格上涨超过网格间隔 → 卖出
                elif price_change_pct >= self.grid_gap and self.last_action != 'sell':
                    # ✅ Phase 3.5: 卖出前检查持仓（现货不能卖空）
                    if self.current_position < self.amount:
                        print(f"[{self.trader_id}] ⚠️ 持仓不足({self.current_position:.6f} BTC < {self.amount} BTC)，跳过卖出")
                    else:
                        print(f"[{self.trader_id}] 价格上涨 {price_change_pct:.2f}% → 卖出 {self.amount} BTC @ ${current_price:,.2f}")
                        try:
                            result = self.exchange.market_sell(self.symbol, self.amount)
                            self._save_trade(result)
                            self.current_position -= self.amount  # ✅ 更新持仓
                            self.last_price = current_price
                            self.last_action = 'sell'
                            self.trade_count += 1
                            print(f"[{self.trader_id}] ✅ 卖出成功，当前持仓: {self.current_position:.6f} BTC")
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
        
        # ✅ Phase 3.5: 计算持仓变化
        position_before = self.current_position
        if trade_data['action'] == 'buy':
            position_after = self.current_position + trade_data['amount']
        else:  # sell
            position_after = self.current_position - trade_data['amount']
        
        cursor.execute('''
            INSERT INTO trades (trader_id, strategy, symbol, action, price, amount, cost, fee_amount, timestamp, position_before, position_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.trader_id,
            'grid',
            trade_data['symbol'],
            trade_data['action'],
            trade_data['price'],
            trade_data['amount'],
            trade_data['cost'],
            trade_data.get('fee', 0),
            trade_data['timestamp'],
            position_before,
            position_after
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
            'check_interval': self.check_interval,
            'current_position': self.current_position  # ✅ Phase 3.5: 返回持仓信息
        })
        return status
    
    def _check_stop_conditions(self, current_price: float) -> tuple[bool, str]:
        """
        ✅ Phase 3.5 - P1: 检查止损止盈条件（通用框架）
        
        Args:
            current_price: 当前价格
            
        Returns:
            (should_stop, reason): 是否应该停止, 原因
        """
        # 如果没有持仓，不需要检查止损止盈
        if self.current_position == 0:
            return False, ""
        
        # 如果没有启用止损止盈，跳过检查
        if self.stop_loss_pct is None and self.take_profit_pct is None:
            return False, ""
        
        try:
            # 调用盈亏计算API（复用逻辑）
            import sqlite3
            
            conn = sqlite3.connect('data/database.db')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT action, price, amount FROM trades WHERE trader_id = ? ORDER BY id",
                (self.trader_id,)
            )
            trades = cursor.fetchall()
            conn.close()
            
            if not trades:
                return False, ""
            
            # 计算总成本
            total_buy_cost = 0.0
            total_bought = 0.0
            total_sold = 0.0
            total_sell_revenue = 0.0
            
            for trade in trades:
                if trade[0] == 'buy':
                    total_bought += trade[2]
                    total_buy_cost += trade[1] * trade[2]
                elif trade[0] == 'sell':
                    total_sold += trade[2]
                    total_sell_revenue += trade[1] * trade[2]
            
            if total_buy_cost == 0:
                return False, ""
            
            # 计算已实现盈亏
            if total_sold > 0:
                avg_buy_price = total_buy_cost / total_bought
                realized_pnl = total_sell_revenue - (avg_buy_price * total_sold)
            else:
                realized_pnl = 0.0
            
            # 计算未实现盈亏
            if self.current_position > 0:
                remaining_cost = total_buy_cost - (total_buy_cost / total_bought * total_sold)
                current_value = self.current_position * current_price
                unrealized_pnl = current_value - remaining_cost
            else:
                unrealized_pnl = 0.0
            
            # 总盈亏和盈亏率
            total_pnl = realized_pnl + unrealized_pnl
            pnl_pct = (total_pnl / total_buy_cost * 100)
            
            # 检查止损
            if self.stop_loss_pct is not None and pnl_pct <= self.stop_loss_pct:
                # 触发止损：卖出全部持仓
                if self.current_position > 0:
                    try:
                        print(f"[{self.trader_id}] ❌ 触发止损 ({pnl_pct:.2f}% <= {self.stop_loss_pct}%) → 卖出全部持仓 {self.current_position} BTC")
                        result = self.exchange.market_sell(self.symbol, self.current_position)
                        self._save_trade(result)
                        self.current_position = 0
                    except Exception as e:
                        print(f"[{self.trader_id}] ❌ 止损卖出失败: {e}")
                
                return True, f"止损触发: 盈亏率 {pnl_pct:.2f}% <= {self.stop_loss_pct}%，策略停止"
            
            # 检查止盈
            if self.take_profit_pct is not None and pnl_pct >= self.take_profit_pct:
                # 触发止盈：卖出全部持仓
                if self.current_position > 0:
                    try:
                        print(f"[{self.trader_id}] ✅ 触发止盈 ({pnl_pct:.2f}% >= {self.take_profit_pct}%) → 卖出全部持仓 {self.current_position} BTC")
                        result = self.exchange.market_sell(self.symbol, self.current_position)
                        self._save_trade(result)
                        self.current_position = 0
                    except Exception as e:
                        print(f"[{self.trader_id}] ❌ 止盈卖出失败: {e}")
                
                return True, f"止盈触发: 盈亏率 {pnl_pct:.2f}% >= {self.take_profit_pct}%，策略停止"
            
            return False, ""
        
        except Exception as e:
            print(f"[{self.trader_id}] ⚠️ 检查止损止盈失败: {e}")
            return False, ""
    
    def _is_price_in_grid_range(self, price: float) -> bool:
        """
        ✅ Phase 3.5 - P1: 检查价格是否在网格区间内
        
        Args:
            price: 当前价格
            
        Returns:
            bool: True表示在区间内，False表示超出区间
        """
        # 如果没有设置区间，默认在区间内
        if self.grid_min is None and self.grid_max is None:
            return True
        
        # 检查下限
        if self.grid_min is not None and price < self.grid_min:
            return False
        
        # 检查上限
        if self.grid_max is not None and price > self.grid_max:
            return False
        
        return True
    
    def _update_heartbeat(self):
        """✅ Phase 3.5 - P2: 更新心跳"""
        try:
            # 通知trader_engine更新心跳
            from core.trader import trader_engine
            trader_engine.update_heartbeat(self.trader_id)
        except:
            pass  # 静默失败，不影响策略运行
